# EnglishAI Coach

EnglishAI Coach is a Streamlit application for improving English writing and speaking skills and practicing IELTS, PTE, and DET-style tasks.

## Features

- Writing analysis with grammar, vocabulary, clarity, and organization feedback
- Spelling analysis and suggestions
- Speaking transcription using Groq Whisper
- AI English tutor
- IELTS, PTE, and DET practice task generation
- AI evaluation of writing and speaking responses
- Text-to-speech feedback

## Project Structure

```text
EnglishAI-Coach-Professional/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── utils/
    ├── __init__.py
    ├── ai.py
    ├── spelling.py
    └── speech.py
```

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set your Groq API key as an environment variable:

```bash
GROQ_API_KEY=your_key_here
```

For Streamlit Community Cloud, add `GROQ_API_KEY` under the app Secrets settings.

## Streamlit Deployment

Use:

- Branch: `main`
- Main file path: `app.py`

Make sure `app.py` and the `utils` folder are in the repository root.

## Important

Never upload your API key to GitHub. Store it in Streamlit Secrets or an environment variable.
