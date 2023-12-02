import os
import queue
import threading
import time
import subprocess

import customtkinter as ctk
from customtkinter import filedialog as fd
from mutagen import File, MutagenError
from pydub import AudioSegment, exceptions
from tkinterdnd2 import TkinterDnD, DND_ALL
from ..whisper.utils import get_writer

from .ctkAlert import CTkAlert
from .ctkLoader import CTkLoader
from .icons import icons
from .style import FONTS
from ..logic import Transcriber


class CTk(ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class AddSubtitlesUI(CTk):
    def __init__(self, parent):
        super().__init__(master=parent, width=620, height=720, fg_color=("#F2F0EE", "#1E1F22"), border_width=0)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text=" Add Subtitles", font=FONTS["title"], image=icons["subtitle"],
                             compound="left")
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.close_btn = ctk.CTkButton(self, text="", image=icons["close"], fg_color="transparent", hover=False, width=30,
                                  height=30, command=self.hide_transcribe_ui)
        self.close_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew", columnspan=2)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.master = parent
        self.drag_drop = None
        self.audio_path = None
        self.cancel_signal = False
        self.loader = None
        self.option_menu = None
        self.process = None
        self.queue = queue.Queue()

        self.default_widget()

        self.grid(row=0, column=0, sticky="nsew")

    def default_widget(self):
        label = ctk.CTkLabel(self.main_frame, text="No File Selected", font=FONTS["subtitle_bold"])
        label.grid(row=0, column=0, padx=0, pady=(20, 5), sticky="w")

        self.drag_drop = ctk.CTkButton(self.main_frame, text="➕ \nDrag & Drop Here", width=500, height=250,
                                       text_color=("#000000", "#DFE1E5"), hover=False, fg_color="transparent",
                                       border_width=2, corner_radius=5, border_color=("#D3D5DB", "#2B2D30"),
                                       font=FONTS["normal"])
        self.drag_drop.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")

        self.drag_drop.drop_target_register(DND_ALL)
        self.drag_drop.dnd_bind('<<Drop>>', self.drop)

        label_or = ctk.CTkLabel(self.main_frame, text="Or", font=("", 14))
        label_or.grid(row=2, column=0, padx=0, pady=5, sticky="nsew")

        select_btn = ctk.CTkButton(self.main_frame, text="Browse Files", width=150, height=40,
                                   command=self.select_file_callback, font=FONTS["normal"])
        select_btn.grid(row=3, column=0, padx=200, pady=10, sticky="nsew")

        label_1 = ctk.CTkLabel(self.main_frame, text="Support Formats: MP4, MOV, WMV, AVI",
                               fg_color=("#D3D5DB", "#2B2D30"), corner_radius=5, width=400, height=50,
                               font=FONTS["small"])
        label_1.grid(row=4, column=0, padx=0, pady=20, sticky="sew")

    def task_widget(self):
        file_name, duration, file_size = self.get_audio_info(self.audio_path)

        label = ctk.CTkLabel(self.main_frame, text="Selected File", font=FONTS["subtitle_bold"])
        label.grid(row=0, column=0, padx=0, pady=(20, 5), sticky="w")

        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        label_1 = ctk.CTkLabel(frame, text="File Name", font=FONTS["normal"])
        label_1.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        label_1_value = ctk.CTkLabel(frame, text=file_name, font=FONTS["small"])
        label_1_value.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="e")

        label_2 = ctk.CTkLabel(frame, text="Duration", font=FONTS["normal"])
        label_2.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        label_2_value = ctk.CTkLabel(frame, text=duration, font=FONTS["small"])
        label_2_value.grid(row=1, column=1, padx=20, pady=5, sticky="e")

        label_3 = ctk.CTkLabel(frame, text="Size", font=FONTS["normal"])
        label_3.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="w")
        label_3_value = ctk.CTkLabel(frame, text=f"{file_size:.2f} MB", font=FONTS["small"])
        label_3_value.grid(row=2, column=1, padx=20, pady=(5, 20), sticky="e")

        start_btn = ctk.CTkButton(self.main_frame, text="Start Transcribing", height=40, command=self.start_callback,
                                  font=FONTS["normal"])
        start_btn.grid(row=2, column=0, padx=200, pady=20, sticky="nsew")

    def result_widget(self):
        result = self.queue.get()
        text = str(result["text"]).strip()

        result_label = ctk.CTkLabel(self.main_frame, text="Transcribed Text", font=FONTS["subtitle_bold"])
        result_label.grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")

        textbox = ctk.CTkTextbox(self.main_frame, width=580, height=200, border_width=2, font=FONTS["normal"])
        textbox.grid(row=1, column=0, padx=10, pady=(5, 20), sticky="nsew", columnspan=2)
        textbox.insert("0.0", text=text)

        download_label = ctk.CTkLabel(self.main_frame, text="Download Video with Subtitles", font=FONTS["subtitle_bold"])
        download_label.grid(row=2, column=0, padx=10, pady=(20, 5), sticky="w")

        download_btn = ctk.CTkButton(self.main_frame, text="Download", command=lambda: self.add_subtitle(result),
                                     font=FONTS["normal"], height=35)
        download_btn.grid(row=3, column=0, padx=10, pady=20, sticky="nsw")

    def add_subtitle(self, result):
        file_name = os.path.splitext(os.path.basename(self.audio_path))[0]

        output_video = fd.asksaveasfilename(
            parent=self,
            initialfile=f"{file_name}-subtitle",
            title="Export video with subtitle",
            defaultextension=".mp4",
            filetypes=[("Video files", "*.mp4 *.mov *.wmv *.avi")]
        )
        if output_video:
            self.close_btn.configure(state="disabled")
            widgets = self.main_frame.winfo_children()
            for widget in widgets:
                widget.destroy()

            thread = threading.Thread(target=self.subtitle_handler, args=(output_video, result))
            thread.start()

    def subtitle_handler(self, output_video, result):
        self.loader = CTkLoader(parent=self.master, title="Adding Subtitles", msg="Please wait...",
                                cancel_func=self.kill_process)
        file_name = os.path.splitext(os.path.basename(self.audio_path))[0]
        input_video = self.audio_path
        writer = get_writer("srt", ".")
        subtitle_file_path = f"{file_name}.srt"
        writer(result, input_video, {"highlight_words": True, "max_line_count": 50, "max_line_width": 3})

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i", input_video,
            "-vf", f"subtitles={subtitle_file_path}",
            output_video
        ]

        self.process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        self.process.wait()

        self.loader.hide_loader()

        if self.process.returncode == 0:
            CTkAlert(parent=self.master, status="success", title="Success",
                     msg="Subtitle added successfully.")
            self.close_btn.configure(state="normal")
            self.after(1000, self.default_widget)
        else:
            CTkAlert(parent=self.master, status="error", title="Error",
                     msg="Error adding subtitles to the video.")
            self.close_btn.configure(state="normal")
            self.result_widget()

        os.remove(subtitle_file_path)

    def kill_process(self):
        pass

    def start_callback(self):
        self.close_btn.configure(state="disabled")
        widgets = self.main_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.loader = CTkLoader(parent=self.master, title="Transcribing...", msg="Please wait...",
                                cancel_func=self.set_signal)
        thread = threading.Thread(target=self.start_transcribing, args=(self.audio_path, self.check_signal))
        thread.start()

    def start_transcribing(self, audio_path, check_signal):
        transcriber = Transcriber(audio=audio_path)
        result = transcriber.audio_recognition(cancel_func=check_signal)
        self.loader.hide_loader()
        if result:
            self.queue.put(result)
            self.close_btn.configure(state="normal")
            self.result_widget()

    def set_signal(self):
        self.cancel_signal = True

    def check_signal(self):
        original_value = self.cancel_signal

        if self.cancel_signal:
            self.cancel_signal = False
            self.close_btn.configure(state="normal")
            self.after(1000, self.default_widget)

        return original_value

    def select_file_callback(self):
        file_path = fd.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.mov *.wmv *.avi")])
        if file_path:
            audio_path = os.path.abspath(file_path)
            if self.is_streamable_audio(audio_path):
                self.audio_path = audio_path
                widgets = self.main_frame.winfo_children()

                for widget in widgets:
                    widget.destroy()
                self.after(1000, self.task_widget)
            else:
                CTkAlert(parent=self.master, status="error", title="Error",
                         msg="The chosen audio file is not valid or streamable.")

    @staticmethod
    def is_streamable_audio(audio_path):
        if not os.path.isfile(audio_path):
            return False

        try:
            audio = AudioSegment.from_file(audio_path)
            audio_info = File(audio_path)
            return len(audio) > 0 and audio_info.info.length > 0
        except (FileNotFoundError, exceptions.CouldntDecodeError, MutagenError):
            return False

    @staticmethod
    def get_audio_info(file_path):
        try:
            if not os.path.isfile(file_path):
                return None, None

            file_name = os.path.basename(file_path)

            audio_info = File(file_path)
            if audio_info is None:
                return None, None

            duration_seconds = audio_info.info.length

            duration_formatted = time.strftime("%H:%M:%S", time.gmtime(duration_seconds))

            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            return file_name, duration_formatted, file_size_mb
        except MutagenError:
            return None, None

    def drop(self, event):
        dropped_file = event.data.replace("{", "").replace("}", "")
        audio_path = os.path.abspath(dropped_file)
        if self.is_streamable_audio(audio_path):
            self.audio_path = audio_path
            widgets = self.main_frame.winfo_children()

            for widget in widgets:
                widget.destroy()

            self.after(1000, self.task_widget)
        else:
            CTkAlert(parent=self.master, status="error", title="Error",
                     msg="The chosen audio file is not valid or streamable.")

    def hide_transcribe_ui(self):
        self.destroy()
