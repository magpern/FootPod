import asyncio
import pytest
from unittest.mock import MagicMock
from heartrate_service import GarminHRMService

@pytest.mark.asyncio
async def test_hrm_parsing_heart_rate():
    """Test parsing of HRM data for heart rate."""
    hr_callback_mock = MagicMock()
    cadence_callback_mock = MagicMock()
    service = GarminHRMService(hr_callback=hr_callback_mock, cadence_callback=cadence_callback_mock)

    # Simulated HRM heart rate message (first byte contains flags)
    heart_rate = 120  # Mocked HR in BPM
    data = bytes([0b00000000, heart_rate])  # Flags + HR Value

    service.hr_handler(0, data)

    hr_callback_mock.assert_called_once_with(heart_rate)
    cadence_callback_mock.assert_not_called()

@pytest.mark.asyncio
async def test_hrm_parsing_cadence():
    """Test parsing of HRM data for cadence."""
    hr_callback_mock = MagicMock()
    cadence_callback_mock = MagicMock()
    service = GarminHRMService(hr_callback=hr_callback_mock, cadence_callback=cadence_callback_mock)

    # Simulated RSC (Running Speed & Cadence) message
    cadence_value = 75  # Mocked cadence in SPM
    data = bytes([0b00000000, 0xFF, 0xFF, cadence_value])  # Flags + unknown bytes + cadence

    service.cadence_handler(0, data)

    cadence_callback_mock.assert_called_once_with(cadence_value)
    hr_callback_mock.assert_not_called()

@pytest.mark.asyncio
async def test_mock_hrm_data():
    """Test HRM mock data generation."""
    hr_callback_mock = MagicMock()
    cadence_callback_mock = MagicMock()
    service = GarminHRMService(hr_callback=hr_callback_mock, cadence_callback=cadence_callback_mock)

    # Run the mock HRM data generator for 2 seconds
    mock_task = asyncio.create_task(service.mock_hrm_data())
    await asyncio.sleep(2)
    mock_task.cancel()

    assert hr_callback_mock.call_count > 0
    assert cadence_callback_mock.call_count > 0

    hr_callback_mock.assert_called_with(pytest.approx(117, abs=10))
    cadence_callback_mock.assert_called_with(pytest.approx(75, abs=10))  # Mock cadence is fixed at 75 SPM

@pytest.mark.asyncio
async def test_hrm_reconnection():
    """Test HRM service reconnection handling."""
    disconnect_mock = MagicMock()
    service = GarminHRMService(disconnect_callback=disconnect_mock)

    service.on_disconnect(None)

    disconnect_mock.assert_called_once()
