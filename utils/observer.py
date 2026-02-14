from kivy.utils import platform
import os
import time

# For PC monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = object

# Constants for Android FileObserver
CREATE = 256
MOVED_TO = 128
CLOSE_WRITE = 8

if platform == 'android':
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        from android.permissions import request_permissions, Permission
        
        Context = autoclass('android.content.Context')
        FileObserver = autoclass('android.os.FileObserver')
        Environment = autoclass('android.os.Environment')
        
        class AndroidFileObserver(PythonJavaClass):
            __javainterfaces__ = ['android/os/FileObserver']
            __javacontext__ = 'app'

            def __init__(self, path, callback):
                super().__init__(path, CLOSE_WRITE | MOVED_TO)
                self.callback = callback
                self.directory = path

            @java_method('(ILjava/lang/String;)V')
            def onEvent(self, event, path):
                if path:
                    full_path = os.path.join(self.directory, path)
                    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        print(f"Android FileObserver detected: {full_path}")
                        self.callback(full_path)

    except Exception as e:
        print(f"Error initializing Android libraries: {e}")
        platform = 'pc'

class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            self.callback(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            self.callback(event.dest_path)

def get_android_paths():
    """Returns a list of common image download paths on Android."""
    paths = []
    try:
        # Standard Downloads
        downloads = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
        paths.append(downloads)
        
        # WhatsApp Images (Old and New paths)
        ext_storage = Environment.getExternalStorageDirectory().getAbsolutePath()
        whatsapp_old = os.path.join(ext_storage, "WhatsApp/Media/WhatsApp Images")
        whatsapp_new = os.path.join(ext_storage, "Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images")
        
        if os.path.exists(whatsapp_old): paths.append(whatsapp_old)
        if os.path.exists(whatsapp_new): paths.append(whatsapp_new)
        
        # Pictures / Instagram
        pictures = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
        paths.append(pictures)
        instagram = os.path.join(pictures, "Instagram")
        if os.path.exists(instagram): paths.append(instagram)
        
    except Exception as e:
        print(f"Error getting Android paths: {e}")
    return paths

def start_listening(callback):
    """Starts monitoring for new images."""
    if platform == 'android':
        observers = []
        paths = get_android_paths()
        for path in paths:
            if os.path.exists(path):
                print(f"Starting Android FileObserver for: {path}")
                obs = AndroidFileObserver(path, callback)
                obs.startWatching()
                observers.append(obs)
        return observers
    else:
        if Observer:
            # Simulation paths
            paths_to_watch = [
                os.path.join(os.path.expanduser("~"), "Downloads"),
                os.path.join(os.getcwd(), "test_downloads")
            ]
            if not os.path.exists("test_downloads"):
                os.makedirs("test_downloads")

            observer = Observer()
            event_handler = ImageEventHandler(callback)
            for path in paths_to_watch:
                if os.path.exists(path):
                    observer.schedule(event_handler, path, recursive=False)
                    print(f"Monitoring folder: {path}")
            
            observer.start()
            return observer
    return None

def trigger_notification(title, message):
    """Triggers a system notification."""
    if platform == 'android':
        try:
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationChannel = autoclass('android.app.NotificationChannel')
            NotificationBuilder = autoclass('android.app.Notification$Builder')
            
            # Channel ID is required for API 26+
            channel_id = "steganoscan_alerts"
            name = "SteganoScan Alerts"
            importance = 4 # IMPORTANCE_HIGH
            
            activity = PythonActivity.mActivity
            notification_manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            # Create channel if it doesn't exist
            channel = NotificationChannel(channel_id, name, importance)
            notification_manager.createNotificationChannel(channel)
            
            # Build notification
            builder = NotificationBuilder(activity, channel_id)
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(activity.getApplicationInfo().icon)
            builder.setAutoCancel(True)
            
            notification_manager.notify(int(time.time()), builder.build())
        except Exception as e:
            print(f"Failed to trigger Android Notification: {e}")
    else:
        print(f"--- NOTIFICATION: {title} - {message} ---")
