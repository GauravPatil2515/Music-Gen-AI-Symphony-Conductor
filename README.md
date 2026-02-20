# 🎼 Symphony Conductor AI

A tool that analyzes an orchestra's live performance and provides real-time feedback on pitch and timing.

## Demo

🔗 **Live Demo:** [https://symphony-conductor-ai.onrender.com](https://symphony-conductor-ai.onrender.com)

## Features

- Analyzes musical notes (C, D, E, F, G, A, B with sharps/flats)
- Detects chord quality (major, minor, diminished, augmented)
- Calculates intervals between notes
- Recognizes tempo markings (largo, allegro, presto, etc.)
- Identifies instruments and provides section-specific advice
- AI-powered analysis when API keys are available
- Deterministic fallback — always works without external services

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
| `GROQ_API_KEY` | No | Groq API key for LLM analysis |
| `OPENROUTER_API_KEY` | No | OpenRouter API key |
| `HUGGINGFACE_API_KEY` | No | HuggingFace Inference API key |

All keys are optional. The app falls back to built-in deterministic analysis if no keys are set or if API calls fail.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000 in your browser.

## API

**POST /solve**

Request:
```json
{"data": "C E G allegro"}
```

Response:
```json
{"output": "🎼 Notes detected: C, E, G\n📊 Frequencies (Hz): 261.6, 329.6, 392.0\n🎹 Intervals: major 3rd, minor 3rd\n🏆 Chord quality: Major triad — bright and stable\n⏱️ Tempo: Allegro (~140 BPM)"}
```

## Tech Stack

- **Backend:** Python FastAPI
- **Frontend:** Single HTML file (no CSS frameworks)
- **AI:** Groq / OpenRouter / HuggingFace (optional)
- **Deployment:** Render free tier
