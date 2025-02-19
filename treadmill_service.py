import asyncio
import threading
from bleak import BleakClient, BleakError
from logger_config import logger

class TreadmillService:
    """Fetches treadmill speed and incline from BLE FTMS service."""

    def __init__(self, ble_address, callback=None, disconnect_callback=None, connection_event=None):
        self.ble_address = ble_address
        self.ftms_uuid = "00002acd-0000-1000-8000-00805f9b34fb"  # FTMS UUID
        self.callback = callback
        self.disconnect_callback = disconnect_callback
        self.connection_event = connection_event  # Used to notify service_manager when connected
        self.client = None

    async def connect_and_listen(self):
        """Continuously tries to connect to BLE treadmill and listens for updates."""
        while True:
            try:
                logger.info(f"🔄 Attempting to connect to FTMS Treadmill: {self.ble_address}")

                async with BleakClient(self.ble_address, disconnected_callback=self.on_disconnect) as client:
                    self.client = client
                    logger.info(f"✅ Connected to FTMS Treadmill: {self.ble_address}")

                    if self.connection_event:
                        self.connection_event.set()  # Notify service_manager that connection is established

                    # Subscribe to FTMS notifications
                    await client.start_notify(self.ftms_uuid, self.notification_handler)

                    while True:
                        await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ BLE FTMS connection error: {e}. Retrying in 10 sec...")
                if self.connection_event:
                    self.connection_event.clear()  # Indicate connection failure
                await asyncio.sleep(10)  # Retry after delay

    def on_disconnect(self, client):
        """Handles BLE disconnection."""
        logger.warning(f"⚠️ FTMS Treadmill Disconnected! Reconnecting...")
        if self.disconnect_callback:
            self.disconnect_callback()

    def notification_handler(self, sender, data):
        """Handles incoming FTMS treadmill data."""
        try:
            speed = data[2] / 100.0  # Convert to m/s
            incline = data[4] / 10.0  # Convert to % grade

            if self.callback:
                self.callback(speed, incline)

        except Exception as e:
            logger.error(f"❌ Error processing FTMS data: {e}")

    def start(self):
        """Starts the BLE FTMS listener in a separate asyncio task."""
        asyncio.create_task(self.connect_and_listen())

def run_treadmill_service(ble_address, callback, disconnect_callback, connection_event):
    """Starts the FTMS treadmill BLE service in a separate thread."""
    treadmill_service = TreadmillService(ble_address, callback, disconnect_callback, connection_event)
    thread = threading.Thread(target=asyncio.run, args=(treadmill_service.connect_and_listen(),), daemon=True)
    thread.start()
