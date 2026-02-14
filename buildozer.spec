[app]

# (str) Title of your application
title = SteganoScan Sentinel

# (str) Package name
package.name = steganoscan

# (str) Package domain (needed for android/ios packaging)
package.domain = org.cyberwarlab

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# Removed scipy (too heavy/complex) and watchdog (using Android FileObserver)
requirements = python3,kivy==2.3.0,opencv,numpy,pyjnius

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, POST_NOTIFICATIONS, FOREGROUND_SERVICE, READ_MEDIA_IMAGES

# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use --private data storage (True) or shared storage (False)
android.private_storage = True

# (list) Services to create
services = SentinelService:service.py

# (list) Supported orientations
orientation = portrait

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
