# 🎼 Symphony Conductor AI

A tool that analyzes an orchestra's live performance and provides real-time feedback on pitch and timing.

## Demo

🔗 **Live Demo:** [https://symphony-conductor-ai.onrender.com](https://symphony-conductor-ai.onrender.com)

## Features

- **Pitch Analysis** — note detection, frequency calculation, intonation cents
- **Interval Analysis** — identify intervals between notes with consonance/dissonance labels
- **Chord Recognition** — major, minor, diminished, augmented, 7ths, sus chords
- **Key Detection** — automatic key/scale identification with confidence percentage
- **Scale Reference** — major, minor, pentatonic, blues, dorian, mixolydian, phrygian, whole tone, chromatic
- **Tempo Analysis** — BPM calculation, beat duration, subdivision timing
- **Dynamics Analysis** — ppp through fff with visual levels, crescendo/diminuendo
- **Instrumentation** — 25+ instruments with section, range, and voice classification
- **Orchestra Balance** — section balance tips (brass vs strings, woodwind exposure)
- **Performance Feedback** — natural language analysis of issues (flat, sharp, rushing, muddy, etc.)
- **Interactive Piano** — click notes to build sequences
- **Analysis History** — stored locally, replay previous analyses
- **AI-Powered** — Groq/OpenRouter/HuggingFace with deterministic fallback

## Deploy on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Configure:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (optional, see below)
6. Click **Deploy**

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | No | Groq API key for LLM-powered analysis |
| `OPENROUTER_API_KEY` | No | OpenRouter API key (fallback) |
| `HUGGINGFACE_API_KEY` | No | HuggingFace Inference API key (fallback) |

All keys are optional. The app uses built-in deterministic music analysis if no keys are set or if API calls fail.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000

## API

**POST /solve**

Request:
```json
{"data": "C E G allegro violin ff"}
```

Response:
```json
{"output": "━━━ 🎼 PITCH ANALYSIS ━━━\nNotes: C → E → G\n..."}
```

## Tech Stack

- **Backend:** Python FastAPI
- **Frontend:** Single HTML file (no CSS frameworks)
- **AI:** Groq / OpenRouter / HuggingFace (optional)
- **Deployment:** Render free tier
