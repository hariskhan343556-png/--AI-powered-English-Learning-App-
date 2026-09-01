# 🎓 EnglishAI Coach

An AI-powered English learning application built with Streamlit.

## Features

- Writing analysis and corrections
- Spell checking
- Speaking transcription with Whisper through Groq
- AI English tutor
- Text-to-speech with gTTS
- IELTS, PTE and DET practice
- Simple portfolio-friendly Streamlit interface

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API key

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Never commit this file to GitHub.

## Deployment

Push the project to GitHub and deploy `app.py` through Streamlit Community Cloud.
Add `GROQ_API_KEY` under the app's Secrets settings.
