import time
import logging
from logger_config import logger

# Internal state
distance_m = 0
stride_count = 0
last_time = time.time()

def compute_metrics(sensor_data):
    """Computes distance, elevation gain, and formats ANT+ messages."""
    global distance_m, stride_count, last_time

    elapsed_time = time.time() - last_time
    last_time = time.time()

    # Ensure values are valid
    speed_mps = sensor_data.get("speed", 0.0)  # Default to 0 if missing
    cadence_spm = sensor_data.get("cadence", 0)  # Default to 0
    incline_pct = sensor_data.get("incline", 0.0)  # Default to 0
    heart_rate = sensor_data.get("heart_rate", 0)  # Default to 0

    # Update distance
    distance_m += speed_mps * elapsed_time

    # Simulated stride count
    stride_count += (cadence_spm / 60) * elapsed_time if cadence_spm else 0

    # Compute elevation gain (ensure no division errors)
    elevation_gain = (speed_mps * elapsed_time * incline_pct) / 100 if incline_pct else 0

    # Log only if debug is enabled
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Computed Metrics -> Distance: {distance_m:.2f} m, "
                     f"Strides: {stride_count:.1f}, "
                     f"Elevation Gain: {elevation_gain:.2f} m")

    return {
        "distance": distance_m,
        "stride_count": stride_count,
        "elevation_gain": elevation_gain,
        "heart_rate": heart_rate,
        "speed": speed_mps,
        "cadence": cadence_spm,
        "incline": incline_pct
    }
