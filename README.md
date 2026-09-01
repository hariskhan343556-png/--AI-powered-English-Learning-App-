# EnglishCoach 2.0 — AI-Powered English Learning App

A Streamlit application for improving English writing and speaking with AI feedback, spell checking, and speech transcription.

## Features
- Writing Coach with grammar, vocabulary, clarity, corrections, and improved-version feedback
- Speaking Coach with audio upload, Groq Whisper transcription, and AI evaluation
- IELTS, PTE, DET, and General English practice modes
- Spell checking with `pyspellchecker`
- Streamlit-friendly error handling and modular utility files

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app and select `app.py`.
3. Add this secret under **Settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

4. Deploy.

Never commit your API key to GitHub.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes
The application uses Groq's API for LLM feedback and Whisper transcription. Text-to-speech is implemented with gTTS and is available as a reusable utility for future UI features.
