[app]

title = Калькулятор кошторисів
package.name = projectcalculator
package.domain = org.stariBognot

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
source.exclude_dirs = .git,.github,__pycache__,venv,.venv,bin,.buildozer

version = 1.0.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

entrypoint = main.py

presplash.filename =
icon.filename =

android.api = 33
android.minapi = 23
android.ndk = 25b
android.ndk_api = 23

android.archs = arm64-v8a, armeabi-v7a

android.private_storage = True

android.permissions =

android.accept_sdk_license = True

android.enable_androidx = True

p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 1
