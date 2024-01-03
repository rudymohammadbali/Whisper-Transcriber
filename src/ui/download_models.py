import os

from .. import whisper


def download_model():
    models = whisper.available_models()
    cache_folder = os.path.join(os.path.expanduser('~'), f'.cache{os.path.sep}whisper{os.path.sep}')

    for model in models:
        print(f"Downloading {model}")
        whisper._download(url=whisper._MODELS[model], root=cache_folder, in_memory=False)


download_model()
