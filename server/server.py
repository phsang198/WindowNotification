import ctypes
import io
import json
import os
import sys
import threading
import time
from ctypes import wintypes

import socket

import pygame
import schedule
from flask import Flask, request
from gtts import gTTS
from winotify import Notification

app = Flask(__name__)

def show_message2(message,_duration):
    def show():
        toast = Notification(
        app_id='NHẮC NHỞ',
        title='THÔNG BÁO',
        msg=message,
        duration="short"  # "short" hoặc "long"
        )

        toast.show()

        tts = gTTS(text=message, lang='vi')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        # Phát âm thanh với pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue

    thread = threading.Thread(target=show)
    thread.start()

def show_message(message, type="info"):
    def load_icon(icon_path):
        LR_LOADFROMFILE = 0x00000010
        LR_DEFAULTSIZE = 0x00000040
        # Convert to absolute path if needed
        import os
        icon_path = os.path.abspath(icon_path)
        # Load as HICON (type 1)
        hicon = ctypes.windll.user32.LoadImageW(
            None,
            icon_path,
            1,  # IMAGE_ICON
            0, 0,  # Use actual size
            LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        return hicon

    def show():
        class MSGBOXPARAMS(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("hwndOwner", wintypes.HWND),
                ("hInstance", wintypes.HINSTANCE),
                ("lpszText", wintypes.LPCWSTR),
                ("lpszCaption", wintypes.LPCWSTR),
                ("dwStyle", wintypes.UINT),
                ("lpszIcon", wintypes.LPCWSTR),
                ("dwContextHelpId", wintypes.DWORD),
                ("lpfnMsgBoxCallback", wintypes.LPVOID),
                ("dwLanguageId", wintypes.DWORD),
            ]

        MB_ICONINFORMATION = 0x40
        MB_OK = 0x0
        MB_TOPMOST = 0x1000
        MB_ICONWARNING = 0x30
        MB_ICONERROR = 0x10
        MB_ICONQUESTION = 0x20

        if type == "warning":
            icon = MB_ICONWARNING
            title="Cảnh báo"
        elif type == "error":
            icon = MB_ICONERROR
            title="Lỗi"
        elif type == "question":
            icon = MB_ICONQUESTION
            title="Câu hỏi"
        else:
            icon = MB_ICONINFORMATION  # Mặc định là thông tin
            title="Thông báo"

        params = MSGBOXPARAMS()
        params.cbSize = ctypes.sizeof(MSGBOXPARAMS)
        params.hwndOwner = 0
        params.hInstance = load_icon("F:\\OutSource\\PYTHON\\NHACNHO\\info.ico")
        params.lpszText = message
        params.lpszCaption = title
        params.dwStyle = MB_OK | icon | MB_TOPMOST
        params.lpszIcon = None
        params.dwContextHelpId = 0
        params.lpfnMsgBoxCallback = None
        params.dwLanguageId = 0

        ctypes.windll.user32.MessageBoxIndirectW(ctypes.byref(params))

    thread = threading.Thread(target=show)
    thread.start()

# Hàm xử lý lịch chạy theo loại
def create_schedule(task_type, date_time, message):
    if task_type == "daily":
        # Lặp lại hàng ngày vào giờ đã cho
        schedule.every().day.at(date_time).do(show_message, message)
    elif task_type == "timepoint":
        # Chạy một lần tại thời gian đã cho
        def run_once():
            show_message(message)
            return schedule.CancelJob  # Hủy công việc sau khi chạy
        schedule.every().day.at(date_time).do(run_once)

# Endpoint nhận thông tin và tạo lịch
@app.route('/schedule', methods=['POST'])
def create_schedule_route():
    data = request.get_json()

    # Kiểm tra thông tin đầu vào
    try:
        date_time = data['datetime']  # Ngày/giờ hoặc chỉ giờ/phút
        message = data['message']
        task_type = data['type']  # daily hoặc timepoint
    except KeyError:
        return "Thiếu thông tin trong JSON", 400

    # Tạo lịch theo loại
    create_schedule(task_type, date_time, message)
    return "Lịch đã được tạo", 200

@app.route('/message', methods=['POST'])
def message_box():
    data = request.get_json()

    # Kiểm tra thông tin đầu vào
    try:
        message = data['message']
        type = data['type']
        where = data['where']
        duration = data['duration']

    except KeyError:
        return "Thiếu thông tin trong JSON", 400

    # Tạo lịch theo loại
    if where == 'between' :
        show_message(message,type)
    else:
        show_message2(message,duration)

    return "ok", 200

#def read_config():
    # Kiểm tra xem ứng dụng đang chạy từ file .exe hay .py
    if getattr(sys, 'frozen', False):
        # Nếu là file .exe (frozen)
        application_path = os.path.dirname(sys.executable)
    else:
        # Nếu là file .py
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Đường dẫn đến file config.json
    config_file_path = os.path.join(application_path, 'config.json')
    try:
        # Đọc config.json
        with open(config_file_path, "r") as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(f"Không thể đọc config.json: {e}")
        return None
    
def find_free_port(start_port):
    """Tìm cổng rảnh bắt đầu từ start_port"""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:  # Nếu không kết nối được, cổng rảnh
                return port
            port += 1
            
def get_local_ip():
    """Lấy địa chỉ IP của máy tính"""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# Hàm chạy service Flask
def run_flask():
    #config = read_config()
    #if config:
        #_host = config.get("host", "0.0.0.0")  # Giá trị mặc định nếu không có trong config
        #_port = config.get("port", 5152) 
    app.run(host=get_local_ip(), port=find_free_port(5152)) ;

# Hàm chạy lịch
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Chạy Flask trên một luồng riêng
    threading.Thread(target=run_flask, daemon=True).start()
    # Chạy lịch
    run_schedule()
