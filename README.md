# English Coach 2.0 – AI-Powered English Learning App

A Streamlit app that gives real-time writing and speaking feedback for
**IELTS**, **PTE**, and **DET** prep.

## Features

- 📝 **Writing Practice** — spell-check (pyspellchecker) + AI band/score
  feedback, strengths/weaknesses, and a corrected rewrite (Groq LLM).
- 🎙️ **Speaking Practice** — upload an audio answer, get an AI transcript
  (Groq-hosted Whisper), fluency/vocabulary/grammar feedback, and a spoken
  model answer (gTTS).
- 📊 **My Progress** — tracks your session history and generates a
  personalized study plan targeting your weakest areas.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Get a free Groq API key from https://console.groq.com/keys.

3. Run the app:

   ```bash
   streamlit run app.py
   ```

4. Paste your Groq API key into the sidebar when the app opens (it's kept
   only in that session — never written to disk).

## Notes on the stack

- **LLM feedback**: uses Groq's chat completions API (default model:
  `llama-3.3-70b-versatile`) with structured JSON prompts so scores and tips
  render as clean UI elements rather than raw text.
- **Whisper transcription**: uses Groq's hosted Whisper endpoint
  (`whisper-large-v3-turbo`) rather than running Whisper locally, so there's
  no large model download and it works on lightweight hosting.
- **Text-to-speech**: gTTS requires an internet connection at runtime (it
  calls Google's TTS service).
- **Spell-check**: pyspellchecker runs fully offline/locally.

## Ideas for extending

- Persist session history to a database (SQLite/Postgres) instead of
  `st.session_state`, so progress survives restarts.
- Add a timer for timed writing/speaking tasks to simulate real exam
  conditions.
- Add a prompt bank per exam type so users don't have to write their own
  prompts.
- Swap gTTS for a higher-quality neural TTS voice for the model answers.
