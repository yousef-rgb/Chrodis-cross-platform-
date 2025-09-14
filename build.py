import PyInstaller.__main__
import os

# إعدادات بناء تطبيق Windows
PyInstaller.__main__.run([
    'main.py',
    '--name=Chrodis',
    '--onefile',
    '--windowed',
    '--icon=image.ico',
    '--add-data=.env;.',
    '--version-file=version.txt'
])
