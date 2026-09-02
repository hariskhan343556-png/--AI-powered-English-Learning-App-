"""
English Coach 2.0 – AI-Powered English Learning App
Streamlit application for IELTS / PTE / DET writing & speaking prep.

Stack: Streamlit UI, Groq API (LLM feedback + hosted Whisper transcription),
pyspellchecker (writing spell-check), gTTS (text-to-speech playback).
"""

import streamlit as st

from utils import (
    check_spelling,
    get_groq_client,
    get_writing_feedback,
    get_speaking_feedback,
    get_personalized_plan,
    transcribe_audio,
    text_to_speech,
)

st.set_page_config(
    page_title="English Coach 2.0",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {type, test, overall_score, weaknesses}

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""


# ---------------------------------------------------------------------------
# Sidebar – configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Setup")

    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.groq_api_key,
        help="Get a free key at https://console.groq.com/keys. "
             "Not stored anywhere except this session.",
    )
    st.session_state.groq_api_key = api_key_input

    llm_model = st.selectbox(
        "LLM model (feedback)",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        index=0,
    )

    test_type = st.selectbox("Target exam", ["IELTS", "PTE", "DET"], index=0)

    st.markdown("---")
    st.caption(
        "📝 **Writing tab** — paste an essay, get a spell-check pass plus "
        "AI band/score feedback and a corrected rewrite.\n\n"
        "🎙️ **Speaking tab** — upload an audio answer, get an AI transcript "
        "(Whisper) plus fluency/vocabulary feedback and an audio model answer "
        "(gTTS).\n\n"
        "📊 **My Progress** — personalized recommendations based on your "
        "session history."
    )

if not st.session_state.groq_api_key:
    st.warning("👈 Enter your Groq API key in the sidebar to get started.")

st.title("English Coach 2.0")
st.caption("AI-powered writing & speaking feedback for IELTS, PTE, and DET")

tab_writing, tab_speaking, tab_progress = st.tabs(
    ["📝 Writing Practice", "🎙️ Speaking Practice", "📊 My Progress"]
)

# ---------------------------------------------------------------------------
# Writing tab
# ---------------------------------------------------------------------------

