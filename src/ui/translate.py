import os
import queue
import threading
import time

import customtkinter as ctk
from customtkinter import filedialog as fd
from mutagen import File, MutagenError
from pydub import AudioSegment, exceptions
from tkinterdnd2 import TkinterDnD, DND_ALL

from .ctkAlert import CTkAlert
from .ctkLoader import CTkLoader
from .ctkdropdown import CTkScrollableDropdownFrame
from .icons import icons
from .style import FONTS, DROPDOWN
from ..logic import Transcriber


class CTk(ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


languages = ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'assamese', 'aymara', 'azerbaijani',
             'bambara', 'basque', 'belarusian', 'bengali', 'bhojpuri', 'bosnian', 'bulgarian', 'catalan',
             'cebuano', 'chichewa', 'chinese (simplified)', 'chinese (traditional)', 'corsican', 'croatian',
             'czech', 'danish', 'dhivehi', 'dogri', 'dutch', 'english', 'esperanto', 'estonian', 'ewe',
             'filipino', 'finnish', 'french', 'frisian', 'galician', 'georgian', 'german', 'greek', 'guarani',
             'gujarati', 'haitian creole', 'hausa', 'hawaiian', 'hebrew', 'hindi', 'hmong', 'hungarian',
             'icelandic', 'igbo', 'ilocano', 'indonesian', 'irish', 'italian', 'japanese', 'javanese',
             'kannada', 'kazakh', 'khmer', 'kinyarwanda', 'konkani', 'korean', 'krio', 'kurdish (kurmanji)',
             'kurdish (sorani)', 'kyrgyz', 'lao', 'latin', 'latvian', 'lingala', 'lithuanian', 'luganda',
             'luxembourgish', 'macedonian', 'maithili', 'malagasy', 'malay', 'malayalam', 'maltese', 'maori',
             'marathi', 'meiteilon (manipuri)', 'mizo', 'mongolian', 'myanmar', 'nepali', 'norwegian',
             'odia (oriya)', 'oromo', 'pashto', 'persian', 'polish', 'portuguese', 'punjabi', 'quechua',
             'romanian', 'russian', 'samoan', 'sanskrit', 'scots gaelic', 'sepedi', 'serbian', 'sesotho',
             'shona', 'sindhi', 'sinhala', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili',
             'swedish', 'tajik', 'tamil', 'tatar', 'telugu', 'thai', 'tigrinya', 'tsonga', 'turkish', 'turkmen',
             'twi', 'ukrainian', 'urdu', 'uyghur', 'uzbek', 'vietnamese', 'welsh', 'xhosa', 'yiddish', 'yoruba',
             'zulu']


class TranslateUI(CTk):
    def __init__(self, parent):
        super().__init__(master=parent, width=620, height=720, fg_color=("#F2F0EE", "#1E1F22"), border_width=0)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text=" Translate Audio", font=FONTS["title"], image=icons["translate"],
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
        self.lang_dropdown = None
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

        label_1 = ctk.CTkLabel(self.main_frame, text="Support Formats: WAV, MP3, OGG, FLAC, MP4, MOV, WMV, AVI",
                               fg_color=("#D3D5DB", "#2B2D30"), corner_radius=5, width=400, height=50,
                               font=FONTS["small"])
        label_1.grid(row=4, column=0, padx=0, pady=20, sticky="sew")

    def task_widget(self):
        file_name, duration, file_size = self.get_audio_info(self.audio_path)

        label = ctk.CTkLabel(self.main_frame, text="Selected File", font=FONTS["subtitle_bold"])
        label.grid(row=0, column=0, padx=0, pady=(20, 5), sticky="w")

        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew", columnspan=2)
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

        translate_to = ctk.CTkLabel(self.main_frame, text="Translate To", font=FONTS["normal"])
        translate_to.grid(row=2, column=0, padx=40, pady=20, sticky="w")
        self.lang_dropdown = ctk.CTkOptionMenu(self.main_frame, font=FONTS["small"])
        self.lang_dropdown.grid(row=2, column=1, padx=40, pady=20, sticky="e")
        CTkScrollableDropdownFrame(self.lang_dropdown, values=languages, **DROPDOWN)
        self.lang_dropdown.set(languages[0])

        start_btn = ctk.CTkButton(self.main_frame, text="Start Translating", height=40, command=self.start_callback,
                                  font=FONTS["normal"])
        start_btn.grid(row=3, column=0, padx=200, pady=40, sticky="nsew", columnspan=2)

    def result_widget(self):
        result = self.queue.get()

        result_label = ctk.CTkLabel(self.main_frame, text="Translated Text", font=FONTS["subtitle_bold"])
        result_label.grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")

        textbox = ctk.CTkTextbox(self.main_frame, width=580, height=200, border_width=2, font=FONTS["normal"])
        textbox.grid(row=1, column=0, padx=10, pady=(5, 20), sticky="nsew", columnspan=2)
        textbox.insert("0.0", text=result)

        download_label = ctk.CTkLabel(self.main_frame, text="Download Text", font=FONTS["subtitle_bold"])
        download_label.grid(row=2, column=0, padx=10, pady=(20, 5), sticky="w")

        download_btn = ctk.CTkButton(self.main_frame, text="Download", command=lambda: self.save_text(result),
                                     font=FONTS["normal"], height=35)
        download_btn.grid(row=3, column=0, padx=10, pady=20, sticky="nsw")

    def save_text(self, result):
        file_name = os.path.basename(self.audio_path)
        sep = "."
        file_name = file_name.split(sep, 1)[0]

        file_path = fd.asksaveasfilename(
            parent=self,
            initialfile=file_name,
            title="Export text",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if file_path:
            with open(file_path, 'w', encoding="utf-8") as file:
                file.write(result)

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
        language = self.lang_dropdown.get()
        transcriber = Transcriber(audio=audio_path)
        result = transcriber.translate_audio(cancel_func=check_signal, to_language=language)
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
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.flac"), ("Video files", "*.mp4 *.mov *.wmv *.avi")])
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
