import random
import threading
import tkinter as tk
from datetime import datetime, timedelta
from queue import Queue
from time import sleep

import customtkinter as ctk
import numpy as np
import speech_recognition as sr
import torch
from .. import whisper

from .ctk_tooltip import CTkToolTip
from .ctkdropdown import CTkScrollableDropdownFrame
from .icons import icons
from .style import FONTS, DROPDOWN


class TkAudioVisualizer(tk.Frame):
    def __init__(self,
                 master: any,
                 gradient=None,
                 bar_color: str = "white",
                 bar_width: int = 7,
                 **kwargs):
        tk.Frame.__init__(self, master)
        if gradient is None:
            gradient = ["cyan", "blue"]
        self.viz = DrawBars(self, gradient[0], gradient[1], bar_width, bar_color, relief="sunken", **kwargs)
        self.viz.pack(fill="both", expand=True)

    def start(self):
        """ start the vizualizer """
        if not self.viz._running:
            self.viz._running = True
            self.viz.update()

    def stop(self):
        """ stop the visualizer """
        self.viz._running = False


class DrawBars(tk.Canvas):
    '''A gradient frame which uses a canvas to draw the background'''

    def __init__(self, parent, color1, color2, bar_width, bar_color, **kwargs):
        tk.Canvas.__init__(self, parent, bg=bar_color, bd=0, highlightthickness=0, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self._bar_width = bar_width
        self._running = False
        self.after(100, lambda: self._draw_gradient())
        self.bind("<Configure>", lambda e: self._draw_gradient() if not self._running else None)

    def _draw_gradient(self, event=None):
        '''Draw the gradient spectrum '''
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width + 10

        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(0, limit, self._bar_width):
            bar_height = random.randint(int(limit / 8), int(limit / 2.5))
            if not self._running:
                bar_height = height
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))

            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(i, 0, i, bar_height, tags=("gradient",), width=self._bar_width, fill=color)

        self.lower("gradient")

        if self._running:
            self.after(150, self._draw_gradient)

    def update(self):
        self._draw_gradient()


languages = [
    "English",
    "Chinese",
    "German",
    "Spanish",
    "Russian",
    "Korean",
    "French",
    "Japanese",
    "Portuguese",
    "Turkish",
    "Polish",
    "Catalan",
    "Dutch",
    "Arabic",
    "Swedish",
    "Italian",
    "Indonesian",
    "Hindi",
    "Finnish",
    "Vietnamese",
    "Hebrew",
    "Ukrainian",
    "Greek",
    "Malay",
    "Czech",
    "Romanian",
    "Danish",
    "Hungarian",
    "Tamil",
    "Norwegian",
    "Thai",
    "Urdu",
    "Croatian",
    "Bulgarian",
    "Lithuanian",
    "Latin",
    "Maori",
    "Malayalam",
    "Welsh",
    "Slovak",
    "Telugu",
    "Persian",
    "Latvian",
    "Bengali",
    "Serbian",
    "Azerbaijani",
    "Slovenian",
    "Kannada",
    "Estonian",
    "Macedonian",
    "Breton",
    "Basque",
    "Icelandic",
    "Armenian",
    "Nepali",
    "Mongolian",
    "Bosnian",
    "Kazakh",
    "Albanian",
    "Swahili",
    "Galician",
    "Marathi",
    "Punjabi",
    "Sinhala",
    "Khmer",
    "Shona",
    "Yoruba",
    "Somali",
    "Afrikaans",
    "Occitan",
    "Georgian",
    "Belarusian",
    "Tajik",
    "Sindhi",
    "Gujarati",
    "Amharic",
    "Yiddish",
    "Lao",
    "Uzbek",
    "Faroese",
    "Haitian creole",
    "Pashto",
    "Turkmen",
    "Nynorsk",
    "Maltese",
    "Sanskrit",
    "Luxembourgish",
    "Myanmar",
    "Tibetan",
    "Tagalog",
    "Malagasy",
    "Assamese",
    "Tatar",
    "Hawaiian",
    "Lingala",
    "Hausa",
    "Bashkir",
    "Javanese",
    "Sundanese",
]


class LiveTranscribeUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, width=620, height=720, fg_color=("#F2F0EE", "#1E1F22"), border_width=0)
        self.energy_threshold_value = None
        self.language_value = None
        self.model_size_value = None
        self.tooltip = None
        self.language_dropdown = None
        self.model_dropdown = None
        self.mic_dropdown = None
        self.mic_btn = None
        self.recording = False
        self.close_btn = None
        self.main_frame = None
        self.input_value = None
        self.text_box = None
        self.record_button = None
        self.animation_frame = None
        self.transcribe_thread = None
        self.record_thread = None
        self.paa_thread = None

        self.selected_model = "base"
        self.selected_language = "english"

        self.audio_model = whisper.load_model(self.selected_model)
        self.phrase_time = None
        self.data_queue = Queue()
        self.recorder = sr.Recognizer()
        self.transcription = ['']

        self.energy_threshold = 500
        self.recorder.energy_threshold = self.energy_threshold
        self.recorder.dynamic_energy_threshold = False

        self.source = sr.Microphone(sample_rate=16000)

        self.record_timeout = 2
        self.phrase_timeout = 3

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.ui()
        self.grid(row=0, column=0, sticky="nsew")

    def ui(self):
        title = ctk.CTkLabel(self, text=" Live Transcribe", font=FONTS["title"], image=icons["microphone"],
                             compound="left")
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.close_btn = ctk.CTkButton(self, text="", image=icons["close"], fg_color="transparent", hover=False,
                                       width=30,
                                       height=30, command=self.hide_live_transcribe_ui)
        self.close_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew", columnspan=2)
        self.main_frame.grid_columnconfigure(0, weight=1)

        models = ["Tiny", "Base", "Small", "Medium"]
        model_size_label = ctk.CTkLabel(self.main_frame, text="Model Size", font=FONTS["normal"])
        model_size_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.model_size_value = ctk.CTkOptionMenu(self.main_frame, font=FONTS["small"])
        self.model_size_value.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        self.model_dropdown = CTkScrollableDropdownFrame(self.model_size_value, values=models, **DROPDOWN,
                                                         command=self.model_option_callback)
        self.model_size_value.set(models[0])

        language_label = ctk.CTkLabel(self.main_frame, text="Language", font=FONTS["normal"])
        language_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.language_value = ctk.CTkOptionMenu(self.main_frame, font=FONTS["small"])
        self.language_value.grid(row=1, column=1, padx=20, pady=10, sticky="e")
        self.language_dropdown = CTkScrollableDropdownFrame(self.language_value, values=languages, **DROPDOWN,
                                                            command=self.language_option_callback)
        self.language_value.set(languages[0])

        energy_threshold_label = ctk.CTkLabel(self.main_frame, text="Energy Threshold", font=FONTS["normal"])
        energy_threshold_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.energy_threshold_value = ctk.CTkSlider(self.main_frame, from_=100, to=1000, number_of_steps=50,
                                                    command=self.slider_event)
        self.energy_threshold_value.grid(row=2, column=1, padx=20, pady=10, sticky="e")
        self.energy_threshold_value.set(500)
        self.tooltip = CTkToolTip(widget=self.energy_threshold_value, message="500")

        self.record_button = ctk.CTkButton(self.main_frame, text="Start Transcribing",
                                           height=35, command=self.start_callback)
        self.record_button.grid(row=3, column=0, padx=100, pady=20, columnspan=2, sticky="nsew")

        ctk.CTkLabel(self.main_frame, text="Transcribed text", font=FONTS["subtitle"]).grid(row=4, column=0, sticky="w",
                                                                                            padx=0, pady=(20, 5))

        self.text_box = ctk.CTkTextbox(self.main_frame, height=260, font=FONTS["normal"])
        self.text_box.grid(row=5, column=0, sticky="nsew", pady=(5, 20), columnspan=2)

    def start_callback(self):
        self.pause_play()

        self.record_thread = threading.Thread(target=self.start_recording)
        self.record_thread.start()

        self.paa_thread = threading.Thread(target=self.process_audio_data)
        self.paa_thread.start()

    def process_audio_data(self):
        while True:
            now = datetime.utcnow()

            if not self.data_queue.empty():
                phrase_complete = False

                if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                    phrase_complete = True

                self.phrase_time = now

                audio_data = b''.join(self.data_queue.queue)
                self.data_queue.queue.clear()

                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available(),
                                                     cancel_func=self.cancel_callback, language=self.selected_language)
                text = result['text'].strip()

                if phrase_complete:
                    self.transcription.append(text)
                else:
                    self.transcription[-1] = text

                self.update_text()

            sleep(0.25)

    def record_callback(self, _, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def start_recording(self):
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)

    def update_text(self):
        text_to_display = ' '.join(self.transcription)
        self.text_box.delete("0.0", "end")
        self.text_box.insert("0.0", text_to_display)

    def pause_play(self):
        if not self.recording:
            self.recording = True
            self.record_button.configure(text="Stop Transcribing")
        else:
            self.recording = False
            self.record_button.configure(text="Start Transcribing")

    def slider_event(self, value):
        value = int(value)
        self.energy_threshold = value
        self.recorder.energy_threshold = value
        self.tooltip.configure(message=value)

    def model_option_callback(self, value):
        value1 = str(value).lower()
        self.selected_model = value1
        self.audio_model = whisper.load_model(self.selected_model)
        self.model_size_value.set(value)

    def language_option_callback(self, value):
        value1 = str(value).lower()
        self.selected_language = value1
        self.language_value.set(value)

    def cancel_callback(self):
        pass

    def hide_live_transcribe_ui(self):
        self.destroy()
