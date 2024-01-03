import os

import customtkinter as ctk
from PIL import Image

current_path = os.path.dirname(os.path.realpath(__file__))
icon_path = f"{current_path}{os.path.sep}icons{os.path.sep}"

icons = {
    "close": ctk.CTkImage(dark_image=Image.open(f"{icon_path}close_dark.png"),
                          light_image=Image.open(f"{icon_path}close_light.png"), size=(30, 30)),
    "audio_file": ctk.CTkImage(dark_image=Image.open(f"{icon_path}audio_file_dark.png"),
                               light_image=Image.open(f"{icon_path}audio_file_light.png"), size=(30, 30)),
    "translate": ctk.CTkImage(dark_image=Image.open(f"{icon_path}translation_dark.png"),
                              light_image=Image.open(f"{icon_path}translate_light.png"), size=(30, 30)),
    "microphone": ctk.CTkImage(dark_image=Image.open(f"{icon_path}microphone_dark.png"),
                               light_image=Image.open(f"{icon_path}microphone_light.png"), size=(30, 30)),
    "subtitle": ctk.CTkImage(dark_image=Image.open(f"{icon_path}subtitles_dark.png"),
                             light_image=Image.open(f"{icon_path}subtitle_light.png"), size=(30, 30)),
    "settings": ctk.CTkImage(dark_image=Image.open(f"{icon_path}settings_dark.png"),
                             light_image=Image.open(f"{icon_path}settings_light.png"), size=(30, 30))
}
