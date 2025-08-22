import asyncio
import os
from dotenv import load_dotenv

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineTaskParams
from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.openai.tts import OpenAITTSService

from app.services import SYSTEM_PROMPT

async def main():
    load_dotenv()

   
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return

    
    audio_params = LocalAudioTransportParams(
        audio_in_sample_rate=16000,
        audio_out_sample_rate=24000,
        audio_in_channels=1,
        audio_out_channels=1,
        audio_in_device_name=1,
        audio_out_device_name=3,
    )
    local_audio = LocalAudioTransport(params=audio_params)

 
    stt = OpenAISTTService(model="whisper-1", api_key=openai_api_key)
    
    
    llm = OpenAILLMService(
        model="gpt-4o-mini",
        api_key=openai_api_key,
        system_prompt=SYSTEM_PROMPT
    )
    
   
    tts = OpenAITTSService(
        api_key=openai_api_key,
        voice="nova",  
        model="tts-1"
    )

    
    pipeline = Pipeline([
        local_audio.input(),
        stt,
        llm,
        tts,
        local_audio.output(),
    ])

    print("=" * 60)
    print("🎙️  Voice Bot Prototype - Ola Driver Support")
    print("=" * 60)
    print("SPEAK THIS HINDI PHRASE FIRST:")
    print("👉 'Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi.'")
    print("")
    print("THEN CONFIRM WHEN ASKED:")
    print("👉 'Haan, yeh mera registered number hai.'")
    print("=" * 60)
    print("Make sure your microphone is enabled and speak clearly!")
    print("Press Ctrl+C to stop.")
    print("")

    task = PipelineTask(pipeline)
    try:
        await task.run(PipelineTaskParams(loop=asyncio.get_running_loop()))
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        await task.cancel()
    except Exception as e:
        print(f"❌ Error: {e}")
        await task.cancel()

if __name__ == "__main__":
    asyncio.run(main())