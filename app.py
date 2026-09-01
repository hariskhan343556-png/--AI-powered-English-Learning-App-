import streamlit as st
from utils.ai import analyze_text, tutor_response, generate_exam_task
from utils.spelling import spelling_report
from utils.speech import transcribe_audio, create_audio

st.set_page_config(
    page_title="EnglishAI Coach",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("EnglishAI Coach")
st.caption("AI-powered English practice for writing, speaking, tutoring, and exam preparation.")

with st.sidebar:
    st.header("Learning Modules")
    module = st.radio(
        "Select a module",
        ["Writing Coach", "Speaking Coach", "AI Tutor", "Exam Practice"],
    )
    st.divider()
    st.caption("Powered by Groq, Streamlit, Whisper, SpellChecker and gTTS.")

if module == "Writing Coach":
    st.header("Writing Coach")
    task = st.text_input("Task or topic", placeholder="Describe the writing task or topic.")
    text = st.text_area("Your response", height=260, placeholder="Write your English response here.")

    if text.strip():
        metrics = spelling_report(text)
        c1, c2, c3 = st.columns(3)
        c1.metric("Words", metrics["words"])
        c2.metric("Characters", metrics["characters"])
        c3.metric("Possible spelling issues", metrics["misspellings"])

        if metrics["suggestions"]:
            with st.expander("Spelling suggestions"):
                for item in metrics["suggestions"]:
                    st.write(f"{item['word']} → {', '.join(item['suggestions'])}")

    if st.button("Analyze writing", type="primary", disabled=not text.strip()):
        with st.spinner("Analyzing your writing..."):
            result = analyze_text(text, task)

        st.subheader("AI Feedback")
        st.markdown(result)

        audio = create_audio(result)
        if audio:
            st.audio(audio, format="audio/mp3")

elif module == "Speaking Coach":
    st.header("Speaking Coach")
    st.write("Upload a short English recording for transcription and AI feedback.")
    audio_file = st.file_uploader(
        "Upload audio",
        type=["wav", "mp3", "m4a", "webm", "ogg"],
    )
    prompt = st.text_input("Speaking topic", placeholder="Optional topic or question.")

    if audio_file and st.button("Analyze speaking", type="primary"):
        with st.spinner("Transcribing and analyzing..."):
            transcript = transcribe_audio(audio_file)
            feedback = analyze_text(transcript, prompt or "Speaking practice")

        st.subheader("Transcript")
        st.write(transcript)
        st.subheader("AI Feedback")
        st.markdown(feedback)

elif module == "AI Tutor":
    st.header("AI English Tutor")
    st.write("Ask questions about grammar, vocabulary, writing, pronunciation, or everyday English.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask your English tutor a question...")
    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = tutor_response(st.session_state.messages)
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

elif module == "Exam Practice":
    st.header("Exam Practice")
    c1, c2, c3 = st.columns(3)
    with c1:
        exam = st.selectbox("Exam", ["IELTS", "PTE", "DET"])
    with c2:
        skill = st.selectbox("Skill", ["Writing", "Speaking", "Vocabulary"])
    with c3:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Generate practice task", type="primary"):
        with st.spinner("Creating practice task..."):
            task_text = generate_exam_task(exam, skill, difficulty)
        st.session_state.exam_task = task_text

    if "exam_task" in st.session_state:
        st.subheader("Practice Task")
        st.markdown(st.session_state.exam_task)

        if skill in ["Writing", "Speaking"]:
            response = st.text_area("Your response", height=220)
            if st.button("Get AI evaluation", disabled=not response.strip()):
                with st.spinner("Evaluating your response..."):
                    feedback = analyze_text(
                        response,
                        f"{exam} {skill} practice at {difficulty} level",
                    )
                st.subheader("Evaluation")
                st.markdown(feedback)
