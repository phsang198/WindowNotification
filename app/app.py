import ctypes
import os
import threading
import tkinter as tk
from ctypes import windll

import pyautogui
from PIL import Image, ImageDraw, ImageFont

import sys
import os

if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ tệp .exe
    base_path = sys._MEIPASS
else:
    # Nếu đang phát triển (không phải .exe)
    base_path = os.path.dirname(os.path.abspath(__file__))

IMAGE_PATH = os.path.join(base_path, '1.jpg')
OUTPUT_IMAGE = os.path.join(base_path, 'bg.PNG')
FONT_PATH = os.path.join(base_path, 'font.ttf')
TEXT_PATH = os.path.join(base_path, 'save.txt')

def load_text():
    if os.path.exists(TEXT_PATH):
        with open(TEXT_PATH, "r", encoding="utf-8") as file:
            content = file.read()
            text_box.insert("1.0", content)  # Hiển thị nội dung lên text_box


def save_text_to_file(text):
    
    with open(TEXT_PATH, "w", encoding="utf-8") as file:
        file.write(text)

def func(text):
    try :
        screen_width, screen_height = pyautogui.size()
        
        # Mở và resize ảnh
        img = Image.open(IMAGE_PATH)
        img = img.resize((screen_width, int(img.height * screen_width / img.width)),
                        resample=Image.Resampling.LANCZOS)
        
        img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # Cài đặt font
        font_size = 19
        try:
            font = ImageFont.truetype(FONT_PATH, font_size,encoding="unic" )
        except OSError:
            print("Font không tìm thấy!")
            return

        # Thông số box
        le_tren = 50
        le_phai = 15
        line_spacing = 15
        box_width = 310
        box_height = 380
        text_margin = 10
        
        # Vị trí box
        box_position = (
            screen_width - box_width - le_phai,
            le_tren,
            screen_width - le_phai ,
            le_tren + box_height
        )
        
        outer_box_position = (
            screen_width - box_width - le_phai ,  # Thêm margin cho box ngoài
            le_tren - 35,
            screen_width - le_phai ,
            le_tren
        )
        outl_box = (
            screen_width - box_width - le_phai ,  # Thêm margin cho box ngoài
            le_tren - 35,
            screen_width - le_phai ,
            le_tren + box_height
        )

        draw.rectangle(
            outer_box_position,
            fill= (255, 247, 209)
        )

        # Vẽ box
        draw.rectangle(
            box_position,
            fill=(255, 247, 209)
        )

        draw.rectangle(
            outl_box,
            outline=(0, 0, 0),
            width=1
        )
        
        # Xử lý và vẽ text
        lines = text.split("\n")
        current_y = le_tren
        
        for line in lines:
            # Vẽ text với margin từ viền box
            draw.text(
                (box_position[0] + text_margin , current_y),
                line.strip(),
                fill=(0, 0, 0),
                font=font
            )
            
            # Tính độ cao của dòng text
            bbox = draw.textbbox((0, 0), line, font=font)
            text_height = bbox[3] - bbox[1]
            current_y += text_height + line_spacing
        
        # Lưu ảnh
        img.save(OUTPUT_IMAGE, format='PNG', quality=100, optimize=False)


        #pyautogui.hotkey('win', 'd')  # Thu nhỏ cửa sổ
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02

        # Dùng ctypes để gọi API SystemParametersInfo
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, OUTPUT_IMAGE, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

        #print(text)
        save_text_to_file(text)  

        root.destroy()
    except Exception as e:
        print(f"Error: {e}")
        root.destroy()

# Hàm xử lý ảnh
def save_note():
    text = text_box.get("1.0", "end-1c").strip()  # Lấy nội dung từ text box
    text = text.encode('utf-8').decode('utf-8')
    if not text:
        return  # Không làm gì nếu không có nội dung

    if not os.path.exists(IMAGE_PATH):
        print("Ảnh gốc không tồn tại!")
        return
    
    thread = threading.Thread(target=func, args=(text,))
    thread.daemon = True

    thread.start()
    root.withdraw()

# Tạo cửa sổ Tkinter
windll.shcore.SetProcessDpiAwareness(1)
root = tk.Tk()
root.title("")
root.geometry("300x400")  # Kích thước cửa sổ
root.configure(bg="#fff2ab")  # Màu nền trắng
#root.overrideredirect(True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 300
window_height = 400

position_top = int((screen_height - window_height) / 2)
position_right = int((screen_width - window_width) / 2)

root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Text box
text_box = tk.Text(root, font=("Times New Roman", 16), wrap="word", bg="#fff7d1", bd=0)
text_box.pack(expand=True, fill="both", padx=10, pady=10)

# Lắng nghe phím Ctrl+S
def handle_ctrl_s(event):
    save_note()

root.bind('<Control-s>', handle_ctrl_s)

def handle_escape(event):
    root.destroy()

root.bind('<Escape>', handle_escape)

load_text()
text_box.focus_set()

root.mainloop()