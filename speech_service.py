import os
import logging
import base64
import requests
import json
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ElevenLabs API configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)

def text_to_speech(text: str) -> Optional[str]:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: The text to convert to speech
        
    Returns:
        Base64 encoded audio data, or None if the conversion fails
    """
    logger.debug(f"Converting text to speech: {text[:50]}...")
    
    # Check if ElevenLabs API key is configured
    if not ELEVENLABS_API_KEY:
        logger.warning("ElevenLabs API key is missing. Using browser's built-in TTS.")
        return None
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(
            f"{ELEVENLABS_API_URL}/{ELEVENLABS_VOICE_ID}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            # Convert audio binary data to base64 for embedding in HTML
            audio_data = base64.b64encode(response.content).decode('utf-8')
            return audio_data
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error using ElevenLabs API: {str(e)}")
        return None

def fallback_tts(text: str) -> None:
    """
    Note: This is a placeholder for any server-side fallback TTS implementation.
    The actual implementation uses the browser's SpeechSynthesis API.
    
    Args:
        text: The text to convert to speech
    """
    logger.debug("Using fallback TTS method")
    return None