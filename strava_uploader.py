import requests
import os
from logger_config import logger

# Strava API endpoint
STRAVA_UPLOAD_URL = "https://www.strava.com/api/v3/uploads"
STRAVA_ACTIVITY_URL = "https://www.strava.com/api/v3/activities"

# User must provide their Strava API token (get this from https://www.strava.com/settings/api)
STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")  # Set this via environment variable

def upload_to_strava(fit_filename, title="Treadmill Workout", description=""):
    """
    Uploads a FIT file to Strava manually with title & description.
    :param fit_filename: The FIT file to upload.
    :param title: The title of the workout.
    :param description: A description of the activity.
    """
    if not STRAVA_ACCESS_TOKEN:
        logger.error("❌ STRAVA_ACCESS_TOKEN is not set. Set it as an environment variable.")
        return

    if not os.path.exists(fit_filename):
        logger.error(f"❌ FIT file '{fit_filename}' not found!")
        return

    logger.info(f"📤 Uploading '{fit_filename}' to Strava...")

    with open(fit_filename, "rb") as fit_file:
        response = requests.post(
            STRAVA_UPLOAD_URL,
            headers={"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"},
            files={"file": (fit_filename, fit_file, "application/octet-stream")},
            data={
                "data_type": "fit",
                "name": title,
                "description": description,
                "trainer": 1,  # Marks as an indoor activity
                "private": 0,  # Public by default
            }
        )

    if response.status_code == 201:
        upload_response = response.json()
        activity_id = upload_response.get("id")
        logger.info(f"✅ FIT file uploaded. Activity ID: {activity_id}")

        # Add title & description separately if needed
        if activity_id:
            update_activity(activity_id, title, description)
    else:
        logger.error(f"❌ Strava upload failed: {response.json()}")

def update_activity(activity_id, title, description):
    """Updates the uploaded activity with a title & description."""
    response = requests.put(
        f"{STRAVA_ACTIVITY_URL}/{activity_id}",
        headers={"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"},
        json={"name": title, "description": description}
    )

    if response.status_code == 200:
        logger.info("✅ Activity updated with title & description.")
    else:
        logger.error(f"❌ Failed to update activity: {response.json()}")

def upload_photo(activity_id, image_path):
    """Uploads a photo to a Strava activity."""
    if not os.path.exists(image_path):
        logger.error(f"❌ Image '{image_path}' not found!")
        return

    logger.info(f"📸 Uploading workout summary image to Strava...")

    with open(image_path, "rb") as img:
        response = requests.post(
            f"{STRAVA_ACTIVITY_URL}/{activity_id}/photos",
            headers={"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"},
            files={"file": img}
        )

    if response.status_code == 201:
        logger.info("✅ Workout image uploaded to Strava!")
    else:
        logger.error(f"❌ Failed to upload image: {response.json()}")
        
if __name__ == "__main__":
    fit_file = "treadmill_workout.fit"
    title = input("📌 Enter Strava activity title: ").strip() or "Treadmill Workout"
    description = input("📝 Enter Strava activity description: ").strip() or "Indoor run on the treadmill."
    upload_to_strava(fit_file, title, description)
