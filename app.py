import streamlit as st
import os
import tempfile
from openai import OpenAI
import base64
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="🎙️ Ola Voice Bot Support",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .bot-message {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: left;
    }
    .instruction-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class VoiceBot:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.script = """You are an Ola customer support bot speaking only in Hindi. Follow this script exactly:
        - Wait for the user to say: "Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi."
        - Then you say: "Ola customer support mein aapka swagat hai. Kya yeh aapka registered number hai?"
        - If the user confirms (e.g., "Haan"), you say: "Aapka number blocked nahi hai. Sab theek hai. Kripya apna location badal kar phir se rides check kijye."
        - After giving the solution, end the conversation.
        Do not deviate from this script. Keep responses very short and concise."""
        
        self.chat_history = []

    def understand_speech(self, audio_path):
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="hi"
                )
            return transcript.text
        except:
            return None

    def think_response(self, user_words):
        try:
            messages = [
                {"role": "system", "content": self.script},
                {"role": "user", "content": user_words}
            ]
            
            for msg in self.chat_history[-4:]:
                messages.append(msg)
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.1
            )
            
            return completion.choices[0].message.content
        except:
            return "माफ़ कीजिए, तकनीकी समस्या आ रही है।"

    def speak_response(self, text, filename="bot_speak.mp3"):
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
                speed=1.0
            )
            
            response.stream_to_file(filename)
            return filename
        except:
            return None

    def chat(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        
        bot_reply = self.think_response(user_input)
        
        self.chat_history.append({"role": "assistant", "content": bot_reply})
        
        voice_file = self.speak_response(bot_reply)
        
        return bot_reply, voice_file

def play_audio(audio_file):
    try:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay controls style="width: 100%">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except:
        st.error("Audio couldn't play")

def main():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = VoiceBot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None

    st.markdown('<h1 class="main-header">🎙️ Ola Voice Bot Support</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("ℹ️ About This Bot")
        st.write("This voice assistant helps Ola drivers with ride availability issues in real Hindi conversations.")
        
        st.header("🎯 How to Talk")
        st.write("""
        First say: *"Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi."*
        
        Then say: *"Haan, yeh mera registered number hai."*
        """)
        
        if st.button("🔄 Start New Chat"):
            st.session_state.messages = []
            st.session_state.assistant = VoiceBot()
            st.session_state.current_audio = None
            st.rerun()

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('### 💬 Your Conversation')
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message"><strong>Bot:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('### 🎤 Record Your Message')
        
        recorded_audio = audio_recorder(
            text="Press to speak",
            recording_color="#e8b",
            neutral_color="#6aa",
            icon_size="2x",
        )
        
        if recorded_audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(recorded_audio)
                audio_path = temp_audio.name
            
            with st.spinner("Listening to your words..."):
                user_speech = st.session_state.assistant.understand_speech(audio_path)
                
                if user_speech:
                    st.session_state.messages.append({"role": "user", "content": user_speech})
                    
                    bot_text, bot_audio = st.session_state.assistant.chat(user_speech)
                    
                    if bot_text:
                        st.session_state.messages.append({"role": "assistant", "content": bot_text})
                        st.session_state.current_audio = bot_audio
                        
                        st.rerun()
                
                os.unlink(audio_path)
    
    with col2:
        st.markdown('### 📋 Conversation Guide')
        
        st.markdown("""
        <div class="instruction-box">
        <strong>How this works:</strong><br>
        1. You speak your problem<br>
        2. Bot understands and replies<br>
        3. You confirm your details<br>
        4. Bot helps solve the issue
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('### 🔊 Bot\'s Voice Reply')
        
        if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
            play_audio(st.session_state.current_audio)
            
            with open(st.session_state.current_audio, "rb") as f:
                audio_data = f.read()
            st.download_button(
                label="📥 Save This Response",
                data=audio_data,
                file_name="ola_bot_response.mp3",
                mime="audio/mp3"
            )
        
        st.markdown("---")
        st.markdown("### 🛠️ Behind the Scenes")
        st.write("""
        Powered by:
        - OpenAI Whisper (hearing)
        - GPT-4 (thinking)
        - OpenAI TTS (speaking)
        - All in Hindi
        """)

    st.markdown("---")
    st.caption("Voice support for Ola drivers • Built with modern AI")

if __name__ == "__main__":
    main()