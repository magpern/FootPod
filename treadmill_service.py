import asyncio
import threading
from bleak import BleakClient, BleakError
from logger_config import logger
from config import BLE_TREADMILL_SENSOR_ADDRESS, MOCK_FTMS

class TreadmillService:
    """Fetches treadmill speed, incline, and other metrics from BLE FTMS service OR returns mock data."""

    FTMS_UUID = "00002acd-0000-1000-8000-00805f9b34fb"  # FTMS UUID

    def __init__(self, callback=None, disconnect_callback=None, connection_event=None):
        self.ble_address = BLE_TREADMILL_SENSOR_ADDRESS
        self.callback = callback
        self.disconnect_callback = disconnect_callback
        self.connection_event = connection_event
        self.client = None

        # Store last known values for combining messages
        self.last_speed_mps = 0.0
        self.last_incline = 0.0
        self.total_distance_m = 0.0
        self.elapsed_time_s = 0
        self.total_energy_kcal = 0
        self.heart_rate_bpm = 0
        self.ramp_angle = 0.0
        self.energy_per_hour = 0
        self.energy_per_minute = 0

    async def connect_and_listen(self):
        """Continuously tries to connect to BLE treadmill and listens for updates OR mocks data."""
        if MOCK_FTMS:
            logger.info("🟢 FTMS Mocking Enabled - Simulating BLE Treadmill Data")
            await self.mock_ftms_data()
        else:
            await self.real_ftms_data()

    async def real_ftms_data(self):
        """Handles real FTMS BLE communication."""
        while True:
            try:
                logger.info(f"🔄 Attempting to connect to FTMS Treadmill: {self.ble_address}")

                async with BleakClient(self.ble_address, disconnected_callback=self.on_disconnect) as client:
                    self.client = client
                    logger.info(f"✅ Connected to FTMS Treadmill: {self.ble_address}")

                    if self.connection_event:
                        self.connection_event.set()  # Notify service_manager that connection is established

                    await client.start_notify(self.FTMS_UUID, self.notification_handler)

                    while True:
                        await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ BLE FTMS connection error: {e}. Retrying in 10 sec...")
                if self.connection_event:
                    self.connection_event.clear()
                await asyncio.sleep(10)

    def notification_handler(self, sender, data):
        """Handles incoming FTMS treadmill data, updating speed, incline, and other available metrics."""
        try:
            logger.debug(f"🔍 Raw FTMS Data: {list(data)} (Length: {len(data)})")

            # Read first two bytes as flags
            flags = int.from_bytes(data[0:2], byteorder="little")

            index = 2  # Start reading after the flags

            # Instantaneous Speed (bit 0)
            if flags & (1 << 0) and index + 2 <= len(data):
                self.last_speed_mps = (int.from_bytes(data[index:index+2], byteorder="little") / 100) / 3.6
                index += 2
                logger.info(f"📡 FTMS Speed: {self.last_speed_mps:.2f} m/s")

            # Average Speed (bit 1)
            if flags & (1 << 1) and index + 2 <= len(data):
                avg_speed_mps = (int.from_bytes(data[index:index+2], byteorder="little") / 100) / 3.6
                index += 2
                logger.info(f"📡 FTMS Avg Speed: {avg_speed_mps:.2f} m/s")

            # Total Distance (bit 2)
            if flags & (1 << 2) and index + 3 <= len(data):
                self.total_distance_m = int.from_bytes(data[index:index+3], byteorder="little") / 100.0
                index += 3
                logger.info(f"📡 FTMS Distance: {self.total_distance_m:.1f} m")

            # Incline (bit 3)
            if flags & (1 << 3) and index + 2 <= len(data):
                incline_raw = int.from_bytes(data[index:index+2], byteorder="little", signed=True)
                self.last_incline = incline_raw / 10.0  # Convert 1/10 % grade
                index += 2
                logger.info(f"📡 FTMS Incline: {self.last_incline:.1f}%")

            # Ramp Angle Setting (bit 4)
            if flags & (1 << 4) and index + 2 <= len(data):
                self.ramp_angle = int.from_bytes(data[index:index+2], byteorder="little", signed=True) / 10.0
                index += 2
                logger.info(f"📡 FTMS Ramp Angle: {self.ramp_angle:.1f}°")

            # Total Energy (bit 5)
            if flags & (1 << 5) and index + 2 <= len(data):
                self.total_energy_kcal = int.from_bytes(data[index:index+2], byteorder="little")
                index += 2
                logger.info(f"📡 FTMS Total Energy: {self.total_energy_kcal} kcal")

            # Energy Per Hour (bit 6)
            if flags & (1 << 6) and index + 2 <= len(data):
                self.energy_per_hour = int.from_bytes(data[index:index+2], byteorder="little")
                index += 2
                logger.info(f"📡 FTMS Energy Per Hour: {self.energy_per_hour} kcal/h")

            # Energy Per Minute (bit 7)
            if flags & (1 << 7) and index + 1 <= len(data):
                self.energy_per_minute = data[index]
                index += 1
                logger.info(f"📡 FTMS Energy Per Minute: {self.energy_per_minute} kcal/min")

            # Heart Rate (bit 8)
            if flags & (1 << 8) and index + 1 <= len(data):
                self.heart_rate_bpm = data[index]
                index += 1
                logger.info(f"📡 FTMS Heart Rate: {self.heart_rate_bpm} BPM")

            # Elapsed Time (bit 9)
            if flags & (1 << 9) and index + 2 <= len(data):
                self.elapsed_time_s = int.from_bytes(data[index:index+2], byteorder="little")
                index += 2
                logger.info(f"📡 FTMS Elapsed Time: {self.elapsed_time_s} sec")

            # Send the last known values together
            if self.callback:
                self.callback(
                    self.last_speed_mps, self.last_incline, self.total_distance_m, 
                    self.total_energy_kcal, self.elapsed_time_s, self.heart_rate_bpm,
                    self.ramp_angle, self.energy_per_hour, self.energy_per_minute
                )

        except Exception as e:
            logger.error(f"❌ Error processing FTMS data: {e}")


    def on_disconnect(self, client):
        """Handles BLE disconnection."""
        logger.warning(f"⚠️ FTMS Treadmill Disconnected! Reconnecting...")
        if self.disconnect_callback:
            self.disconnect_callback()

    async def mock_ftms_data(self):
        """Mocks FTMS treadmill speed, incline, distance, energy, and heart rate."""
        while True:
            self.last_speed_mps = 3.0 / 3.6  # Convert 3 km/h to m/s
            self.last_incline = 1.0  # 1% incline
            self.total_distance_m += self.last_speed_mps * 1  # Increase distance every second
            self.total_energy_kcal += 0.1  # Fake energy expenditure
            self.elapsed_time_s += 1  # Simulate elapsed time
            self.heart_rate_bpm = 100  # Simulated HR
            self.ramp_angle = 0.5  # Mocked ramp angle (0.5 degrees)
            self.energy_per_hour = 600  # Mocked energy burn rate (600 kcal/h)
            self.energy_per_minute = 10  # Mocked energy burn rate (10 kcal/min)

            if self.callback:
                self.callback(
                    self.last_speed_mps, self.last_incline, self.total_distance_m, 
                    self.total_energy_kcal, self.elapsed_time_s, self.heart_rate_bpm,
                    self.ramp_angle, self.energy_per_hour, self.energy_per_minute
                )

            logger.info(
                f"🟢 Mock FTMS -> Speed: {self.last_speed_mps:.2f} m/s, Incline: {self.last_incline:.1f}%, "
                f"Distance: {self.total_distance_m:.1f} m, Energy: {self.total_energy_kcal} kcal, "
                f"Time: {self.elapsed_time_s} sec, HR: {self.heart_rate_bpm} BPM, "
                f"Ramp Angle: {self.ramp_angle:.1f}°, Energy/hour: {self.energy_per_hour} kcal/h, "
                f"Energy/minute: {self.energy_per_minute} kcal/min"
            )

            await asyncio.sleep(1)  # Simulate FTMS update every second

def run_treadmill_service(callback, disconnect_callback, connection_event):
    """Starts the FTMS treadmill BLE service in a separate thread OR runs a mock."""
    treadmill_service = TreadmillService(callback, disconnect_callback, connection_event)
    thread = threading.Thread(target=asyncio.run, args=(treadmill_service.connect_and_listen(),), daemon=True)
    thread.start()
