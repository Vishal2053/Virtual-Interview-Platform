# speech_service.py
import os
import logging
import base64
import requests
import io
import soundfile as sf
import speech_recognition as sr
from typing import Optional
from dotenv import load_dotenv
from pydub import AudioSegment
import io
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from gtts import gTTS
import base64
import io

def text_to_speech(text: str) -> str:
    try:
        tts = gTTS(text=text, lang='en')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        audio_base64 = base64.b64encode(audio_io.read()).decode("utf-8")
        return audio_base64
    except Exception as e:
        logger.error(f"gTTS Error: {str(e)}")
        return ""



def transcribe_audio(audio_file) -> Optional[str]:
    """
    Transcribe WebM audio using Google Speech Recognition.
    """
    logger.debug("Transcribing audio with Google Speech Recognition...")

    try:
        # Read uploaded WebM file and convert to WAV using pydub
        audio_bytes = audio_file.read()
        webm_audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

        # Export to WAV format in memory
        wav_io = io.BytesIO()
        webm_audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Use SpeechRecognition with converted WAV
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio, language='en-US')
        logger.debug(f"Transcription successful: {transcript}")
        return transcript

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None
