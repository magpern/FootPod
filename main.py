import time
from service_manager import start_services, stop_services
from ant_broadcaster import node
from logger_config import logger
from strava_uploader import upload_photo, upload_to_strava

# BLE Sensor Addresses
BLE_HRM_SENSOR_ADDRESS = "DC:1D:77:84:61:B9"
BLE_TREADMILL_SENSOR_ADDRESS = "FA:E4:E3:04:27:CE"

# Start BLE Services & FIT File Logging
start_services(BLE_HRM_SENSOR_ADDRESS, BLE_TREADMILL_SENSOR_ADDRESS)

try:
    logger.info("🎬 System Initialized - Running ANT+ Broadcast")
    node.start()
except KeyboardInterrupt:
    logger.warning("🛑 Shutting down...")
    stop_services()  # Stop BLE services & save FIT file
    node.stop()

    # Ask if the user wants to upload the workout to Strava
    while True:
        upload = input("📤 Do you want to upload the workout to Strava? (yes/no): ").strip().lower()
        if upload == "yes":
            activity_id = upload_to_strava("treadmill_workout.fit")

            # Ask if user wants to upload the workout summary image
            if activity_id:
                image_upload = input("📸 Upload workout summary image? (yes/no): ").strip().lower()
                if image_upload == "yes":
                    upload_photo(activity_id, "workout_summary.png")

            break
        elif upload == "no":
            logger.info("✅ FIT file saved locally. Strava upload skipped.")
            break
        else:
            print("❓ Please enter 'yes' or 'no'.")
