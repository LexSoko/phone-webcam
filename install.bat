@echo off 
pyinstaller --noconfirm --clean --windowed --name "PhoneWebcam" --icon "icons/icon.iso" --add-data "html;html" --add-data "css;css" --add-data "config;config" src/main.py
pause