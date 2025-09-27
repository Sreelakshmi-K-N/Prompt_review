import streamlit as st
import requests
import speech_recognition as sr
from costar_mapper import extract_costar
from rule_engine import evaluate_prompt
from llm_broker import get_llm_response
from db_logger import log_prompt
from user_auth import create_user, authenticate_user

st.set_page_config(page_title="Prompt Review Engine", layout="centered")

# 🔐 Session state
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# 🔐 Login
if not st.session_state.user_authenticated:
    st.sidebar.header("🔐 User Login")
    auth_mode = st.sidebar.radio("Login or Signup", ["Login", "Signup"])
    username_input = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Signup":
        if st.sidebar.button("Create Account"):
            create_user(username_input, password_input)
            st.sidebar.success("Account created! Please log in.")
    elif auth_mode == "Login":
        if st.sidebar.button("Login"):
            if authenticate_user(username_input, password_input):
                st.session_state.user_authenticated = True
                st.session_state.username = username_input
                st.sidebar.success("Login successful!")
            else:
                st.sidebar.error("Invalid credentials.")
else:
    st.sidebar.markdown(f"👤 {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.user_authenticated = False
        st.session_state.username = ""
        st.session_state.prompt = ""

# ✅ Main App
if st.session_state.user_authenticated:
    page = st.sidebar.radio("📂 Navigate", ["Prompt Review", "Feedback"])

    # 🎨 Styling
    st.markdown("""
        <style>
            body { background-color: #f5f5ff; }
            .main { background-color: #ffffff; padding: 2rem; border-radius: 10px; }
            h1, h2, h3 { color: #6a5acd; }
            .stTextArea textarea { background-color: #ffffff !important; }
            .stButton button { background-color: #6a5acd !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    if page == "Prompt Review":
        st.title("🧪 Prompt Review Engine")
        st.write("Analyze your prompt using COSTAR and get a safety verdict before sending it to an LLM.")

        # 🌐 Voice input language
        st.sidebar.subheader("🌐 Voice Input Language")
        language_code = st.sidebar.selectbox("Choose language", {
            "English (India)": "en-IN",
            "Hindi": "hi-IN",
            "Tamil": "ta-IN",
            "Kannada": "kn-IN",
            "Telugu": "te-IN"
        })

        # 🎤 Voice input
        st.subheader("🎤 Record Voice Prompt")
        if st.button("Start Recording"):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Speak now.")
                audio = r.listen(source)
                try:
                    st.session_state.prompt = r.recognize_google(audio, language=language_code)
                    st.success("Transcription complete.")
                except sr.UnknownValueError:
                    st.error("Could not understand audio.")
                except sr.RequestError:
                    st.error("Speech recognition service failed.")

        # 🖊 Manual input fallback
        st.session_state.prompt = st.text_area("🖊 Enter your prompt here:", value=st.session_state.prompt)

        # ⚙ Model selection
        st.sidebar.header("⚙ Settings")
        model_choice = st.sidebar.selectbox("Choose LLM model", ["mistral", "llama2", "gemma", "llama3"])

        def is_ollama_running():
            try:
                response = requests.get("http://localhost:11434")
                return response.status_code == 200
            except:
                return False

        ollama_available = is_ollama_running()
        use_mock = not ollama_available

        if not ollama_available:
            st.warning("⚠ Ollama server is not reachable. Using mock response instead.")

        # 🚀 Evaluate prompt
        if st.button("Evaluate Prompt") and st.session_state.prompt:
            costar = extract_costar(st.session_state.prompt)
            verdict, reason, fix_suggestion = evaluate_prompt(st.session_state.prompt, costar)

            st.markdown("### 🧠 COSTAR Breakdown")
            for key, value in costar.items():
                st.markdown(f"""
                <div style='background-color:#f0f8ff;padding:10px;margin-bottom:10px;border-left:5px solid #6a5acd;border-radius:5px'>
                    <strong>{key}:</strong> {value}
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='background-color:#e6f2ff;padding:10px;border-radius:8px'>
                <h4 style='color:#003366'>✅ Verdict</h4>
                <p><strong>{verdict}</strong> – {reason}</p>
            </div>
            """, unsafe_allow_html=True)

            llm_response = ""
            if verdict == "ALLOW":
                llm_response = get_llm_response(st.session_state.prompt, use_mock=use_mock, model=model_choice)
                st.markdown("### 🤖 LLM Response")
                st.markdown(f"""
                <div style='background-color:#f9f9f9;padding:10px;border-left:5px solid #6a5acd;border-radius:5px'>
                    <pre>{llm_response}</pre>
                </div>
                """, unsafe_allow_html=True)
            elif verdict == "NEEDS_FIX":
                st.markdown("### 🛠 Suggested Fix")
                st.write(fix_suggestion)
            elif verdict == "BLOCK":
                st.markdown("### 🚫 Blocked Prompt")
                st.write("This prompt contains unsafe or prohibited content.")

            log_prompt(st.session_state.prompt, verdict, reason, costar["Tone"], costar, llm_response)

    elif page == "Feedback":
        st.title("📝 Feedback Center")
        st.write("Share your thoughts about the app or LLM responses.")

        rating = st.radio("Rate your experience:", ["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"])
        comments = st.text_area("Additional comments")
        if st.button("Submit Feedback"):
            st.success("Thanks for your feedback!")
else:
    st.warning("Please log in to access the Prompt Review Engine.")