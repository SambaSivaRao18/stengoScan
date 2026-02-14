# SteganoScan Sentinel

**SteganoScan Sentinel** is a production-ready Mobile Steganalysis App designed for Android. It monitors your device's media gallery in real-time and uses statistical bit-analysis to detect hidden steganographic content.

## Features

- **Real-time Monitoring**: Uses Android `ContentObserver` to detect new images.
- **Statistical Detection**: Implements a Chi-Square test on the Least Significant Bits (LSB).
- **Background Scans**: Analyzes images in a separate thread.
- **UI Alerts**: Displays a modal security warning when hidden information is detected.

## Local Development (Windows / Simulation)

To run the UI on your desktop for testing:

1. **Delete broken environments** (if any):
   ```powershell
   Remove-Item -Recurse -Force venv, .venv
   ```

2. **Create a fresh environment with Python 3.12**:
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```powershell
   python -m src.main
   ```

## Troubleshooting
If you see `ModuleNotFoundError: No module named 'kivy'`, it means your virtual environment is not active or was created with the wrong Python version (like 3.14). Always ensure `(venv)` is visible in your prompt.

## How to Test UI Alerts
Click the red **"Test Alert UI"** button in the app to see the steganography detection popup.
