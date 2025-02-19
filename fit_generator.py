import fitdecode
import time
from datetime import datetime
from logger_config import logger

class FitFileGenerator:
    """Handles FIT file generation for treadmill workouts."""

    def __init__(self, filename="treadmill_workout.fit"):
        """
        Initializes FIT file generation.
        :param filename: Name of the output FIT file.
        """
        self.filename = filename
        self.start_time = int(time.time())
        self.records = []  # Store records before writing

        logger.info(f"📂 FIT File Generation Started: {self.filename}")

    def add_record(self, sensor_data):
        """
        Adds a workout data record to the FIT file.
        :param sensor_data: Dictionary containing speed, cadence, HR, incline, etc.
        """
        timestamp = int(time.time())

        # Create a FIT data record
        record = {
            "timestamp": timestamp,
            "speed": sensor_data["speed"],
            "distance": sensor_data.get("distance", 0),
            "cadence": sensor_data["cadence"],
            "heart_rate": sensor_data["heart_rate"],
            "elevation_gain": sensor_data.get("elevation", 0)
        }

        self.records.append(record)
        logger.debug(f"📡 FIT Record -> {record}")

    def save_fit_file(self):
        """Writes the collected data to a FIT file."""
        with open(self.filename, "wb") as fitfile:
            encoder = fitdecode.FitEncoder(fitfile)

            # Start a new session
            encoder.start_file()
            encoder.write_file_id(type="activity", time_created=datetime.utcfromtimestamp(self.start_time))

            # Write records
            for record in self.records:
                encoder.write_record(record)

            encoder.finish_file()

        logger.info(f"✅ FIT File Saved: {self.filename}")
