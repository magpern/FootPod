# Set logging level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"

# 🔹 BLE Device Addresses
BLE_HRM_SENSOR_ADDRESS = "DC:1D:77:84:61:B9"  # Garmin HRM BLE Address
BLE_TREADMILL_SENSOR_ADDRESS = "FA:E4:E3:04:27:CE"  # FTMS Treadmill BLE Address

# 🔹 ANT+ Network Configuration
ANT_NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]

# 🔹 FootPod Broadcast Configuration
FOOTPOD_DEVICE_ID = 1001  # Unique ANT+ Device ID
FOOTPOD_DEVICE_TYPE = 124  # Foot Pod Device Type
FOOTPOD_TRANSMISSION_TYPE = 5  # Transmission Type
FOOTPOD_RF_FREQUENCY = 57  # RF Frequency for Foot Pod
FOOTPOD_PERIOD = 8134  # Broadcast period (4Hz = every 250ms)

# 🔹 FIT File Settings
FIT_FILE_NAME = "treadmill_workout.fit"

# 🔹 Manufacturer Info (For ANT+ Device Pages 80 & 81)
MANUFACTURER_ID = 130  # Example Manufacturer ID
SOFTWARE_VERSION = 2
SERIAL_NUMBER = 12345678
