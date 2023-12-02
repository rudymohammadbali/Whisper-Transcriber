import os

import customtkinter as ctk
from PIL import Image

current_path = os.path.dirname(os.path.realpath(__file__))

icons = {
    "close": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\close_dark.png"),
                          light_image=Image.open(f"{current_path}\\icons\\close_light.png"), size=(30, 30)),
    "audio_file": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\audio_file_dark.png"),
                               light_image=Image.open(f"{current_path}\\icons\\audio_file_light.png"), size=(30, 30)),
    "translate": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\translation_dark.png"),
                              light_image=Image.open(f"{current_path}\\icons\\translate_light.png"), size=(30, 30)),
    "microphone": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\microphone_dark.png"),
                               light_image=Image.open(f"{current_path}\\icons\\microphone_light.png"), size=(30, 30)),
    "subtitle": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\subtitles_dark.png"),
                             light_image=Image.open(f"{current_path}\\icons\\subtitle_light.png"), size=(30, 30)),
    "settings": ctk.CTkImage(dark_image=Image.open(f"{current_path}\\icons\\settings_dark.png"),
                             light_image=Image.open(f"{current_path}\\icons\\settings_light.png"), size=(30, 30))
}
