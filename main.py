import os
import webbrowser

import customtkinter as ctk
from PIL import Image

from src.logic.settings import SettingsHandler
from src.ui.add_subtitles import AddSubtitlesUI
from src.ui.live_transcribe import LiveTranscribeUI
from src.ui.settings import SettingsUI
from src.ui.style import FONTS
from src.ui.transcribe import TranscribeUI
from src.ui.translate import TranslateUI

current_path = os.path.dirname(os.path.realpath(__file__))

icons = {
    "logo": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\logo.png"),
                         light_image=Image.open(f"{current_path}\\assets\\icons\\logo.png"), size=(50, 50)),
    "close": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\close_dark.png"),
                          light_image=Image.open(f"{current_path}\\assets\\icons\\close_light.png"), size=(30, 30)),
    "audio_file": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\audio_file_dark.png"),
                               light_image=Image.open(f"{current_path}\\assets\\icons\\audio_file_light.png"),
                               size=(30, 30)),
    "translation": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\translation_dark.png"),
                                light_image=Image.open(f"{current_path}\\assets\\icons\\translation_light.png"),
                                size=(30, 30)),
    "microphone": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\microphone_dark.png"),
                               light_image=Image.open(f"{current_path}\\assets\\icons\\microphone_light.png"),
                               size=(30, 30)),
    "subtitles": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\subtitles_dark.png"),
                              light_image=Image.open(f"{current_path}\\assets\\icons\\subtitles_light.png"),
                              size=(30, 30)),
    "paypal": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\paypal_dark.png"),
                           light_image=Image.open(f"{current_path}\\assets\\icons\\paypal_light.png"), size=(30, 30)),
    "settings": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\settings_dark.png"),
                             light_image=Image.open(f"{current_path}\\assets\\icons\\settings_light.png"),
                             size=(30, 30)),
    "help": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\help_dark.png"),
                         light_image=Image.open(f"{current_path}\\assets\\icons\\help_light.png"), size=(30, 30)),
    "github": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\assets\\icons\\github_dark.png"),
                           light_image=Image.open(f"{current_path}\\assets\\icons\\github_light.png"), size=(30, 30))
}

logo = f"{current_path}\\assets\\icons\\logo.ico"

btn = {
    "width": 280,
    "height": 116,
    "text_color": ("#FFFFFF", "#DFE1E5"),
    "compound": "left",
    "font": ("Inter", 16)
}

secondary_btn = {
    "width": 280,
    "height": 100,
    "fg_color": ("#221D21", "#2B2D30"),
    "hover": False,
    "border_width": 0,
    "text_color": ("#FFFFFF", "#DFE1E5"),
    "compound": "left",
    "font": ("Inter", 16)
}

link_btn = {
    "width": 140,
    "height": 80,
    "fg_color": "transparent",
    "hover_color": ("#D3D5DB", "#2B2D30"),
    "border_color": ("#D3D5DB", "#2B2D30"),
    "border_width": 2,
    "text_color": ("#000000", "#DFE1E5"),
    "compound": "left",
    "font": ("Inter", 16)
}


def help_link():
    webbrowser.open("https://github.com/iamironman0/Whisper-Transcriber/discussions/categories/q-a")


def github_link():
    webbrowser.open("https://github.com/iamironman0")


def paypal_link():
    webbrowser.open("https://www.paypal.com/paypalme/iamironman0")


class Testing(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("620x720")
        self.resizable(False, False)
        self.iconbitmap(logo)
        self.title("Whisper Transcriber")

        settings_handler = SettingsHandler()
        settings = settings_handler.load_settings()
        theme = settings.get("theme")
        color_theme = settings.get("color_theme")

        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme(color_theme)

        self.main_ui()

    def main_ui(self):
        title = ctk.CTkLabel(self, text="Welcome to Whisper Transcriber", text_color=("#000000", "#DFE1E5"),
                             font=FONTS["title_bold"], image=icons["logo"], compound="top")
        title.grid(row=0, column=0, padx=20, pady=20, sticky="nsew", columnspan=2)

        label = ctk.CTkLabel(self, text="Select a Service", text_color=("#000000", "#DFE1E5"), font=FONTS["subtitle"])
        label.grid(row=1, column=0, padx=20, pady=20, sticky="w")

        btn_1 = ctk.CTkButton(self, text="Transcribe Audio", **btn, image=icons["audio_file"],
                              command=lambda: TranscribeUI(parent=self))
        btn_1.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")
        btn_2 = ctk.CTkButton(self, text="Translate Audio", **btn, image=icons["translation"],
                              command=lambda: TranslateUI(parent=self))
        btn_2.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="nsew")

        btn_3 = ctk.CTkButton(self, text="Live Transcriber", **btn, image=icons["microphone"],
                              command=lambda: LiveTranscribeUI(parent=self))
        btn_3.grid(row=3, column=0, padx=(20, 10), pady=10, sticky="nsew")
        btn_4 = ctk.CTkButton(self, text="Add Subtitle", **btn, image=icons["subtitles"],
                              command=lambda: AddSubtitlesUI(parent=self))
        btn_4.grid(row=3, column=1, padx=(10, 20), pady=10, sticky="nsew")

        btn_5 = ctk.CTkButton(self, text="Settings", font=("Inter", 16), text_color=("#FFFFFF", "#DFE1E5"), width=280,
                              height=100, image=icons["settings"], command=lambda: SettingsUI(parent=self))
        btn_5.grid(row=4, column=0, padx=(20, 10), pady=20, sticky="nsew")
        btn_6 = ctk.CTkButton(self, text="Support on PayPal", **secondary_btn, image=icons["paypal"],
                              command=paypal_link)
        btn_6.grid(row=4, column=1, padx=(10, 20), pady=20, sticky="nsew")

        btn_7 = ctk.CTkButton(self, text="Github", **link_btn, image=icons["github"], command=github_link)
        btn_7.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        btn_8 = ctk.CTkButton(self, text="Help", **link_btn, image=icons["help"], command=help_link)
        btn_8.grid(row=5, column=1, padx=20, pady=20, sticky="nsew")


app = Testing()
app.mainloop()
