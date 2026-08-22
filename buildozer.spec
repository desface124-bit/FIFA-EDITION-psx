[app]

# (str) Title of your application
title = FIFA 2001 Editor

# (str) Package name
package.name = fifa2001editor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.fifa2001

# (str) Source code where main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,bin,dbi,img,iso

# (str) Application version
version = 1.0

# (list) List of requirements
requirements = python3,kivy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (list) List of service to declare
services =


[buildozer]

# (int) Log level (0 = error only, 1 = warning, 2 = info, 3 = debug)
log_level = 2

# (bool) Display warning if running as root
warn_on_root = 1

# (str) Path to build artifacts
build_dir = .buildozer

# (str) Path to generated APK/AAB
bin_dir = ./bin


[android]

# (str) Android API target
android.api = 35

# (str) Minimum API supported
android.minapi = 23

# (str) Android NDK version
android.ndk = 27c

# (str) Android architecture
android.arch = arm64-v8a

# (list) Android permissions
android.permissions = READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

# (bool) Use AndroidX
android.enable_androidx = True

# (bool) Build an APK instead of an AAB by default
android.release_artifact = apk

# (bool) Accept SDK licenses automatically
android.accept_sdk_license = True


[python-for-android]

# (str) Python-for-Android branch
p4a.branch = master


[app:android]

# Android application settings
android.presplash_color = #101010
