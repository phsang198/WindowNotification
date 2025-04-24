@echo off
:: Cài đặt các thư viện trong requirements.txt

set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

pip install -r requirements.txt

:: Hiển thị thông báo hoàn tất
echo Da install xong cac thu vien.

pause