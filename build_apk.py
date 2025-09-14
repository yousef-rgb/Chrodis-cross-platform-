import os
import subprocess

print("🚀 بناء تطبيق Android APK...")

# أوامر بناء APK باستخدام Flet
subprocess.run([
    'flet', 'build', 'apk',
    '--python', 'main.py',
    '--name', 'Chrodis',
    '--product-name', 'Chrodis Medical Assistant',
    '--org', 'com.youssef.chrodis',
    '--icon', 'image.ico'
], check=True)

print("✅ تم بناء APK بنجاح! يمكنك العثور عليه في مجلد build/apk")
