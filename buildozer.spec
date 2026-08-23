[app]

# (str) Title of your application
title = FIFA 2001 Player Editor

# (str) Package name
package.name = fifa2001editor

# (str) Package domain (needed for Android)
package.domain = org.jegames

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

# (list) Application requirements
requirements = python3,kivy,plyer

# (str) Presplash of the application
presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation
orientation = portrait

# (list) Android permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (bool) Indicate if the app should be fullscreen
fullscreen = 0

# (str) Android API target
android.api = 33

# (str) Minimum Android API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Android architecture
android.archs = arm64-v8a, armeabi-v7a

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (bool) Copy the application data to external storage
android.private_storage = True

# (str) Version
version = 1.0.0

# (str) Name of the main Python file
# Keep the Python file in the same folder as this buildozer.spec
source.main = main.py


[buildozer]

# (str) Log level
log_level = 2

# (bool) Warn when buildozer.spec changes
warn_on_root = 1


[android]

# (bool) Enable Android backup
android.allow_backup = True

# (str) Android app activity orientation
android.orientation = portrait

# (bool) Use AndroidX
android.enable_androidx = True

# (str) Android app theme
android.add_src =

# (list) Gradle dependencies
android.gradle_dependencies =

# (str) Extra arguments for python-for-android
p4a.branch = main

# (str) Extra python-for-android arguments
p4a.extra_args =

# (bool) Enable logcat on build
android.logcat_filters = *:S python:D


[toolchain]

# (str) Python-for-Android toolchain
