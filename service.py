import time
import os
import shutil
from engine.steganalysis import check_stego
from utils.observer import start_listening, trigger_notification

# Paths for scanning
SCAN_DIR = "/sdcard/SteganoScan_Pending"
GALLERY_DIR = "/sdcard/Pictures/SteganoScan_Clean"

if not os.path.exists(SCAN_DIR):
    try: os.makedirs(SCAN_DIR)
    except: pass
if not os.path.exists(GALLERY_DIR):
    try: os.makedirs(GALLERY_DIR)
    except: pass

def on_new_image(path):
    print(f"Service: Detected {path}")
    basename = os.path.basename(path)
    
    # Avoid infinite loops if we are detecting our own moves
    if SCAN_DIR in path or GALLERY_DIR in path:
        return

    temp_path = os.path.join(SCAN_DIR, basename)
    
    try:
        # Move to scanning folder
        print(f"Service: Moving {basename} to scan folder...")
        shutil.move(path, temp_path)
        
        # Scan
        is_stego = check_stego(temp_path)
        
        if is_stego:
            print(f"Service: ALERT! Stego found in {basename}")
            trigger_notification(
                "⚠️ Steganography Detected!",
                f"Suspicious hidden data found in {basename}. Image quarantined."
            )
            # Stay in SCAN_DIR (Quarantine)
        else:
            print(f"Service: {basename} is clean. Moving to Gallery.")
            # Move to clean gallery
            final_path = os.path.join(GALLERY_DIR, basename)
            shutil.move(temp_path, final_path)
            
    except Exception as e:
        print(f"Service Logic Error: {e}")

def setup_foreground():
    """Sets up the service as a Foreground Service with a notification."""
    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        PythonService = autoclass('org.kivy.android.PythonService')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        
        service = PythonService.mService
        channel_id = "steganoscan_service"
        name = "SteganoScan Background Monitor"
        
        notification_manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
        channel = NotificationChannel(channel_id, name, 2) # IMPORTANCE_LOW
        notification_manager.createNotificationChannel(channel)
        
        builder = NotificationBuilder(service, channel_id)
        builder.setContentTitle("SteganoScan Active")
        builder.setContentText("Monitoring for hidden information...")
        builder.setSmallIcon(service.getApplicationInfo().icon)
        
        # ID must not be 0
        service.startForeground(1, builder.build())
        print("Service: Foreground status established.")
    except Exception as e:
        print(f"Service: Could not start foreground: {e}")

if __name__ == '__main__':
    print("SteganoScan Sentinel Service Initializing...")
    
    # Establish foreground status for Android 10+
    try:
        from kivy.utils import platform
        if platform == 'android':
            setup_foreground()
    except:
        pass

    # Start the observer (returns a list of observers on Android)
    observers = start_listening(on_new_image)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if observers:
            if isinstance(observers, list):
                for o in observers: o.stopWatching()
            else:
                observers.stop()
