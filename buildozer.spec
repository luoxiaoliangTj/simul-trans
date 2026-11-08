[app]

# (str) Title of the application
title = simul-trans

# (str) Package name (Android package identifier, no dots in the first segment)
package.name = simultrans

# (str) Package domain (needed for android/ios packaging)
package.domain = org.lxl

# (str) Source code where the main.py lives
source = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Source files to exclude
source.exclude_exts = spec

# (list) Source files to exclude (regex)
source.exclude_patterns = __pycache__, *.pyc, .git, .github, build, bin

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,android

# (str) Supported orientation (one of landscape, sensorLandscape, sensorPortrait, portrait)
orientation = portrait

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported Android API level
#android.api = 33

# (str) Minimum Android API level
#android.minapi = 21

# (list) Android architectures to build
android.archs = arm64-v8a

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) Duplicate the application sources into the APK
android.duplicate_src = 1

# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be >= android.minapi
#android.target_api = 33

# (str) Android entrypoint, default is main activity
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class of the Android Activity
#android.activity_class_name = org.kivy.android.PythonActivity

# (list) Additional Java source files to compile
#android.add_src = %(source.dir)s/src/android

# (list) Python modules to add (compiled)
#android.add_jar =

# (str) Python-for-Android git checkout directory (default: automatic)
#p4a.local_recipe =

# (str) Buildozer log level (0 = none, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1

# (str) Path to a custom buildozer spec
#build_spec = %(source.dir)s/buildozer.spec

[buildozer]

# (int) Log level (0 = none, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1

# (str) Path to buildozer working directory
#build_dir = .buildozer

# (str) Path to the output directory (where the .apk will be generated)
#bin_dir = %(source.dir)s/bin

# (str) Name of the APK to generate
#apk_filename = %(source.dir)s/bin/%(app.package.name)s-%(app.version)s.apk

# (str) Python-for-Android version to use
#p4a = develop

# (str) Python-for-Android git repository
#p4a.source = https://github.com/kivy/python-for-android.git

# (str) Python-for-Android git branch
#p4a.branch = master

# (str) Python-for-Android git commit
#p4a.commit = HEAD

[android]

# (str) Android NDK version to use
ndk = 25b

# (str) Android SDK version to use
sdk = 20

# (str) Android API level to use
api = 33

# (str) Minimum Android API level
minapi = 21

# (str) Android NDK directory (if empty, it will be downloaded)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be downloaded)
#android.sdk_path =

# (str) ANT directory (if empty, it will be downloaded)
#android.ant_path =

# (str) python-for-android fork to use if not using p4a from pypi
#android.p4a_fork = kivy

# (list) Python dependencies to install via pip (in addition to requirements)
#android.add_pip =

[ios]

# (str) Name of the extension file to use
#ios.extension_file = %(source.dir)s/ios/extension.m

# (list) Source files to include
#ios.source.include_exts = py,m,mm,h,c

# (list) Source files to exclude
#ios.source.exclude_exts =

# (list) Source files to exclude (regex)
#ios.source.exclude_patterns =

# (str) Code signing identity
#ios.code_signing_identity =

# (str) iOS deployment target
#ios.deployment_target = 11.0

# (str) iOS architectures
#ios.archs = armv7 arm64
