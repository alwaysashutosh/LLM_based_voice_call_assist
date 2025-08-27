"""
Voice Bot Audio Configuration
============================

Auto-generated configuration based on audio diagnostics.
Generated on: 2025-08-24T23:13:37.735982
Device: Microphone Array (Intel® Smart 
Sample Rate: 44100Hz
"""

# Audio Configuration
AUDIO_CONFIG = {
  "device_index": 1,
  "device_name": "Microphone Array (Intel\u00c2\u00ae Smart ",
  "sample_rate": 44100,
  "channels": 1,
  "format": "pyaudio.paInt16",
  "chunk_size": 1024,
  "exception_on_overflow": False,
  "recommendations": [
    "Using device: Microphone Array (Intel\u00c2\u00ae Smart ",
    "Using sample rate 44100Hz (16000Hz preferred for voice)"
  ]
}

# PipeCat Configuration
def get_pipecat_audio_params():
    """Get PipeCat audio parameters"""
    from pipecat.transports.local.audio import LocalAudioTransportParams
    
    return LocalAudioTransportParams(
        audio_in_sample_rate=44100,
        audio_out_sample_rate=24000,
        audio_in_channels=1,
        audio_out_channels=1,
    )

# PyAudio Configuration
def get_pyaudio_config():
    """Get PyAudio configuration"""
    import pyaudio
    
    return {
        'format': pyaudio.paInt16,
        'channels': 1,
        'rate': 44100,
        'input': True,
        'input_device_index': 1,
        'frames_per_buffer': 1024,
        'exception_on_overflow': False
    }

# Usage Example
if __name__ == "__main__":
    print("Voice Bot Audio Configuration")
    print("=" * 40)
    print(f"Device: {AUDIO_CONFIG['device_name']}")
    print(f"Sample Rate: {AUDIO_CONFIG['sample_rate']}Hz")
    print(f"Channels: {AUDIO_CONFIG['channels']}")
    print(f"Device Index: {AUDIO_CONFIG['device_index']}")
    print()
    print("Recommendations:")
    for rec in AUDIO_CONFIG['recommendations']:
        print(f"  - {rec}")
