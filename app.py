import os
import tempfile
from io import BytesIO

import streamlit as st

st.set_page_config(page_title="EnglishCoach 2.0", page_icon="🗣️", layout="wide")

try:
    from utils.ai import get_feedback, transcribe_audio
    from utils.audio import text_to_speech
    from utils.spell import check_spelling
except Exception as exc:
    st.error(f"Application startup error: {exc}")
    st.stop()

st.title("🗣️ EnglishCoach 2.0")
st.caption("AI-powered English learning for writing, speaking, vocabulary, and exam preparation")

with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Learning mode", ["Writing Coach", "Speaking Coach", "Exam Practice"])
    exam = st.selectbox("Target exam", ["General English", "IELTS", "PTE", "DET"])
    st.info("Add your GROQ_API_KEY in Streamlit Cloud → Settings → Secrets for AI feedback and Whisper transcription.")

if mode == "Writing Coach":
    st.subheader("✍️ Writing Coach")
    text = st.text_area("Write something in English", height=220, placeholder="Write a paragraph, email, answer, or essay...")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Check Spelling", use_container_width=True):
            if not text.strip():
                st.warning("Please enter some text first.")
            else:
                misspelled = check_spelling(text)
                if misspelled:
                    st.warning("Possible spelling issues: " + ", ".join(misspelled))
                else:
                    st.success("No obvious spelling mistakes found.")
    with c2:
        if st.button("Get AI Feedback", type="primary", use_container_width=True):
            if not text.strip():
                st.warning("Please enter some text first.")
            else:
                with st.spinner("Analyzing your English..."):
                    result = get_feedback(text, exam=exam, task="writing")
                st.markdown(result)

elif mode == "Speaking Coach":
    st.subheader("🎙️ Speaking Coach")
    st.write("Upload an audio recording. The app transcribes it with Whisper and gives personalized feedback.")
    audio = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg", "webm"])
    if audio:
        st.audio(audio)
        if st.button("Transcribe & Analyze", type="primary"):
            suffix = os.path.splitext(audio.name)[1] or ".wav"
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                    f.write(audio.getbuffer())
                    path = f.name
                with st.spinner("Transcribing with Whisper..."):
                    transcript = transcribe_audio(path)
                st.markdown("### Transcript")
                st.write(transcript)
                with st.spinner("Generating speaking feedback..."):
                    st.markdown(get_feedback(transcript, exam=exam, task="speaking"))
            except Exception as exc:
                st.error(str(exc))
            finally:
                try:
                    os.remove(path)
                except Exception:
                    pass

else:
    st.subheader("📝 Exam Practice")
    task = st.selectbox("Practice task", ["Essay / Long Answer", "Speaking Response", "Short Answer"])
    prompt = st.text_area("Enter your response", height=240)
    if st.button("Evaluate Response", type="primary"):
        if not prompt.strip():
            st.warning("Please enter a response first.")
        else:
            with st.spinner("Evaluating your response..."):
                st.markdown(get_feedback(prompt, exam=exam, task=task.lower()))

st.divider()
st.caption("Built with Streamlit • Groq • Whisper • pyspellchecker • gTTS")
