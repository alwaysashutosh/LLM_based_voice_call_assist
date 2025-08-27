import streamlit as st
import os, base64, asyncio, tempfile
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="🎙️ Ola Voice Bot Support", page_icon="🎙️", layout="wide")

class VoiceBot:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """You are an Ola customer support bot speaking only in Hindi. Follow this script exactly:
        - Wait for the user to say: "Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi."
        - Then you say: "Ola customer support mein aapka swagat hai. Kya yeh aapka registered number hai?"
        - If the user confirms (e.g., "Haan"), you say: "Aapka number blocked nahi hai. Sab theek hai. Kripya apna location badal kar phir se rides check kijye."
        - After giving the solution, end the conversation.
        Do not deviate from this script. Keep responses very short and concise."""
        self.conversation_state = "waiting_for_complaint"

    def transcribe_audio(self, audio_bytes):
        """Transcribe audio using Whisper"""
        try:
            #saving file check
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                audio_path = tmp_file.name
            
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="hi"
                )
            os.unlink(audio_path)
            return transcript.text
        except Exception as e:
            st.error(f"Transcription error: {e}")
            return None

    def get_llm_response(self, user_input):
        """Get response from GPT-4"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.1
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Technical error: {e}"

    def text_to_speech(self, text):
        """Convert text to Hindi speech"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            return response.content  # Returns audio bytes directly
        except Exception as e:
            st.error(f"TTS error: {e}")
            return None

def play_audio(audio_bytes):
    """Auto-play audio in Streamlit"""
    try:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay controls style="width: 100%">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio playback error: {e}")

def main():
    if "assistant" not in st.session_state:
        st.session_state.assistant = VoiceBot()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    st.markdown('<h1 style="text-align:center;color:#FF4B4B;">🎙️ Ola Voice Bot Support</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.write("""
        1. Click the microphone below
        2. Say in Hindi: *"Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi."*
        3. Wait for bot response
        4. Then say: *"Haan, yeh mera registered number hai."*
        """)
        
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.assistant = VoiceBot()
            st.rerun()

    # Main content
    recorded_audio = audio_recorder(
        text="🎤 Press to speak",
        recording_color="#FF4B4B",
        neutral_color="#0066CC",
        icon_size="2x"
    )
    
    if recorded_audio:
        with st.spinner("🔄 Processing your voice..."):
            
            transcript = st.session_state.assistant.transcribe_audio(recorded_audio)
            
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                
                
                bot_text = st.session_state.assistant.get_llm_response(transcript)
                
                if bot_text:
                    st.session_state.messages.append({"role": "assistant", "content": bot_text})
                    
                    # Convert to speech
                    bot_audio = st.session_state.assistant.text_to_speech(bot_text)
    
    
    if st.session_state.messages:
        st.subheader("💬 Conversation")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div style="background:#000000;padding:10px;border-radius:10px;margin:5px 0;"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#000000;padding:10px;border-radius:10px;margin:5px 0;"><strong>Bot:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                
                
                if msg == st.session_state.messages[-1]:  # latest message
                    bot_audio = st.session_state.assistant.text_to_speech(msg["content"])
                    if bot_audio:
                        play_audio(bot_audio)

if __name__ == "__main__":
    main()