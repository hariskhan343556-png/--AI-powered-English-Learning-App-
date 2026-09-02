"""
utils.py
Helper functions for English Coach 2.0:
- Spell checking (pyspellchecker)
- AI writing/speaking feedback (Groq LLM)
- Audio transcription (Groq-hosted Whisper)
- Text-to-speech (gTTS)
"""

import io
import json
import re

from spellchecker import SpellChecker
from gtts import gTTS
from groq import Groq


# ---------------------------------------------------------------------------
# Spell checking
# ---------------------------------------------------------------------------

_spell = SpellChecker()


def check_spelling(text: str):
    """
    Returns a list of dicts: [{"word": "...", "suggestion": "..."}]
    for words that appear misspelled. Ignores punctuation, numbers, and
    single-letter tokens.
    """
    words = re.findall(r"[A-Za-z']+", text)
    candidates = [w for w in words if len(w) > 1]

    misspelled = _spell.unknown([w.lower() for w in candidates])
    results = []
    seen = set()
    for w in candidates:
        lw = w.lower()
        if lw in misspelled and lw not in seen:
            seen.add(lw)
            suggestion = _spell.correction(lw)
            results.append({"word": w, "suggestion": suggestion or "(no suggestion)"})
    return results


# ---------------------------------------------------------------------------
# Groq client helpers
# ---------------------------------------------------------------------------

def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


TEST_RUBRICS = {
    "IELTS": (
        "Evaluate as an IELTS examiner using the four official band criteria: "
        "Task Achievement/Response, Coherence & Cohesion, Lexical Resource, "
        "and Grammatical Range & Accuracy. Give an estimated band score (0-9, "
        "in 0.5 increments) for each criterion and an overall band."
    ),
    "PTE": (
        "Evaluate as a PTE Academic scorer using the criteria: Content, "
        "Grammar, Vocabulary, and Form/Spelling. Give an estimated score "
        "out of 90 for each criterion and an overall score."
    ),
    "DET": (
        "Evaluate as a Duolingo English Test (DET) scorer using the "
        "sub-scores: Literacy, Conversation, Comprehension, and Production. "
        "Give an estimated score for each on the DET 10-160 scale and an "
        "overall score."
    ),
}


def get_writing_feedback(client: Groq, model: str, test_type: str, prompt: str, essay: str) -> dict:
    """
    Sends the essay to the LLM and asks for structured JSON feedback.
    """
    rubric = TEST_RUBRICS.get(test_type, TEST_RUBRICS["IELTS"])

    system_msg = (
        "You are an expert English language test coach. "
        f"{rubric} "
        "Always respond with STRICT valid JSON only, no markdown fences, "
        "no commentary outside the JSON. Use this schema:\n"
        "{\n"
        '  "scores": {"<criterion>": <number>, ...},\n'
        '  "overall_score": <number or string>,\n'
        '  "strengths": ["...", "..."],\n'
        '  "weaknesses": ["...", "..."],\n'
        '  "corrected_text": "the essay rewritten with grammar/word-choice '
        'fixes, keeping the student\'s ideas and voice",\n'
        '  "actionable_tips": ["...", "...", "..."]\n'
        "}"
    )

    user_msg = (
        f"Test type: {test_type}\n"
        f"Task prompt given to student: {prompt or '(no prompt provided)'}\n\n"
        f"Student's essay:\n\"\"\"\n{essay}\n\"\"\""
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        max_tokens=1500,
    )

    raw = completion.choices[0].message.content.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fall back to returning raw text if the model didn't produce clean JSON
        return {"raw_response": raw}


def get_speaking_feedback(client: Groq, model: str, test_type: str, prompt: str, transcript: str) -> dict:
    """
    Same idea as writing feedback, but tuned for spoken-language transcripts
    (fluency, filler words, coherence, vocabulary, grammar under time pressure).
    """
    rubric = TEST_RUBRICS.get(test_type, TEST_RUBRICS["IELTS"])

    system_msg = (
        "You are an expert English speaking test coach. "
        f"{rubric} "
        "You are given a transcript of a student's spoken answer (transcribed "
        "by Whisper). Judge fluency, coherence, vocabulary, grammar, and "
        "pronunciation risk (infer likely pronunciation issues from spelling "
        "patterns, repeated words, and filler words like 'um', 'uh', 'like'). "
        "Always respond with STRICT valid JSON only, no markdown fences. "
        "Schema:\n"
        "{\n"
        '  "scores": {"<criterion>": <number>, ...},\n'
        '  "overall_score": <number or string>,\n'
        '  "fluency_notes": "...",\n'
        '  "filler_word_count": <number>,\n'
        '  "strengths": ["...", "..."],\n'
        '  "weaknesses": ["...", "..."],\n'
        '  "model_answer": "a strong sample answer to the same prompt",\n'
        '  "actionable_tips": ["...", "...", "..."]\n'
        "}"
    )

    user_msg = (
        f"Test type: {test_type}\n"
        f"Speaking prompt: {prompt or '(no prompt provided)'}\n\n"
        f"Transcript of student's answer:\n\"\"\"\n{transcript}\n\"\"\""
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        max_tokens=1500,
    )

    raw = completion.choices[0].message.content.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_response": raw}


def get_personalized_plan(client: Groq, model: str, test_type: str, history_summary: str) -> str:
    """
    Generates a personalized study plan based on a summary of the user's
    recent writing/speaking session results.
    """
    system_msg = (
        "You are a supportive, practical English test-prep coach. "
        "Based on the student's recent session history, write a short, "
        "encouraging, personalized study plan (5-7 bullet points) targeting "
        f"their weakest areas for the {test_type} exam. Be specific and "
        "actionable, not generic."
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": history_summary},
        ],
        temperature=0.5,
        max_tokens=600,
    )
    return completion.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Whisper transcription (via Groq's hosted Whisper endpoint)
# ---------------------------------------------------------------------------

def transcribe_audio(client: Groq, audio_bytes: bytes, filename: str = "audio.wav",
                      whisper_model: str = "whisper-large-v3-turbo") -> str:
    """
    Sends audio bytes to Groq's Whisper transcription endpoint and returns
    the transcript text.
    """
    file_tuple = (filename, audio_bytes)
    transcription = client.audio.transcriptions.create(
        file=file_tuple,
        model=whisper_model,
        response_format="text",
    )
    # response_format="text" returns a plain string in the Groq SDK
    if isinstance(transcription, str):
        return transcription.strip()
    return getattr(transcription, "text", str(transcription)).strip()


# ---------------------------------------------------------------------------
# Text-to-speech
# ---------------------------------------------------------------------------

def text_to_speech(text: str, lang: str = "en") -> bytes:
    """
    Converts text to speech using gTTS and returns MP3 bytes.
    """
    tts = gTTS(text=text, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
