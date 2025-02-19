import matplotlib.pyplot as plt
import os
from datetime import datetime
from logger_config import logger

def generate_workout_image(workout_summary, output_path="workout_summary.png"):
    """
    Generates a workout summary image.
    :param workout_summary: Dictionary with workout stats (distance, time, HR, cadence, incline, elevation).
    :param output_path: Path to save the generated image.
    """
    logger.info("🎨 Generating workout summary image...")

    # Extract workout data
    distance_km = workout_summary.get("distance", 0) / 1000  # Convert meters to km
    duration_min = workout_summary.get("duration", 0) / 60  # Convert sec to min
    avg_hr = workout_summary.get("avg_heart_rate", 0)
    avg_cadence = workout_summary.get("avg_cadence", 0)
    avg_incline = workout_summary.get("avg_incline", 0)
    total_elevation = workout_summary.get("total_elevation", 0)

    # Create a figure
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#2E2E2E')  # Background color
    ax.set_facecolor('#3E3E3E')

    # Text formatting
    title = "🏃 Treadmill Workout Summary"
    stats = [
        f"📏 Distance: {distance_km:.2f} km",
        f"⏳ Duration: {duration_min:.1f} min",
        f"❤️ Avg HR: {avg_hr} BPM",
        f"🏃 Cadence: {avg_cadence} SPM",
        f"📈 Avg Incline: {avg_incline}%",
        f"⛰️ Elevation Gain: {total_elevation:.2f} m"
    ]

    ax.text(0.5, 0.85, title, fontsize=14, fontweight='bold', ha='center', color="white")
    for i, stat in enumerate(stats):
        ax.text(0.5, 0.7 - (i * 0.1), stat, fontsize=12, ha='center', color="white")

    ax.set_xticks([])  # Remove axes
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Save the image
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    logger.info(f"✅ Workout summary image saved: {output_path}")

    return output_path

# Example usage (for testing)
if __name__ == "__main__":
    test_summary = {
        "distance": 5000,  # meters
        "duration": 1800,  # seconds
        "avg_heart_rate": 145,
        "avg_cadence": 85,
        "avg_incline": 2.5,
        "total_elevation": 50  # meters
    }
    generate_workout_image(test_summary)
