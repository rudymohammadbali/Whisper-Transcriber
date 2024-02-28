import json
import os

import GPUtil
import torch


class GPUInfo:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cuda_available = torch.cuda.is_available()
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '..', '..', f"assets{os.path.sep}config")
        self.config_path = os.path.normpath(file_path)
        self.gpu_info_file_path = os.path.join(self.config_path, "gpu_info.json")

    def get_gpu_info(self):
        if self.cuda_available:
            gpu_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_device)
            total_memory = round(torch.cuda.get_device_properties(current_device).total_memory / (1024 ** 3))
        else:
            gpus = GPUtil.getGPUs()
            gpu_count = len(gpus)

            if gpu_count == 0:
                current_device = "No GPU found."
                gpu_name = "N/A"
                total_memory = 0
            else:
                current_gpu = gpus[0]
                current_device = f"{current_gpu.name} ({current_gpu.id})"
                gpu_name = current_gpu.name
                total_memory = current_gpu.memoryTotal / 1024

        return {"cuda_available": self.cuda_available,
                "gpu_count"     : gpu_count,
                "current_gpu"   : current_device,
                "gpu_name"      : gpu_name,
                "total_memory"  : total_memory}

    def save_gpu_info(self):
        settings = self.get_gpu_info()

        try:
            if not os.path.exists(self.config_path):
                os.mkdir(self.config_path)

            with open(self.gpu_info_file_path, 'w') as file: json.dump(settings, file)
        except FileNotFoundError or PermissionError:
            pass

    def load_gpu_info(self):
        if not os.path.exists(self.gpu_info_file_path) or os.path.getsize(self.gpu_info_file_path) == 0:
            self.save_gpu_info()
        try:
            with open(self.gpu_info_file_path, 'r') as file: loaded_settings = json.load(file)
        except FileNotFoundError:
            self.save_gpu_info()
            with open(self.gpu_info_file_path, 'r') as file: loaded_settings = json.load(file)
        return loaded_settings
