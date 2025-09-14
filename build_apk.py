import os
import subprocess

print("🚀 بناء تطبيق Android APK...")

# إنشاء ملف flet.config.json إذا لم يكن موجوداً
flet_config = {
    "name": "Chrodis",
    "description": "Chrodis Medical Assistant",
    "org": "com.youssef.chrodis",
    "icon": "image.ico",
    "python": "main.py"
}

with open('flet.config.json', 'w') as f:
    import json
    json.dump(flet_config, f, indent=2)

print("✅ تم إنشاء ملف flet.config.json")

# بناء APK باستخدام Flet
try:
    result = subprocess.run([
        'flet', 'build', 'apk'
    ], capture_output=True, text=True, check=True)
    
    print("✅ تم بناء APK بنجاح!")
    print("Output:", result.stdout)
    
except subprocess.CalledProcessError as e:
    print("❌ فشل في بناء APK:")
    print("Error:", e.stderr)
    print("Output:", e.stdout)
    exit(1)
