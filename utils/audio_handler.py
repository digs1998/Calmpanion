import whisper
import sounddevice as sd
import torch
import numpy as np
import tempfile
import streamlit as st
import wave

class AudioHandler:
    def __init__(self, model_size: str = "base"):
        """Initialize Whisper ASR model"""
        self.model = whisper.load_model(model_size)

    def record_audio(self, duration=5, samplerate=16000) -> str:
        """Records audio and saves it as a .wav file"""
        print("🎙️ Recording... Speak now!")

        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.float32)
        sd.wait()

        # Convert float32 to int16 (Whisper expects 16-bit PCM)
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Save as a temporary .wav file
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        with wave.open(temp_audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(samplerate)
            wf.writeframes(audio_int16.tobytes())

        return temp_audio_path  # Return the file path

    def transcribe(self, audio_file: str = None) -> str:
        """Transcribe an existing audio file, or record a new one if not provided"""
        if audio_file is None:
            audio_file = self.record_audio()  # Record new audio if no file is provided

        try:
            result = self.model.transcribe(audio_file, fp16=torch.cuda.is_available())  # Use fp16 if GPU is available
            return result["text"]
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
