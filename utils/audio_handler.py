import speech_recognition as sr
import streamlit as st
from typing import Optional

class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def record_audio(self) -> Optional[str]:
        """Record audio from microphone and convert to text"""
        try:
            with sr.Microphone() as source:
                st.write("Listening... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                st.write("Processing speech...")
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    st.error("Could not understand the audio")
                    return None
                except sr.RequestError:
                    st.error("Could not request results from speech recognition service")
                    return None
        except Exception as e:
            st.error(f"Error recording audio: {str(e)}")
            return None
