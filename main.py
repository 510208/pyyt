import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import messagebox
from tkinter import Tk, Checkbutton, IntVar
from tkinter import filedialog
from tkinter import PhotoImage, Toplevel
from pytube import YouTube
import re
import shutil
import logging
import ssl
ssl._create_default_https_context = ssl._create_stdlib_context
from moviepy.editor import *
from moviepy.config import change_settings
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TALB
import os
from pprint import pprint
import time
from PIL import Image, ImageTk

# 設定log
logging.basicConfig(level=logging.DEBUG)

# 獲取程式的當前路徑
current_path = os.path.dirname(os.path.realpath(__file__))

logging.debug(f"程式的當前路徑: {current_path}")
logging.debug(f"ffmpeg.exe 的路徑: {os.path.join(current_path, 'ffmpeg.exe')}")

# 指定 ffmpeg 的路徑
change_settings({"FFMPEG_BINARY": os.path.join(current_path, "ffmpeg.exe")})

# 建立視窗物件
win = ThemedTk(theme="arc")
win.title("ytPython - 開源版")
win.geometry("580x450")
win.resizable(True, True)

# 建立函式
def on_progress(video_list, chunk, bytes_remaining):
    total_size = video_list.filesize
    bytes_downloaded = total_size - bytes_remaining

    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_bar['value'] = percentage_of_completion
    win.update_idletasks()

def check_video_stat(event=None):
    if url_input.get() == "":
        messagebox.showinfo("提示", "請輸入YouTube影片網址")
        return

    global yt
    yt = YouTube(url_input.get(), on_progress_callback=on_progress)

    # 取得影片的所有格式
    global video_list
    video_list = list(yt.streams)

    # 分離視頻和音頻流，並排序
    video_video_lists = sorted([video_list for video_list in video_list if video_list.type == 'video'], key=lambda s: (s.resolution, s.fps), reverse=True)
    audio_video_lists = sorted([video_list for video_list in video_list if video_list.type == 'audio'], key=lambda s: int(s.abr[:-4]), reverse=True)
    
    global video_list2
    video_list2 = []
    for i in video_video_lists:
        if i.mime_type == "video/mp4":
            video_list2.append("影訊：" + str(i.resolution))
    for i in audio_video_lists:
        if i.mime_type == "audio/mp4":
            video_list2.append("音訊：" + str(i.abr))

    video_qlsel["values"] = video_list2
    video_path.insert(0, os.path.join(current_path, yt.title))

# 檢查 ffmpeg.exe 是否存在
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        messagebox.showinfo("提示", "請前往 https://github.com/BtbN/FFmpeg-Builds/releases 下載並安裝 ffmpeg-master-latest-win64-gpl.zip")

def sel_path():
    path_ = filedialog.asksaveasfile()
    video_path.insert(0, path_)

# 轉換影片檔案為音訊檔
def convert_video_to_audio(video_path):
    try:
        logging.debug("轉換中...")
        video = VideoFileClip(video_path)
        audio_path = video_path.replace(".mp4", ".mp3")
        video.audio.write_audiofile(audio_path)
        return audio_path
    except KeyError:
        print("指定的影片只有聲音，將直接重新命名")
        audio_path = video_path.replace(".mp4", ".mp3")
        shutil.move(video_path, audio_path)
        return audio_path
    # except Exception as e:
    #     logging.critical(e)

# 主下載程式
def download_video():
    logging.debug("下載中...")
    selected_quality = video_qlsel.get()
    selected_abr = selected_quality.split('：')[1]  # 從選擇的品質中取得音訊比特率
    for stream in video_list:
        logging.debug(f"選擇的品質: {selected_quality}, 流的解析度: {stream.resolution}, 流的音訊比特率: {stream.abr}")
        if stream.abr == selected_abr and stream.mime_type == "audio/mp4":
            logging.debug("偵測到類型為音訊...")
            audio_path = stream.download()
            logging.info(f"音訊已下載，檔案路徑: {audio_path}")
            mp3_path = convert_video_to_audio(audio_path)  # 轉換下載的 .mp4 檔案為 .mp3
            logging.info(f"檔案已轉換為 .mp3，檔案路徑: {mp3_path}")
            break
        else:
            logging.debug("無法偵測到類型...")
            # messagebox.showinfo("提示", "無法偵測到類型")

