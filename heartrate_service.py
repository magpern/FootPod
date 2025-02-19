import asyncio
import threading
import random
from bleak import BleakClient, BleakError
from logger_config import logger
from config import BLE_HRM_SENSOR_ADDRESS, MOCK_HRM

class GarminHRMService:
    """Handles heart rate and cadence from a Garmin HRM OR returns mock data."""

    HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Heart Rate Measurement UUID
    RSC_UUID = "00002a53-0000-1000-8000-00805f9b34fb"  # Running Speed & Cadence UUID

    def __init__(self, hr_callback=None, cadence_callback=None, disconnect_callback=None, connection_event=None):
        self.ble_address = BLE_HRM_SENSOR_ADDRESS
        self.hr_callback = hr_callback
        self.cadence_callback = cadence_callback
        self.disconnect_callback = disconnect_callback
        self.connection_event = connection_event
        self.client = None

    async def connect_and_listen(self):
        """Continuously tries to connect to BLE HRM and listens for updates OR mocks data."""
        if MOCK_HRM:
            logger.info("🟢 HRM Mocking Enabled - Simulating BLE HRM Data")
            await self.mock_hrm_data()
        else:
            await self.real_hrm_data()

    async def real_hrm_data(self):
        """Handles real HRM BLE communication."""
        while True:
            try:
                logger.info(f"🔄 Attempting to connect to Garmin HRM: {self.ble_address}")

                async with BleakClient(self.ble_address, disconnected_callback=self.on_disconnect) as client:
                    self.client = client
                    logger.info(f"✅ Connected to Garmin HRM: {self.ble_address}")

                    if self.connection_event:
                        self.connection_event.set()

                    await client.start_notify(self.HR_UUID, self.hr_handler)
                    await client.start_notify(self.RSC_UUID, self.cadence_handler)

                    while True:
                        await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ BLE HRM connection error: {e}. Retrying in 10 sec...")
                if self.connection_event:
                    self.connection_event.clear()
                await asyncio.sleep(10)

    async def mock_hrm_data(self):
        """Mocks HRM heart rate (80 ±5 bpm) and cadence (40 ±5 spm)."""
        while True:
            hr_value = random.randint(75, 85)  # 80 ±5 BPM
            cadence_value = random.randint(35, 45)  # 40 ±5 SPM

            if self.hr_callback:
                self.hr_callback(hr_value)

            if self.cadence_callback:
                self.cadence_callback(cadence_value)

            logger.info(f"🟢 Mock HRM -> HR: {hr_value} BPM, Cadence: {cadence_value} SPM")

            await asyncio.sleep(1)  # Simulate HRM update every second

    def on_disconnect(self, client):
        """Handles BLE disconnection."""
        logger.warning(f"⚠️ Garmin HRM Disconnected! Reconnecting...")
        if self.disconnect_callback:
            self.disconnect_callback()

def run_garmin_hrm_service(hr_callback, cadence_callback, disconnect_callback, connection_event):
    """Starts the Garmin HRM BLE service in a separate thread OR runs a mock."""
    hrm_service = GarminHRMService(hr_callback, cadence_callback, disconnect_callback, connection_event)
    thread = threading.Thread(target=asyncio.run, args=(hrm_service.connect_and_listen(),), daemon=True)
    thread.start()
