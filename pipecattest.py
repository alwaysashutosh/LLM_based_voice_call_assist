import asyncio
import time
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineTaskParams
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.frames.frames import TextFrame
from pipecat.processors.frame_processor import FrameDirection
import os
from dotenv import load_dotenv

load_dotenv()

async def test_tts_only():
    """Test only Text-to-Speech"""
    print("Testing TTS only...")
    
    audio_params = LocalAudioTransportParams(
        audio_out_sample_rate=24000,
        audio_out_channels=1,
        audio_out_device_name="Speakers",
    )
    local_audio = LocalAudioTransport(params=audio_params)
    
    tts = OpenAITTSService(
        api_key=os.getenv("OPENAI_API_KEY"),
        voice="nova",
        model="tts-1"
    )
    
    pipeline = Pipeline([
        tts,
        local_audio.output(),
    ])
    
    # Manually send text to TTS with correct parameters
    text_frame = TextFrame("नमस्ते, यह एक टेस्ट है")
    await tts.process_frame(text_frame, FrameDirection.DOWNSTREAM)
    
    print("TTS test completed")

async def test_simple_tts():
    """Simpler TTS test without pipeline complexity"""
    print("Testing simple TTS...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test Hindi text with OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input="ओला कस्टमर सपोर्ट में आपका स्वागत है"
        )
        
        # Save the audio
        response.stream_to_file("hindi_tts_test.mp3")
        print("✅ TTS test successful! Saved as hindi_tts_test.mp3")
        print("Play the file to hear Hindi pronunciation")
        
    except Exception as e:
        print(f"❌ TTS error: {e}")

async def main():
    print("Running audio tests...")
    
    # Test simple TTS first
    await test_simple_tts()
    
    # Then test pipeline TTS
    await test_tts_only()

if __name__ == "__main__":
    asyncio.run(main())