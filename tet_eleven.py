# test_elevenlabs.py
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Test if API key works
try:
    voices = client.voices.get_all()
    print("✅ ElevenLabs connection successful!")
    print(f"Available voices: {len(voices.voices)}")
    
    # Test TTS - FIXED: Convert generator to bytes
    audio_generator = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        model_id="eleven_turbo_v2",
        text="Hello, this is a test"
    )
    
    # Convert generator to bytes
    audio_bytes = b"".join(audio_generator)
    
    # Save to file to verify audio works
    with open("test_audio.mp3", "wb") as f:
        f.write(audio_bytes)
    print("✅ TTS test successful! Audio saved as test_audio.mp3")
    
except Exception as e:
    print(f"❌ ElevenLabs error: {e}")