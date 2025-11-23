@echo off
chcp 65001
echo Build starting... 
cls 

pyinstaller --onefile --windowed --icon=icon.ico --name="SystemTool" --add-data="icon.ico;." main.py
pause