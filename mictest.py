import pyaudio
import wave

def test_microphone():
    p = pyaudio.PyAudio()
    
    # Check available devices
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']} - {info['maxInputChannels']} input channels")
    try:
        stream = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=16000,
                       input=True,
                       frames_per_buffer=1024)
        print("✅ Microphone access successful!")
        stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"❌ Microphone error: {e}")
    
    p.terminate()

if __name__ == "__main__":
    test_microphone()