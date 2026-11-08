[app]

# (str) Title of the application
title = simul-trans

# (str) Package name (Android package identifier)
package.name = simultrans

# (str) Package domain (needed for android/ios packaging)
package.domain = org.lxl

# (str) Source code where the main.py lives
source.dir = .

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation
orientation = portrait

[buildozer]

# (int) Log level (0 = none, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 0

[android]

# (str) Android NDK version to use
ndk = 25b

# (str) Android SDK version to use
sdk = 20

# (str) Android API level to use
api = 33

# (str) Minimum Android API level
minapi = 21

# (list) Android architectures to build
archs = arm64-v8a

# (bool) Duplicate the application sources into the APK
duplicate_src = 1

# (list) Permissions
permissions = INTERNET, RECORD_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[ios]

# (str) iOS architectures
#ios.archs = armv7 arm64
