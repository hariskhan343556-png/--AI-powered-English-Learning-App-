import streamlit as st
from utils.ai import analyze_writing, chat_with_tutor
from utils.spelling import spelling_report
from utils.speech import transcribe_audio, text_to_speech

st.set_page_config(page_title="EnglishAI Coach", page_icon="🎓", layout="wide")

st.title("🎓 EnglishAI Coach")
st.caption("AI-powered English practice for writing, speaking, vocabulary, and exam preparation.")

if "chat" not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.header("Practice Mode")
    mode = st.radio("Choose a module", ["Writing Coach", "Speaking Coach", "AI Tutor", "Exam Practice"])
    st.divider()
    st.info("For Groq features, add GROQ_API_KEY to Streamlit Secrets.")

if mode == "Writing Coach":
    st.header("✍️ Writing Coach")
    prompt = st.text_area("Optional task/prompt", placeholder="e.g. Write an IELTS Task 2 essay about online education.")
    text = st.text_area("Write your English here", height=260, placeholder="Start writing...")
    if st.button("Analyze Writing", type="primary", use_container_width=True):
        if not text.strip():
            st.warning("Please enter some writing first.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Words", len(text.split()))
            c2.metric("Characters", len(text))
            spelling = spelling_report(text)
            c3.metric("Possible spelling issues", len(spelling))

            if spelling:
                st.subheader("🔤 Spelling")
                for word, suggestions in spelling.items():
                    st.write(f"**{word}** → {', '.join(suggestions[:5])}")

            with st.spinner("AI is evaluating your writing..."):
                result = analyze_writing(text, prompt)
            st.subheader("🤖 AI Feedback")
            st.markdown(result)

            if st.button("🔊 Read feedback aloud"):
                audio = text_to_speech(result)
                if audio:
                    st.audio(audio, format="audio/mp3")

elif mode == "Speaking Coach":
    st.header("🎤 Speaking Coach")
    st.write("Upload an audio recording of your English speaking practice.")
    audio = st.file_uploader("Audio file", type=["wav", "mp3", "m4a", "webm", "ogg"])
    if audio:
        st.audio(audio)
        if st.button("Transcribe & Analyze", type="primary", use_container_width=True):
            with st.spinner("Transcribing with Whisper..."):
                transcript = transcribe_audio(audio)
            if transcript:
                st.subheader("📝 Transcript")
                st.write(transcript)
                with st.spinner("Analyzing speaking performance..."):
                    result = analyze_writing(
                        transcript,
                        "Evaluate this as English speaking practice. Focus on fluency, grammar, vocabulary, coherence and likely IELTS/PTE/DET-style performance."
                    )
                st.subheader("📊 Speaking Feedback")
                st.markdown(result)

elif mode == "AI Tutor":
    st.header("🧠 AI English Tutor")
    st.write("Practice natural English conversation and ask grammar or vocabulary questions.")
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(msg)

    user_msg = st.chat_input("Talk to your English tutor...")
    if user_msg:
        st.session_state.chat.append(("user", user_msg))
        with st.chat_message("user"):
            st.markdown(user_msg)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = chat_with_tutor(st.session_state.chat)
            st.markdown(answer)
        st.session_state.chat.append(("assistant", answer))

elif mode == "Exam Practice":
    st.header("📝 Exam Practice")
    exam = st.selectbox("Choose exam", ["IELTS", "PTE", "Duolingo English Test (DET)"])
    task = st.selectbox("Choose practice", ["Writing", "Speaking", "Vocabulary"])
    if st.button("Generate Practice Task", type="primary", use_container_width=True):
        with st.spinner("Generating a practice task..."):
            result = chat_with_tutor([
                ("user", f"Create one realistic {exam} {task} practice task. Give clear instructions, suggested time, and what a high-scoring answer should demonstrate. Do not provide the answer.")
            ])
        st.markdown(result)
