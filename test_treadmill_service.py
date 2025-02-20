import asyncio
import pytest
from unittest.mock import MagicMock
from treadmill_service import TreadmillService

@pytest.mark.asyncio
async def test_ftms_parsing_speed():
    """Test parsing of FTMS data for speed."""
    callback_mock = MagicMock()
    service = TreadmillService(callback=callback_mock)

    # Simulated FTMS speed message (flags indicate speed is present)
    flags = 0b00000001  # Bit 0: Instantaneous Speed
    speed_value = int(5.0 * 3.6 * 100)  # 5.0 m/s converted to 1/100 km/h
    data = flags.to_bytes(2, byteorder="little") + speed_value.to_bytes(2, byteorder="little")

    service.notification_handler(0, data)

    # Ensure the callback matches the correct number of parameters
    callback_mock.assert_called_once_with(5.0, 0.0, 0.0, 0, 0, 0, 0.0, 0, 0)

@pytest.mark.asyncio
async def test_ftms_parsing_incline():
    """Test parsing of FTMS data for incline."""
    callback_mock = MagicMock()
    service = TreadmillService(callback=callback_mock)

    # Simulated FTMS incline message (bit 3: Incline present)
    flags = 0b00001000  # Only Incline is set
    incline_value = int(1.5 * 10)  # 1.5% incline in 1/10 %

    # Correctly construct the FTMS packet (2 bytes flags + 2 bytes incline)
    data = flags.to_bytes(2, byteorder="little") + incline_value.to_bytes(2, byteorder="little", signed=True)

    service.notification_handler(0, data)

    # ✅ Check that the mock was called with correct values
    callback_mock.assert_called_once_with(
        0.0, 1.5, 0.0, 0, 0, 0, 0.0, 0, 0  # Expecting 9 values
    )

@pytest.mark.asyncio
async def test_ftms_parsing_full_packet():
    """Test parsing of FTMS data with all fields."""
    callback_mock = MagicMock()
    service = TreadmillService(callback=callback_mock)

    flags = 0b1111111111  # All fields present (corrected flag size)
    speed_value = int(4.0 * 3.6 * 100)  # 4.0 m/s converted to 1/100 km/h
    avg_speed_value = int(3.5 * 3.6 * 100)  # 3.5 m/s avg
    distance_value = int(2500)  # 2500 cm (25 meters)
    incline_value = int(2.0 * 10)  # 2.0% incline
    ramp_angle_value = int(0.5 * 10)  # 0.5° incline
    energy_value = int(150)  # 150 kcal
    energy_per_hour_value = int(600)  # 600 kcal/h
    energy_per_minute_value = 10  # 10 kcal/min
    heart_rate_value = 110  # 110 BPM
    elapsed_time_value = int(300)  # 300 seconds

    data = (
        flags.to_bytes(2, byteorder="little")
        + speed_value.to_bytes(2, byteorder="little")
        + avg_speed_value.to_bytes(2, byteorder="little")
        + distance_value.to_bytes(3, byteorder="little")
        + incline_value.to_bytes(2, byteorder="little", signed=True)
        + ramp_angle_value.to_bytes(2, byteorder="little", signed=True)
        + energy_value.to_bytes(2, byteorder="little")
        + energy_per_hour_value.to_bytes(2, byteorder="little")
        + bytes([energy_per_minute_value])
        + bytes([heart_rate_value])
        + elapsed_time_value.to_bytes(2, byteorder="little")
    )

    service.notification_handler(0, data)

    # Corrected assertion to match full expected parameters
    callback_mock.assert_called_once_with(
        4.0, 2.0, 25.0, 150, 300, 110, 0.5, 600, 10
    )

@pytest.mark.asyncio
async def test_mock_ftms_data():
    """Test FTMS mock treadmill data."""
    callback_mock = MagicMock()
    service = TreadmillService(callback=callback_mock)

    mock_task = asyncio.create_task(service.mock_ftms_data())
    await asyncio.sleep(2)
    mock_task.cancel()

    assert callback_mock.call_count > 0

    # Mock should return stable, consistent values (no need for approx)
    callback_mock.assert_called_with(
        pytest.approx(0.8333, rel=0.1),  # ✅ Allow precision tolerance
        pytest.approx(1.0, rel=0.1),
        pytest.approx(1.66, rel=0.1),
        pytest.approx(0.2, rel=0.1),
        2, 100,  # Integers, no need for approx
        pytest.approx(0.5, rel=0.1),
        600, 10
    )

