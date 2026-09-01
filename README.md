# EnglishAI Coach

EnglishAI Coach is a Streamlit application for English writing, speaking, conversation, and proficiency-exam practice.

## Technology

- Streamlit
- Groq API
- Whisper
- PySpellChecker
- gTTS

## Features

- Writing analysis
- Grammar and vocabulary feedback
- Spelling review
- Speaking transcription
- Speaking performance analysis
- AI English tutor
- IELTS practice
- PTE practice
- Duolingo English Test practice
- Text-to-speech feedback

## Local setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the Groq API key as an environment variable or Streamlit Secret.

Run:

```bash
streamlit run app.py
```

## Streamlit deployment

Deploy the repository using Streamlit Community Cloud.

Set:

```text
Branch: main
Main file path: app.py
```

Under Streamlit Secrets, add:

```toml
GROQ_API_KEY = "your_api_key"
```

Never commit API keys or Streamlit secrets to GitHub.
