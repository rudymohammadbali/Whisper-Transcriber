from .. import whisper

from .settings import SettingsHandler
from deep_translator import GoogleTranslator


class Transcriber:
    def __init__(self, audio: str):
        self.audio = audio
        get_config = SettingsHandler()
        config = get_config.load_settings()

        model = config.get("model_size", "base").lower()
        self.language = config.get("language", "auto detect").lower()
        device = config.get("device", "cpu").lower()
        self.fp16 = False

        if self.language == "english" and model not in ["large", "large-v1", "large-v2"]:
            model += ".en"

        if device == "gpu":
            device = "cuda"
            self.fp16 = True

        self.load_model = whisper.load_model(name=model, device=device)

        self.options = {
            "task": "transcribe",
            "fp16": self.fp16
        }

    def audio_recognition(self, cancel_func=any):
        print("Audio Recognition started...")
        if self.language == "auto detection":
            audio = whisper.load_audio(self.audio)
            audio = whisper.pad_or_trim(audio)

            mel = whisper.log_mel_spectrogram(audio).to(self.load_model.device)

            _, probs = self.load_model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            result = whisper.transcribe(model=self.load_model, audio=self.audio,
                                        language=detected_language, **self.options, cancel_func=cancel_func)
        else:
            result = whisper.transcribe(model=self.load_model, audio=self.audio,
                                        **self.options, language=self.language, cancel_func=cancel_func)

        return result

    def translate_audio(self, cancel_func, to_language):
        print("Audio Translate started...")
        result = self.audio_recognition(cancel_func=cancel_func)
        text = str(result["text"]).strip()
        language = to_language
        translated_text = GoogleTranslator(source='auto', target=language).translate(text=text)
        # langs_list = GoogleTranslator().get_supported_languages()
        return translated_text
