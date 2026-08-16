[app]

# (str) Назва програми
title = Electro Calculator

# (str) Назва пакета — тільки латинські літери та цифри, без пробілів
package.name = projectcalculator

# (str) Унікальний домен програми
package.domain = org.staribognot

# (str) Папка з вашим кодом
source.dir = progekt_caculate


# (str) Файли, які потрібно включати до APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,txt

# (list) Папки, які не потрібно включати до APK
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,.venv,env,.env

# (str) Версія програми
version = 1.0.0

# (str) Основний файл програми
# Якщо ваш головний файл називається main.py — залишайте так.
entrypoint = main.py

# (list) Залежності Python.
# Kivy 2.3.0 сумісний з Android.
requirements = python3,kivy==2.3.0

# (str) Орієнтація екрана
orientation = portrait

# (bool) Повноекранний режим.
# 0 = Android покаже верхню системну панель.
fullscreen = 0

# (str) Шлях до іконки програми, якщо вона є.
# Приклад: icon.filename = assets/icon.png
icon.filename =

# (str) Зображення, яке показується під час запуску.
# Приклад: presplash.filename = assets/presplash.png
presplash.filename =


# -------------------------------------------------------------------
# Android configuration
# -------------------------------------------------------------------

# Android API для компіляції
android.api = 33

# Мінімальна Android версія для встановлення програми.
# API 24 = Android 7.0.
#
# ВАЖЛИВО:
# API 23 спричиняв помилку:
# implicit declaration of function 'preadv'
# implicit declaration of function 'pwritev'
#
# Тому значення має бути НЕ МЕНШЕ 24.
android.minapi = 24

# Android NDK API.
# Має бути 24 або вище, інакше Python не збереться.
android.ndk_api = 24

# Версія NDK
android.ndk = 25b

# Архітектура APK.
# arm64-v8a підходить для сучасних Samsung, Xiaomi, Pixel тощо.
# Це найстабільніша та найшвидша конфігурація збірки.
android.archs = arm64-v8a

# Використовувати внутрішнє сховище програми.
# Це правильно для SQLite БД та PNG-експорту на Android 10+.
android.private_storage = True

# AndroidX
android.enable_androidx = True

# Автоматично приймати Android SDK ліцензії
android.accept_sdk_license = True

# SDL2 bootstrap необхідний Kivy
p4a.bootstrap = sdl2

# Не потрібні небезпечні permissions.
# База даних та PNG зберігаються у внутрішній папці програми.
android.permissions =

# Якщо в майбутньому потрібен доступ до Інтернету:
# android.permissions = INTERNET

# Якщо потрібна вібрація:
# android.permissions = VIBRATE


# -------------------------------------------------------------------
# Buildozer configuration
# -------------------------------------------------------------------

[buildozer]

# 2 показує детальний лог у GitHub Actions
log_level = 2

# Попереджати, якщо Buildozer запущений від root
warn_on_root = 1
