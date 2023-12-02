import os
import subprocess
import sys
import threading
import webbrowser

import customtkinter as ctk

from .ctkAlert import CTkAlert
from .ctkLoader import CTkLoader
from .ctkdropdown import CTkScrollableDropdownFrame
from .icons import icons
from .style import FONTS, DROPDOWN
from ..logic import GPUInfo, SettingsHandler, ModelRequirements

current_path = os.path.dirname(os.path.realpath(__file__))

languages = [
    "Auto Detection",
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


def help_link():
    webbrowser.open("https://github.com/iamironman0/Whisper-Transcriber/discussions/categories/q-a")


class SettingsUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, width=620, height=720, fg_color=("#F2F0EE", "#1E1F22"), border_width=0)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.master = parent
        self.settings_handler = SettingsHandler()

        self.theme_btn = None
        self.color_theme_btn = None
        self.device_dropdown = None
        self.language_dropdown = None
        self.model_dropdown = None
        self.theme_dropdown = None
        self.color_theme_dropdown = None
        self.general_frame = None
        self.model_frame = None
        self.gpu_frame = None
        self.reset_btn = None
        self.mic_dropdown = None
        self.mic_btn = None

        self.loader = None
        self.process = None
        self.thread = None

        title = ctk.CTkLabel(self, text=" Settings", font=FONTS["title"], image=icons["settings"], compound="left")
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.close_btn = ctk.CTkButton(self, text="", image=icons["close"], fg_color="transparent", hover=False,
                                       width=30,
                                       height=30, command=self.hide_settings_ui)
        self.close_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew", columnspan=2)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.default_widget()

        self.reset_btn = ctk.CTkButton(self, text="Reset", height=35, command=self.reset_callback, font=FONTS["normal"])
        self.reset_btn.grid(row=3, column=0, padx=20, pady=0, sticky="w")

        self.grid(row=0, column=0, sticky="nsew")

    def default_widget(self):
        segmented_button = ctk.CTkSegmentedButton(self.main_frame, values=["General", "Model Settings", "GPU Info"],
                                                  width=150,
                                                  height=35, command=self.update_view, border_width=0,
                                                  font=FONTS["normal"])
        segmented_button.grid(row=0, column=0, padx=0, pady=20, sticky="nsew", columnspan=3)
        segmented_button.set("General")

        self.general_frame = ctk.CTkFrame(self.main_frame)
        self.general_frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew", columnspan=2)
        self.general_frame.grid_columnconfigure(0, weight=1)
        self.general_widget()

    def update_view(self, frame):
        try:
            self.general_frame.grid_forget()
            self.model_frame.grid_forget()
            self.gpu_frame.grid_forget()
        except AttributeError:
            pass

        if frame == "General":
            self.general_frame = ctk.CTkFrame(self.main_frame)
            self.general_frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew", columnspan=2)
            self.general_frame.grid_columnconfigure(0, weight=1)
            self.general_widget()

        elif frame == "Model Settings":
            self.model_frame = ctk.CTkFrame(self.main_frame)
            self.model_frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew", columnspan=2)
            self.model_frame.grid_columnconfigure(0, weight=1)
            self.model_frame.grid_columnconfigure(1, weight=1)
            self.model_widget()

        elif frame == "GPU Info":
            self.gpu_frame = ctk.CTkFrame(self.main_frame)
            self.gpu_frame.grid(row=1, column=0, padx=0, pady=20, sticky="nsew", columnspan=2)
            self.gpu_frame.grid_columnconfigure(0, weight=1)
            self.gpu_widget()

    def gpu_widget(self):
        get_info = GPUInfo()
        info = get_info.load_gpu_info()
        cuda_available = info.get("cuda_available", "N/A")
        if cuda_available:
            cuda_available = "True"
        else:
            cuda_available = "False"

        label_1 = ctk.CTkLabel(self.gpu_frame, text="CUDA Available", font=FONTS["normal"])
        label_1.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        label_1_value = ctk.CTkLabel(self.gpu_frame, text=cuda_available, font=FONTS["small"])
        label_1_value.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        label_2 = ctk.CTkLabel(self.gpu_frame, text="GPU Count", font=FONTS["normal"])
        label_2.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        label_2_value = ctk.CTkLabel(self.gpu_frame, text=info.get("gpu_count", "N/A"), font=FONTS["small"])
        label_2_value.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        label_3 = ctk.CTkLabel(self.gpu_frame, text="Current GPU", font=FONTS["normal"])
        label_3.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        label_3_value = ctk.CTkLabel(self.gpu_frame, text=info.get("current_gpu", "N/A"), font=FONTS["small"])
        label_3_value.grid(row=2, column=1, padx=20, pady=10, sticky="e")

        label_4 = ctk.CTkLabel(self.gpu_frame, text="GPU Name", font=FONTS["normal"])
        label_4.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        label_4_value = ctk.CTkLabel(self.gpu_frame, text=info.get("gpu_name", "N/A"), font=FONTS["small"])
        label_4_value.grid(row=3, column=1, padx=20, pady=10, sticky="e")

        label_5 = ctk.CTkLabel(self.gpu_frame, text="Total Memory", font=FONTS["normal"])
        label_5.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="w")
        label_5_value = ctk.CTkLabel(self.gpu_frame, text=f"{info.get('total_memory', 'N/A')} GB", font=FONTS["small"])
        label_5_value.grid(row=4, column=1, padx=20, pady=(10, 20), sticky="e")

    def model_widget(self):
        settings = self.settings_handler.load_settings()

        model_size = settings.get("model_size", "Base").capitalize()
        language = settings.get("language", "Auto Detection").capitalize()
        device = settings.get("device", "CPU").upper()

        model_requirements = ModelRequirements()
        model_values, device_values = model_requirements.update_model_requirements()
        model_size_label = ctk.CTkLabel(self.model_frame, text="Model Size", font=FONTS["normal"])
        model_size_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        model_size_value = ctk.CTkOptionMenu(self.model_frame, font=FONTS["small"])
        model_size_value.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        self.model_dropdown = CTkScrollableDropdownFrame(model_size_value, values=model_values, **DROPDOWN,
                                                         command=lambda
                                                             new_value=model_size_value: self.change_settings_value(
                                                             key_name="model_size", new_value=f"{new_value}"))
        model_size_value.set(model_size)

        language_label = ctk.CTkLabel(self.model_frame, text="Language", font=FONTS["normal"])
        language_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        language_value = ctk.CTkOptionMenu(self.model_frame, font=FONTS["small"])
        language_value.grid(row=1, column=1, padx=20, pady=10, sticky="e")
        self.language_dropdown = CTkScrollableDropdownFrame(language_value, values=languages, **DROPDOWN,
                                                            command=lambda
                                                                new_value=language_value: self.change_settings_value(
                                                                key_name="language", new_value=f"{new_value}"))
        language_value.set(language)

        device_label = ctk.CTkLabel(self.model_frame, text="Device", font=FONTS["normal"])
        device_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        device_value = ctk.CTkOptionMenu(self.model_frame, font=FONTS["small"])
        device_value.grid(row=2, column=1, padx=20, pady=10, sticky="e")
        self.device_dropdown = CTkScrollableDropdownFrame(device_value, values=device_values, **DROPDOWN,
                                                          command=lambda
                                                              new_value=device_value: self.change_settings_value(
                                                              key_name="device", new_value=f"{new_value}"))
        device_value.set(device)

        download_btn = ctk.CTkButton(self.model_frame, text="Download All Models", command=self.download_callback,
                                     height=50, font=FONTS["small"])
        download_btn.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="e")

        btns_frame = ctk.CTkScrollableFrame(self.model_frame, fg_color="transparent", label_text="Installed Models",
                                            label_font=FONTS["normal"])
        btns_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

        installed_models = []

        cache_folder = os.path.join(os.path.expanduser('~'), '.cache\\whisper\\')
        files = os.listdir(cache_folder)
        for file in files:
            name, extension = os.path.splitext(file)

            installed_models.append(name)

        if installed_models:
            for index, model in enumerate(installed_models):
                model_btn = ctk.CTkButton(btns_frame, text=str(model).capitalize(), height=25, hover=False,
                                          corner_radius=2, font=FONTS["small"])
                model_btn.grid(row=index, column=0, padx=20, pady=5, sticky="nsew")
        else:
            warning_btn = ctk.CTkButton(btns_frame, text="No models are installed", height=25, hover=False,
                                        corner_radius=2, font=FONTS["small"])
            warning_btn.grid(row=0, column=0, padx=20, pady=5, sticky="nsew")

    def general_widget(self):
        settings = self.settings_handler.load_settings()
        theme = settings.get("theme", "System").capitalize()
        color_theme = settings.get("color_theme", "Blue").capitalize()

        theme_label = ctk.CTkLabel(self.general_frame, text="Theme", font=FONTS["normal"])
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.theme_btn = ctk.CTkOptionMenu(self.general_frame, font=FONTS["small"])
        values = ["System", "Light", "Dark"]
        self.theme_btn.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")
        self.theme_dropdown = CTkScrollableDropdownFrame(self.theme_btn, values=values, **DROPDOWN,
                                                         command=self.change_theme)
        self.theme_btn.set(theme)

        color_theme_label = ctk.CTkLabel(self.general_frame, text="Color Theme", font=FONTS["normal"])
        color_theme_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")
        self.color_theme_btn = ctk.CTkOptionMenu(self.general_frame, font=FONTS["small"])
        color_values = ["Blue", "Dark-Blue", "Green"]
        self.color_theme_btn.grid(row=1, column=1, padx=20, pady=(20, 10), sticky="e")
        self.color_theme_dropdown = CTkScrollableDropdownFrame(self.color_theme_btn, values=color_values,
                                                               **DROPDOWN,
                                                               command=self.change_color_theme)
        self.color_theme_btn.set(color_theme)

        developer_label = ctk.CTkLabel(self.general_frame, text="Developer", font=FONTS["normal"])
        developer_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        developer_value = ctk.CTkLabel(self.general_frame, text="@iamironman", font=FONTS["small"])
        developer_value.grid(row=2, column=1, padx=20, pady=10, sticky="e")

        released_label = ctk.CTkLabel(self.general_frame, text="Released", font=FONTS["normal"])
        released_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        released_value = ctk.CTkLabel(self.general_frame, text="12/2/2023", font=FONTS["small"])
        released_value.grid(row=3, column=1, padx=20, pady=10, sticky="e")

        help_label = ctk.CTkLabel(self.general_frame, text="FAQ or Help Center", font=FONTS["normal"])
        help_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        help_value = ctk.CTkButton(self.general_frame, text="Get help", font=FONTS["small"], command=help_link)
        help_value.grid(row=4, column=1, padx=20, pady=10, sticky="e")

    def download_callback(self):
        self.close_btn.configure(state="disabled")
        self.reset_btn.destroy()
        widgets = self.main_frame.winfo_children()

        for widget in widgets:
            widget.grid_forget()

        self.loader = CTkLoader(parent=self.master, title="Downloading Models", msg="Please wait...",
                                cancel_func=self.cancel_downloads)

        self.thread = threading.Thread(target=self.download_thread)
        self.thread.start()

    def download_thread(self):
        interpreter_path = sys.executable
        script_path = f"{current_path}\\download_models.py"

        command = [interpreter_path, script_path]
        self.process = subprocess.Popen(command)

        return_code = self.process.wait()
        if return_code == 0:
            CTkAlert(parent=self.master, status="success", title="Download Complete",
                     msg="All available models are installed successfully.")
            self.cancel_downloads()
        else:
            CTkAlert(parent=self.master, status="error", title="Download Failed",
                     msg="Failed to download models. Please check your internet connection and try again.")

        self.cancel_downloads()

    def cancel_downloads(self):
        self.loader.hide_loader()
        self.process.terminate()
        self.close_btn.configure(state="normal")
        self.main_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew", columnspan=2)
        self.after(1000, self.default_widget)

    def reset_callback(self):
        message = self.settings_handler.reset_settings()
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

        self.default_widget()

        CTkAlert(parent=self.master, status="success", title="Success", msg=message)

    def change_settings_value(self, key_name: str, new_value: str):
        self.settings_handler.save_settings(**{f"{key_name}": f"{new_value.lower()}"})
        for widget in self.model_frame.winfo_children():
            widget.grid_forget()

        self.update_view(frame="Model Settings")

    def change_theme(self, theme):
        new_theme = str(theme).lower()
        ctk.set_appearance_mode(new_theme)
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

        self.settings_handler.save_settings(**{"theme": f"{new_theme}"})

        self.default_widget()

    def change_color_theme(self, color_theme):
        new_color_theme = str(color_theme).lower()
        ctk.set_default_color_theme(new_color_theme)

        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

        self.settings_handler.save_settings(**{"color_theme": f"{new_color_theme}"})

        self.default_widget()

    def hide_settings_ui(self):
        self.destroy()
