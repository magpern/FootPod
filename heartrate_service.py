import asyncio
import threading
from bleak import BleakClient, BleakError
from logger_config import logger

class GarminHRMService:
    """Handles both heart rate and cadence from a single BLE HRM device."""

    HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Heart Rate Measurement UUID
    RSC_UUID = "00002a53-0000-1000-8000-00805f9b34fb"  # Running Speed & Cadence UUID

    def __init__(self, ble_address, hr_callback=None, cadence_callback=None, disconnect_callback=None, connection_event=None):
        self.ble_address = ble_address
        self.hr_callback = hr_callback
        self.cadence_callback = cadence_callback
        self.disconnect_callback = disconnect_callback
        self.connection_event = connection_event  # Used to signal when connected
        self.client = None

    async def connect_and_listen(self):
        """Continuously tries to connect to BLE HRM and listens for updates."""
        while True:
            try:
                logger.info(f"🔄 Attempting to connect to Garmin HRM: {self.ble_address}")

                async with BleakClient(self.ble_address, disconnected_callback=self.on_disconnect) as client:
                    self.client = client
                    logger.info(f"✅ Connected to Garmin HRM: {self.ble_address}")

                    if self.connection_event:
                        self.connection_event.set()  # Notify service_manager that connection is established

                    # Subscribe to HR notifications
                    await client.start_notify(self.HR_UUID, self.hr_handler)
                    await client.start_notify(self.RSC_UUID, self.cadence_handler)

                    while True:
                        await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ BLE HRM connection error: {e}. Retrying in 10 sec...")
                if self.connection_event:
                    self.connection_event.clear()  # Indicate connection failure
                await asyncio.sleep(10)

    def on_disconnect(self, client):
        """Handles BLE disconnection."""
        logger.warning(f"⚠️ Garmin HRM Disconnected! Reconnecting...")
        if self.disconnect_callback:
            self.disconnect_callback()

    def hr_handler(self, sender, data):
        """Handles heart rate data."""
        try:
            heart_rate = data[1]  # Extract HR from BLE packet
            if self.hr_callback:
                self.hr_callback(heart_rate)
        except Exception as e:
            logger.error(f"❌ Error processing HR data: {e}")

    def cadence_handler(self, sender, data):
        """Handles cadence data."""
        try:
            cadence_spm = data[3]  # Steps per minute
            if self.cadence_callback:
                self.cadence_callback(cadence_spm)
        except Exception as e:
            logger.error(f"❌ Error processing cadence data: {e}")

    def start(self):
        """Starts the BLE HRM listener in a separate asyncio task."""
        asyncio.create_task(self.connect_and_listen())

def run_garmin_hrm_service(ble_address, hr_callback, cadence_callback, disconnect_callback, connection_event):
    """Starts the Garmin HRM BLE service in a separate thread."""
    hrm_service = GarminHRMService(ble_address, hr_callback, cadence_callback, disconnect_callback, connection_event)
    thread = threading.Thread(target=asyncio.run, args=(hrm_service.connect_and_listen(),), daemon=True)
    thread.start()