with tab_writing:
    st.subheader("Writing Practice")

    w_prompt = st.text_area(
        "Task prompt (optional but recommended)",
        placeholder="e.g. Some people believe technology has made life more "
                     "complicated. To what extent do you agree or disagree?",
        height=80,
    )

    essay_text = st.text_area(
        "Your essay / response",
        placeholder="Paste or write your response here...",
        height=250,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        run_spellcheck = st.button("🔤 Check Spelling", use_container_width=True)
    with col2:
        run_ai_feedback = st.button(
            "🤖 Get AI Feedback", type="primary", use_container_width=True
        )

    if run_spellcheck:
        if not essay_text.strip():
            st.info("Write something first.")
        else:
            issues = check_spelling(essay_text)
            if not issues:
                st.success("No spelling issues found! ✅")
            else:
                st.warning(f"Found {len(issues)} possible spelling issue(s):")
                for item in issues:
                    st.write(f"❌ **{item['word']}** → suggestion: *{item['suggestion']}*")

    if run_ai_feedback:
        if not st.session_state.groq_api_key:
            st.error("Add your Groq API key in the sidebar first.")
        elif not essay_text.strip():
            st.info("Write something first.")
        else:
            with st.spinner("Analyzing your writing..."):
                try:
                    client = get_groq_client(st.session_state.groq_api_key)
                    feedback = get_writing_feedback(
                        client, llm_model, test_type, w_prompt, essay_text
                    )
                except Exception as e:
                    st.error(f"Something went wrong calling the AI: {e}")
                    feedback = None

            if feedback:
                if "raw_response" in feedback:
                    st.markdown(feedback["raw_response"])
                else:
                    scores = feedback.get("scores", {})
                    overall = feedback.get("overall_score", "N/A")

                    score_cols = st.columns(len(scores) + 1 if scores else 1)
                    for i, (k, v) in enumerate(scores.items()):
                        score_cols[i].metric(k, v)
                    score_cols[-1].metric("Overall", overall)

                    st.markdown("#### ✅ Strengths")
                    for s in feedback.get("strengths", []):
                        st.write(f"- {s}")

                    st.markdown("#### ⚠️ Areas to improve")
                    for w in feedback.get("weaknesses", []):
                        st.write(f"- {w}")

                    st.markdown("#### ✍️ Suggested rewrite")
                    st.info(feedback.get("corrected_text", "N/A"))

                    st.markdown("#### 🎯 Actionable tips")
                    for t in feedback.get("actionable_tips", []):
                        st.write(f"- {t}")

                    st.session_state.history.append(
                        {
                            "type": "writing",
                            "test": test_type,
                            "overall_score": overall,
                            "weaknesses": feedback.get("weaknesses", []),
                        }
                    )

# ---------------------------------------------------------------------------
# Speaking tab
# ---------------------------------------------------------------------------

with tab_speaking:
    st.subheader("Speaking Practice")

    s_prompt = st.text_area(
        "Speaking prompt (optional but recommended)",
        placeholder="e.g. Describe a skill you learned recently. You should "
                     "say what it is, how you learned it, and why it was useful.",
        height=80,
        key="speaking_prompt",
    )

    audio_file = st.file_uploader(
        "Upload your spoken answer (mp3, wav, m4a)",
        type=["mp3", "wav", "m4a"],
    )

    if audio_file:
        st.audio(audio_file)

    run_speaking_feedback = st.button(
        "🎧 Transcribe & Get Feedback", type="primary", use_container_width=True
    )

    if run_speaking_feedback:
        if not st.session_state.groq_api_key:
            st.error("Add your Groq API key in the sidebar first.")
        elif not audio_file:
            st.info("Upload an audio file first.")
        else:
            with st.spinner("Transcribing your speech..."):
                try:
                    client = get_groq_client(st.session_state.groq_api_key)
                    audio_bytes = audio_file.read()
                    transcript = transcribe_audio(
                        client, audio_bytes, filename=audio_file.name
                    )
                except Exception as e:
                    st.error(f"Transcription failed: {e}")
                    transcript = None

            if transcript:
                st.markdown("#### 📄 Transcript")
                st.write(transcript)

                with st.spinner("Analyzing your speaking..."):
                    try:
                        feedback = get_speaking_feedback(
                            client, llm_model, test_type, s_prompt, transcript
                        )
                    except Exception as e:
                        st.error(f"Something went wrong calling the AI: {e}")
                        feedback = None

                if feedback:
                    if "raw_response" in feedback:
                        st.markdown(feedback["raw_response"])
                    else:
                        scores = feedback.get("scores", {})
                        overall = feedback.get("overall_score", "N/A")

                        score_cols = st.columns(len(scores) + 1 if scores else 1)
                        for i, (k, v) in enumerate(scores.items()):
                            score_cols[i].metric(k, v)
                        score_cols[-1].metric("Overall", overall)

                        st.markdown("#### 🗣️ Fluency notes")
                        st.write(feedback.get("fluency_notes", "N/A"))
                        st.write(
                            f"Filler words detected: "
                            f"**{feedback.get('filler_word_count', 'N/A')}**"
                        )

                        st.markdown("#### ✅ Strengths")
                        for s in feedback.get("strengths", []):
                            st.write(f"- {s}")

                        st.markdown("#### ⚠️ Areas to improve")
                        for w in feedback.get("weaknesses", []):
                            st.write(f"- {w}")

                        st.markdown("#### 🎯 Actionable tips")
                        for t in feedback.get("actionable_tips", []):
                            st.write(f"- {t}")

                        model_answer = feedback.get("model_answer", "")
                        if model_answer:
                            st.markdown("#### 🌟 Model answer")
                            st.info(model_answer)
                            try:
                                mp3_bytes = text_to_speech(model_answer)
                                st.audio(mp3_bytes, format="audio/mp3")
                            except Exception as e:
                                st.caption(f"(Could not generate audio: {e})")

                        st.session_state.history.append(
                            {
                                "type": "speaking",
                                "test": test_type,
                                "overall_score": overall,
                                "weaknesses": feedback.get("weaknesses", []),
                            }
                        )

# ---------------------------------------------------------------------------
# Progress tab
# ---------------------------------------------------------------------------

with tab_progress:
    st.subheader("My Progress & Personalized Plan")

    if not st.session_state.history:
        st.info("Complete a writing or speaking exercise to start building your history.")
    else:
        st.markdown("#### Session history")
        for i, h in enumerate(reversed(st.session_state.history), 1):
            st.write(
                f"{i}. **{h['type'].title()}** ({h['test']}) — "
                f"Overall: {h['overall_score']}"
            )

        if st.button("🧭 Generate Personalized Study Plan", type="primary"):
            if not st.session_state.groq_api_key:
                st.error("Add your Groq API key in the sidebar first.")
            else:
                summary_lines = []
                for h in st.session_state.history:
                    summary_lines.append(
                        f"- {h['type']} ({h['test']}), overall score: "
                        f"{h['overall_score']}, weaknesses: "
                        f"{', '.join(h['weaknesses']) if h['weaknesses'] else 'none noted'}"
                    )
                history_summary = "\n".join(summary_lines)

                with st.spinner("Building your personalized plan..."):
                    try:
                        client = get_groq_client(st.session_state.groq_api_key)
                        plan = get_personalized_plan(
                            client, llm_model, test_type, history_summary
                        )
                        st.markdown("#### 🧭 Your personalized study plan")
                        st.markdown(plan)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
