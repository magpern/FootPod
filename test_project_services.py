import pytest
import asyncio
from unittest.mock import MagicMock, patch
from service_manager import start_services, stop_services, update_hrm_data, update_stride_cadence, update_treadmill_data
from data_processor import compute_metrics
from workout_image_generator import generate_workout_image

@pytest.mark.asyncio
async def test_service_startup():
    """Test that BLE services start correctly."""
    with patch("service_manager.run_garmin_hrm_service"), patch("service_manager.run_treadmill_service"):
        start_services()

@pytest.mark.asyncio
async def test_service_disconnection_recovery():
    """Test BLE disconnection recovery."""
    with patch("service_manager.run_garmin_hrm_service"), patch("service_manager.run_treadmill_service"):
        stop_services()
        start_services()


@pytest.mark.asyncio
async def test_compute_metrics():
    """Test metric computation for speed, cadence, and incline."""
    sensor_data = {"speed": 2.5, "cadence": 85, "incline": 1.5, "heart_rate": 120}
    result = compute_metrics(sensor_data)
    assert "distance" in result
    assert "stride_count" in result
    assert "elevation_gain" in result

@pytest.mark.asyncio
async def test_generate_workout_image():
    """Test workout summary image generation."""
    workout_summary = {"distance": 5000, "duration": 1800, "avg_heart_rate": 145, "avg_cadence": 85, "avg_incline": 2.5, "total_elevation": 50}
    with patch("matplotlib.pyplot.savefig") as mock_save:
        generate_workout_image(workout_summary)
        mock_save.assert_called
