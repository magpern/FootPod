import threading
import time
from heartrate_service import run_garmin_hrm_service
from treadmill_service import run_treadmill_service
from fit_generator import FitFileGenerator
from logger_config import logger
from config import BLE_HRM_SENSOR_ADDRESS, BLE_TREADMILL_SENSOR_ADDRESS

# Global stop event
stop_event = threading.Event()

# Connection events to wait for BLE connection
hrm_connection_event = threading.Event()
ftms_connection_event = threading.Event()

# Sensor data storage (defaulting to zero values)
sensor_data = {
    "heart_rate": 0,
    "cadence": 0,
    "speed": 0.0,
    "incline": 0.0
}

# Initialize FIT file generator
fit_generator = FitFileGenerator()

def update_hrm_data(heart_rate):
    """Updates heart rate data and logs it in the FIT file."""
    if stop_event.is_set():
        return
    sensor_data["heart_rate"] = heart_rate
    logger.debug(f"Heart Rate Updated: {heart_rate} BPM")
    fit_generator.add_record(sensor_data)

def update_stride_cadence(cadence):
    """Updates cadence from Garmin HRM service and logs it in the FIT file."""
    if stop_event.is_set():
        return
    sensor_data["cadence"] = cadence
    logger.debug(f"Stride Cadence Updated: {cadence} SPM")
    fit_generator.add_record(sensor_data)

def update_treadmill_data(speed, incline):
    """Updates treadmill speed and incline and logs it in the FIT file."""
    if stop_event.is_set():
        return
    sensor_data["speed"], sensor_data["incline"] = speed, incline
    logger.debug(f"Treadmill Updated: Speed={speed:.2f} m/s, Incline={incline:.1f}%")
    fit_generator.add_record(sensor_data)

# **Handle BLE Disconnections**
def on_hrm_disconnected():
    """Handles HRM disconnection by resetting connection state and triggering reconnection."""
    logger.warning("⚠️ HRM Disconnected! Restarting service...")
    hrm_connection_event.clear()  # Reset connection event
    threading.Thread(target=run_garmin_hrm_service, args=(hrm_address, update_hrm_data, update_stride_cadence, on_hrm_disconnected, hrm_connection_event), daemon=True).start()

def on_ftms_disconnected():
    """Handles FTMS disconnection by resetting connection state and triggering reconnection."""
    logger.warning("⚠️ FTMS Disconnected! Restarting service...")
    ftms_connection_event.clear()  # Reset connection event
    threading.Thread(target=run_treadmill_service, args=(treadmill_address, update_treadmill_data, on_ftms_disconnected, ftms_connection_event), daemon=True).start()

def start_services():
    """Starts BLE services using addresses from config.py."""
    logger.info("🚀 Starting BLE services and FIT file recording...")

    # Start HRM service
    threading.Thread(
        target=run_garmin_hrm_service, 
        args=(BLE_HRM_SENSOR_ADDRESS, update_hrm_data, update_stride_cadence, on_hrm_disconnected, hrm_connection_event), 
        daemon=True
    ).start()

    # Start FTMS service
    threading.Thread(
        target=run_treadmill_service, 
        args=(BLE_TREADMILL_SENSOR_ADDRESS, update_treadmill_data, on_ftms_disconnected, ftms_connection_event), 
        daemon=True
    ).start()

    # Wait for HRM connection
    if not hrm_connection_event.wait(timeout=30):
        logger.warning("⚠️ HRM failed to connect within 30 seconds. Continuing...")

    # Wait for FTMS connection
    if not ftms_connection_event.wait(timeout=30):
        logger.warning("⚠️ FTMS failed to connect within 30 seconds. Continuing...")


def stop_services():
    """Stops BLE services and finalizes the FIT file."""
    logger.info("🛑 Stopping services and finalizing FIT file...")
    
    stop_event.set()  # Signal all threads to stop
    time.sleep(2)  # Allow some time for threads to exit
    fit_generator.end_workout()
    logger.info("✅ Services stopped successfully.")
