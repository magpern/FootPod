# FootPod Project

🚀 **FootPod** is a Python-based project that emulates an ANT+ Foot Pod using BLE data from a treadmill (FTMS) and a heart rate monitor (HRM). The project transmits real-time speed, cadence, and heart rate over ANT+.

## 📌 Features
✅ Reads speed & incline from an FTMS-enabled treadmill  
✅ Reads heart rate & cadence from a Garmin HRM  
✅ Generates a FIT file for upload to Strava  
✅ Broadcasts data over ANT+  
✅ Supports automatic reconnection for BLE devices  

## 🛠️ Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/magpern/FootPod.git
   cd FootPod
   ```

2. **Create a virtual environment (Recommended)**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## 🚴‍♂️ Running the Project
```sh
python main.py
```

## 🔌 BLE Device Setup
- **Treadmill (FTMS)**
  - Ensure your treadmill supports FTMS BLE.
  - The app will attempt to connect automatically.
  
- **Garmin HRM**
  - Ensure your HRM is turned on and broadcasting.
  - The app will detect and connect automatically.

## 📡 ANT+ Broadcast
The FootPod emulator sends ANT+ messages every 250ms (4Hz), supporting:
- **Page 1** (Speed & Distance)
- **Page 2** (Cadence & Stride)
- **Pages 80 & 81** (Device information)

## 📂 FIT File Generation
- A FIT file is generated during the session.
- Once the workout ends, you can upload the FIT file to Strava.

## 🔧 Configuration
Modify `config.py` to adjust settings like:
- BLE device addresses
- ANT+ network ID
- FIT file naming conventions

## 🛑 Stopping the Service
Press `CTRL+C` to stop the program. The FIT file will be finalized and saved.

## 📜 License
This project is **open-source** under the MIT License.

---
🚀 Developed by **@magpern**
