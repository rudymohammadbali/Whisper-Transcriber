import json
import os

from .gpu_details import GPUInfo

MODEL_SETTINGS = {
    "models": ["Tiny", "Base", "Small", "Medium", "Large", "Large-v1", "Large-v2", "Large-v3"],
    "device": ["GPU", "CPU"]
}


class ModelRequirements:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '..', '..', f'assets{os.path.sep}config')
        config_path = os.path.normpath(file_path)
        self.filename = os.path.join(config_path, "recommended_models.json")

    @staticmethod
    def model_requirements(available_memory, required_memory):
        recommended_models = [model for model, memory in required_memory.items() if available_memory >= memory]
        return recommended_models

    def read_json_file(self):
        try:
            with open(self.filename, 'r') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            with open(self.filename, 'w') as json_file:
                json.dump(MODEL_SETTINGS, json_file, indent=2)
            return MODEL_SETTINGS

    def write_json_file(self, data):
        with open(self.filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    def update_model_requirements(self):
        gpu_monitor = GPUInfo()
        gpu_info = gpu_monitor.load_gpu_info()
        available_memory = gpu_info["total_memory"]
        cuda = gpu_info["cuda_available"]

        required_memory = {
            "Tiny": 1,
            "Base": 1,
            "Small": 2,
            "Medium": 5,
            "Large": 10,
            "Large-v1": 10,
            "Large-v2": 10,
            "Large-v3": 10
        }

        json_data = self.read_json_file()

        if json_data:
            if cuda:
                device = ["CPU", "GPU"]
                recommended_models = self.model_requirements(available_memory, required_memory)
                json_data["models"] = recommended_models
                json_data["device"] = device
            else:
                recommended_models = ["Tiny", "Base", "Small", "Medium", "Large", "Large-v1", "Large-v2", "Large-v3"]
                device = ["CPU"]
                json_data["models"] = recommended_models
                json_data["device"] = device

            self.write_json_file(json_data)
            return recommended_models, device
