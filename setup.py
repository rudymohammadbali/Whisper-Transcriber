import os
import subprocess
import sys
import time

try:
    import pkg_resources
except ImportError:
    if sys.platform.startswith("win"):
        subprocess.call('python -m pip install setuptools', shell=True)
    else:
        subprocess.call('python3 -m pip install setuptools', shell=True)
    import pkg_resources

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Checking the required folders
folders = ["assets", "src"]
missing_folder = []
for i in folders:
    if not os.path.exists(i):
        missing_folder.append(i)
if missing_folder:
    print("These folder(s) not available: " + str(missing_folder))
    print("Download them from the repository properly")
    sys.exit()
else:
    print("All folders available!")

# Checking required modules
required = {"Pillow==10.1.0", "sounddevice==0.4.6", "scipy==1.11.4", "deep-translator==1.11.4", "mutagen==1.47.0", "pydub==0.25.1", "tkinterdnd2==0.3.0", "numpy==1.26.2",
            "SpeechRecognition==3.10.0", "customtkinter==5.2.1", "tqdm==4.66.1", "numba==0.58.1", "tiktoken==0.5.1", "more-itertools==10.1.0", "GPUtil==1.4.0", "PyAudio==0.2.14", "packaging==23.2"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
missing_set = [*missing, ]
pytorch_win = "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
pytorch_linux = "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
pytorch_mac = "torch torchvision torchaudio"

# Download the modules if not installed
if missing:
    try:
        print("Installing modules...")
        for x in range(len(missing_set)):
            y = missing_set[x]
            if sys.platform.startswith("win"):
                subprocess.call('python -m pip install ' + y, shell=True)
            else:
                subprocess.call('python3 -m pip install ' + y, shell=True)
    except:
        print("Unable to download! \nThis are the required ones: " + str(
            required) + "\nUse 'pip install module_name' to download the modules one by one.")
        time.sleep(3)
        sys.exit()

    try:
        print("Installing Pytorch...")
        if sys.platform.startswith("win"):
            subprocess.call('python -m pip install ' + pytorch_win, shell=True)
        elif sys.platform.startswith("linux"):
            subprocess.call('python3 -m pip install ' + pytorch_linux, shell=True)
        elif sys.platform.startswith("darwin"):
            subprocess.call('python3 -m pip install ' + pytorch_mac, shell=True)
    except:
        print("Unable to download! \nThis are the required ones: " + str(required) + "\nUse 'pip/pip3 install module_name' to download the modules one by one.")
        sys.exit()
else:
    print("All required modules installed!")

# Everything done!
print("Setup Complete!")
time.sleep(5)
sys.exit()
