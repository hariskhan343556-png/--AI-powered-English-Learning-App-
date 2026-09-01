import streamlit as st
from utils.ai import analyze_text, tutor_response, generate_exam_task
from utils.spelling import spelling_report
from utils.speech import transcribe_audio, text_to_speech

st.set_page_config(
    page_title="EnglishAI Coach",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb;
}
h1, h2, h3 {
    letter-spacing: -0.02em;
}
.metric-card {
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title("EnglishAI Coach")
st.write("AI-assisted English learning for writing, speaking, conversation, and exam preparation.")

with st.sidebar:
    st.subheader("Learning Modules")
    mode = st.radio(
        "Select a module",
        ["Writing Coach", "Speaking Coach", "AI Tutor", "Exam Practice"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Use your Groq API key through Streamlit Secrets for AI and transcription features.")

if mode == "Writing Coach":
    st.header("Writing Coach")
    st.write("Improve grammar, vocabulary, clarity, spelling, and organization.")

    task = st.text_input(
        "Writing task or topic",
        placeholder="Example: Discuss the advantages and disadvantages of online education."
    )

    text = st.text_area(
        "Your writing",
        height=280,
        placeholder="Enter your English writing here..."
    )

    if st.button("Analyze Writing", type="primary", use_container_width=True):
        if not text.strip():
            st.warning("Please enter some writing before starting the analysis.")
        else:
            spelling = spelling_report(text)

            col1, col2, col3 = st.columns(3)
            col1.metric("Words", len(text.split()))
            col2.metric("Characters", len(text))
            col3.metric("Possible spelling issues", len(spelling))

            if spelling:
                st.subheader("Spelling Review")
                for word, suggestions in spelling.items():
                    if suggestions:
                        st.write(f"**{word}**: {', '.join(suggestions[:5])}")

            with st.spinner("Analyzing your writing..."):
                feedback = analyze_text(text, task)

            st.subheader("AI Feedback")
            st.markdown(feedback)

            if st.button("Generate Audio Feedback"):
                audio = text_to_speech(feedback)
                if audio:
                    st.audio(audio, format="audio/mp3")

elif mode == "Speaking Coach":
    st.header("Speaking Coach")
    st.write("Upload a recording of your English speaking practice for transcription and AI feedback.")

    audio_file = st.file_uploader(
        "Upload an audio recording",
        type=["wav", "mp3", "m4a", "webm", "ogg"]
    )

    if audio_file:
        st.audio(audio_file)

        if st.button("Transcribe and Analyze", type="primary", use_container_width=True):
            with st.spinner("Transcribing the recording..."):
                transcript = transcribe_audio(audio_file)

            if transcript.startswith("ERROR:"):
                st.error(transcript.replace("ERROR: ", ""))
            else:
                st.subheader("Transcript")
                st.write(transcript)

                speaking_task = (
                    "Evaluate this English speaking transcript. "
                    "Assess grammar, vocabulary, fluency, coherence, "
                    "naturalness and provide an informal IELTS, PTE or DET-style level estimate."
                )

                with st.spinner("Analyzing speaking performance..."):
                    feedback = analyze_text(transcript, speaking_task)

                st.subheader("Speaking Feedback")
                st.markdown(feedback)

elif mode == "AI Tutor":
    st.header("AI English Tutor")
    st.write("Practice English conversation and ask questions about grammar, vocabulary, and communication.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Write a message in English...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your response..."):
                response = tutor_response(st.session_state.messages)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

elif mode == "Exam Practice":
    st.header("Exam Practice")
    st.write("Generate practice tasks for major English proficiency examinations.")

    exam = st.selectbox(
        "Examination",
        ["IELTS", "PTE", "Duolingo English Test"]
    )

    skill = st.selectbox(
        "Skill",
        ["Writing", "Speaking", "Vocabulary"]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Intermediate", "Upper Intermediate", "Advanced"]
    )

    if st.button("Generate Practice Task", type="primary", use_container_width=True):
        with st.spinner("Generating practice material..."):
            task = generate_exam_task(exam, skill, difficulty)

        st.subheader("Practice Task")
        st.markdown(task)
