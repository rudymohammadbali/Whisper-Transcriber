import os
import json


DEFAULT_CONFIG = {
    "theme": "system",
    "color_theme": "blue",
    "model_size": "base",
    "language": "auto detection",
    "device": "cpu"
}


class SettingsHandler:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '..', '..', 'assets\\config')
        self.config_path = os.path.normpath(file_path)
        self.settings_file_path = os.path.join(self.config_path, "settings.json")

    def save_settings(self, **new_settings: dict):
        try:
            existing_settings = self.load_settings()
            existing_settings.update(new_settings)
            if not os.path.exists(self.config_path):
                os.mkdir(self.config_path)

            with open(self.settings_file_path, 'w') as file:
                json.dump(existing_settings, file)
            return "Your settings have been saved successfully."
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file_path) and os.path.getsize(self.settings_file_path) > 0:
                with open(self.settings_file_path, "r") as file:
                    loaded_settings = json.load(file)
                return loaded_settings
            else:
                with open(self.settings_file_path, 'w') as file:
                    json.dump(DEFAULT_CONFIG, file)
                return DEFAULT_CONFIG
        except FileNotFoundError:
            return DEFAULT_CONFIG

    def reset_settings(self):
        try:
            if not os.path.exists(self.config_path):
                os.mkdir(self.config_path)

            with open(self.settings_file_path, 'w') as file:
                json.dump(DEFAULT_CONFIG, file)
            return "Your settings have been reset to default values."
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
