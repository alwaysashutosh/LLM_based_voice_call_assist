import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_hindi_tts():
    """Test Hindi TTS directly with OpenAI (streams to files)."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
            # Use streaming response API to reliably write MP3 files
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                input=phrase
            ) as response:
                out_file = f"hindi_demo_{i+1}.mp3"
                response.stream_to_file(out_file)
            print(f"Saved: sample {i+1} -> {out_file}")
        
        print("All audio files generated successfully. Play them to verify.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hindi_tts()