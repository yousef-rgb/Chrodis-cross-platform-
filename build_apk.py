import os
import subprocess

print("🚀 بناء تطبيق Android APK...")

# الطريقة المباشرة بدون خيارات إضافية
try:
    # أولاً أنشئ ملف flet.config.json
    config = {
        "name": "Chrodis",
        "description": "Chrodis Medical Assistant",
        "org": "com.youssef.chrodis",
        "icon": "image.ico"
    }
    
    import json
    with open('flet.config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # ثم نفّذ أمر البناء
    result = subprocess.run([
        'flet', 'build', 'apk', 'main.py'
    ], capture_output=True, text=True, check=True)
    
    print("✅ تم بناء APK بنجاح!")
    print("Output:", result.stdout)
    
except Exception as e:
    print("❌ فشل في بناء APK:", str(e))
    exit(1)