# # 主下載程式
# def download_video():
#     logging.debug("下載中...")
#     selected_quality = video_qlsel.get()
#     selected_abr = selected_quality.split('：')[1]  # 從選擇的品質中取得音訊比特率
#     for stream in video_list:
#         logging.debug(f"選擇的品質: {selected_quality}, 流的解析度: {stream.resolution}, 流的音訊比特率: {stream.abr}")
#         if stream.abr == selected_abr and stream.mime_type == "audio/mp4":
#             logging.debug("偵測到類型為音訊...")
#             audio_path = stream.download()
#             print(f"音訊已下載，檔案路徑: {audio_path}")
#             return  # 當找到匹配的流時，立即停止迴圈
#     logging.debug("無法偵測到類型...")
#     messagebox.showinfo("提示", "無法偵測到類型")

# 建立物件
# 加載圖片
logo = PhotoImage(file='logo.png')  # 請將 'logo.png' 替換為你的圖片檔案路徑

# 創建一個空的 Label
empty_label = ttk.Label(win, width=50)
empty_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')

# 獲取 Label 的寬度
win.update()  # 更新視窗以確保獲取的寬度是正確的
width = empty_label.winfo_width()

# 加載圖片
image = Image.open('logo.png')  # 請將 'logo.png' 替換為你的圖片檔案路徑

# 計算新的高度
original_width, original_height = image.size
new_height = original_height * width // original_width

# 改變圖片的大小
image = image.resize((width, new_height))

# 創建 PhotoImage 物件
logo = ImageTk.PhotoImage(image)

# 創建圖片標籤
logo_label = ttk.Label(win, image=logo)
logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

# 刪除空的 Label
empty_label.destroy()

url_input = ttk.Entry(win, width=50)
url_input.grid(row=1, column=0, padx=10, pady=10, sticky='w')
url_input.bind("<Return>", check_video_stat)

url_download = ttk.Button(win, text="查詢資料", width=20, command=check_video_stat)
url_download.grid(row=1, column=1, padx=10, pady=10, sticky='w')

video_qllbl = ttk.Label(win, text="影片類型與品質：", anchor="w", width=50, background="systembuttonface")
video_qllbl.grid(row=2, column=0, padx=10, pady=10, sticky='w')

video_qlsel = ttk.Combobox(win, width=20, state="readonly")
video_qlsel.values = ["請選擇影片品質"]
video_qlsel.grid(row=2, column=1, padx=10, pady=10, sticky='w')

video_download = ttk.Button(win, text="下載影片", width=20, command=download_video)
video_download.grid(row=3, column=0, padx=10, pady=10, sticky='w')

video_path_lbl = ttk.Label(win, text="下載路徑：", anchor="w", width=50, background="systembuttonface")
video_path_lbl.grid(row=4, column=0, padx=10, pady=10, sticky='w')

# 創建一個 Frame 物件
frame = ttk.Frame(win)
frame.grid(row=4, column=1, padx=10, pady=10, sticky='w')

# 將 video_path 和 path_button 放在同一格
video_path = ttk.Entry(frame, width=17)
video_path.pack(side='left')

path_button = ttk.Button(frame, text="...", width=3, command=sel_path)
path_button.pack(side='left')

# 建立提醒
tip = ttk.Label(win, text="此軟體會將檔案儲存到你指定的路徑，檔名預設會使用影片標題", anchor="w", width=50, background="systembuttonface")
tip.grid(row=5, column=0, padx=10, pady=10, sticky='w')

progress_bar = ttk.Progressbar(win, length=560)
progress_bar.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='w')

win.lift()
win.mainloop()