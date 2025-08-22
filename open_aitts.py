# simple_tts_test.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_hindi_tts():
    """Test Hindi TTS directly with OpenAI"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test all the phrases from your script
    hindi_phrases = [
        "मैं 2 घंटे से ऑनलाइन हूं पर मुझे कोई राइड नहीं मिल रही",
        "ओला कस्टमर सपोर्ट में आपका स्वागत है",
        "क्या यह आपका रजिस्टर्ड नंबर है?",
        "हां, यह मेरा रजिस्टर्ड नंबर है",
        "आपका नंबर ब्लॉक नहीं है, सब ठीक है",
        "कृपया अपना लोकेशन बदल कर फिर से राइड्स चेक कीजिए"
    ]
    
    try:
        for i, phrase in enumerate(hindi_phrases):
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=phrase
            )
            
            response.stream_to_file(f"hindi_demo_{i+1}.mp3")
            print(f"✅ Saved: '{phrase}' -> hindi_demo_{i+1}.mp3")
        
        print("\n🎧 All audio files generated successfully!")
        print("Play them to verify Hindi pronunciation quality")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hindi_tts()