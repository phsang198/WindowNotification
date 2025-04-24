@echo off
:: Cài đặt các thư viện trong requirements.txt
pyinstaller --onefile --noconsole --add-data "config.json;." server.py

:: Hiển thị thông báo hoàn tất
echo Da install xong cac thu vien.
pause
