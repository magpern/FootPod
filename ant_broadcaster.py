from openant.easy.node import Node
from openant.easy.channel import Channel
from logger_config import logger
from data_processor import compute_metrics
from service_manager import sensor_data  # Import shared sensor data
from config import ANT_NETWORK_KEY, FOOTPOD_DEVICE_ID, FOOTPOD_DEVICE_TYPE, FOOTPOD_TRANSMISSION_TYPE, FOOTPOD_RF_FREQUENCY, FOOTPOD_PERIOD
from config import MANUFACTURER_ID, SOFTWARE_VERSION, SERIAL_NUMBER

# Create ANT+ node and channel
node = Node()
footpod_channel = node.new_channel(Channel.Type.BIDIRECTIONAL_TRANSMIT)
node.set_network_key(0, ANT_NETWORK_KEY)

# Configure FootPod ANT+ Channel
footpod_channel.set_rf_freq(FOOTPOD_RF_FREQUENCY)
footpod_channel.set_period(FOOTPOD_PERIOD)
footpod_channel.set_id(FOOTPOD_DEVICE_ID, FOOTPOD_DEVICE_TYPE, FOOTPOD_TRANSMISSION_TYPE)
footpod_channel.open()

logger.info("✅ ANT+ Foot Pod Broadcasting Started")

# Manufacturer info
MANUFACTURER_ID = 130  # Example ID
SOFTWARE_VERSION = 2
SERIAL_NUMBER = 12345678

def send_device_info():
    """Sends Device Info Pages 80 & 81 for Garmin identification."""
    
    manufacturer_packet = [
        80, MANUFACTURER_ID & 0xFF, (MANUFACTURER_ID >> 8) & 0xFF, 1, 1, 1, 1, 1
    ]
    product_packet = [
        81, 0xFF, SOFTWARE_VERSION, SOFTWARE_VERSION, 
        SERIAL_NUMBER & 0xFF, (SERIAL_NUMBER >> 8) & 0xFF,
        (SERIAL_NUMBER >> 16) & 0xFF, (SERIAL_NUMBER >> 24) & 0xFF
    ]
    
    logger.info(f"📡 Sending Device Info (Page 80) - Manufacturer ID: {MANUFACTURER_ID}")
    logger.info(f"📡 Sending Device Info (Page 81) - Software Version: {SOFTWARE_VERSION}, Serial Number: {SERIAL_NUMBER}")

    footpod_channel.send_broadcast_data(manufacturer_packet)
    footpod_channel.send_broadcast_data(product_packet)
    
    logger.info("✅ Device info packets sent successfully.")

# Track messages to ensure periodic device info broadcast
message_count = 0

def on_event_tx(data):
    """Handles ANT+ data transmission events on a proper schedule."""
    global message_count

    if not sensor_data:  # Ensure we have valid sensor data
        return

    updated_data = compute_metrics(sensor_data)  # Compute updated values
    sensor_data.update(updated_data)  # Update shared state

    # Extract required values
    speed_mps = sensor_data["speed"]
    cadence_spm = sensor_data["cadence"]
    distance_m = sensor_data["distance"]
    stride_count = sensor_data["stride_count"]
    heart_rate = sensor_data["heart_rate"]

    # Send device info every 65 messages (~16 seconds at 4Hz)
    if message_count % 65 == 0:
        send_device_info()

    # Send Page 1 (Speed & Distance) every 3rd message
    if message_count % 3 == 0:
        page_1_payload = [
            1, 0xFF, 0xFF, int(distance_m) & 0xFF, (int(distance_m) & 0x0F) << 4 | (int(speed_mps) & 0x0F),
            int((speed_mps - int(speed_mps)) * 256), int(stride_count) & 0xFF, 0x20
        ]
        footpod_channel.send_broadcast_data(page_1_payload)
        logger.info(f"📡 ANT+ Page 1 -> Distance: {distance_m:.2f}m, Speed: {speed_mps:.2f}m/s, Strides: {stride_count}")

    # Send Page 2 (Cadence & Stride) in between Page 1 broadcasts
    else:
        page_2_payload = [
            2, 0xFF, 0xFF, int(cadence_spm // 2),  # Convert Steps Per Minute (SPM) to Strides Per Minute
            ((int(cadence_spm // 2) % 16) << 4) | (int(speed_mps) & 0x0F),
            int((speed_mps - int(speed_mps)) * 256), int(heart_rate), 0x20
        ]
        footpod_channel.send_broadcast_data(page_2_payload)
        logger.info(f"📡 ANT+ Page 2 -> Cadence: {cadence_spm // 2} SPM (Converted from {cadence_spm} Steps), Speed: {speed_mps:.2f}m/s, HR: {heart_rate} BPM")

    message_count += 1  # Increment message count

footpod_channel.on_broadcast_tx_data = on_event_tx
