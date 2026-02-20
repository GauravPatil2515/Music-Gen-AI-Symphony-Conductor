import os, re, random, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NOTES = {"C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13, "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00, "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88}
INTERVALS = {"unison": 0, "minor 2nd": 1, "major 2nd": 2, "minor 3rd": 3, "major 3rd": 4, "perfect 4th": 5, "tritone": 6, "perfect 5th": 7, "minor 6th": 8, "major 6th": 9, "minor 7th": 10, "major 7th": 11, "octave": 12}
TEMPO_MARKS = {"largo": (40, 60), "adagio": (60, 80), "andante": (80, 100), "moderato": (100, 120), "allegro": (120, 160), "vivace": (160, 180), "presto": (180, 220)}

def parse_notes(text):
    found = []
    for token in re.findall(r'[A-Ga-g][#b]?\d?', text):
        note = token[0].upper()
        if len(token) > 1 and token[1] in '#b':
            note += token[1]
        if note in NOTES:
            found.append(note)
    return found

def analyze_local(data):
    if not data or not data.strip():
        return "🎵 Welcome to Symphony Conductor! Enter musical notes (e.g. C E G), a tempo marking (e.g. allegro), or describe your performance for analysis."
    text = data.strip()
    lines = []
    notes = parse_notes(text)
    lower = text.lower()
    tempo = None
    for mark, (lo, hi) in TEMPO_MARKS.items():
        if mark in lower:
            tempo = mark
            bpm = random.randint(lo, hi)
            break
    bpm_match = re.search(r'(\d+)\s*bpm', lower)
    if bpm_match:
        bpm = int(bpm_match.group(1))
        for mark, (lo, hi) in TEMPO_MARKS.items():
            if lo <= bpm <= hi:
                tempo = mark
                break
    if notes:
        lines.append(f"🎼 Notes detected: {', '.join(notes)}")
        freqs = [NOTES[n] for n in notes]
        lines.append(f"📊 Frequencies (Hz): {', '.join(f'{f:.1f}' for f in freqs)}")
        if len(notes) >= 2:
            intervals = []
            note_list = list(NOTES.keys())
            for i in range(len(notes) - 1):
                idx1 = note_list.index(notes[i])
                idx2 = note_list.index(notes[i + 1])
                semitones = (idx2 - idx1) % 12
                name = [k for k, v in INTERVALS.items() if v == semitones]
                intervals.append(name[0] if name else f"{semitones} semitones")
            lines.append(f"🎹 Intervals: {', '.join(intervals)}")
            if len(notes) >= 3:
                idx = [list(NOTES.keys()).index(n) % 12 for n in notes[:3]]
                d1 = (idx[1] - idx[0]) % 12
                d2 = (idx[2] - idx[1]) % 12
                if d1 == 4 and d2 == 3:
                    lines.append("🏆 Chord quality: Major triad — bright and stable")
                elif d1 == 3 and d2 == 4:
                    lines.append("🏆 Chord quality: Minor triad — dark and emotional")
                elif d1 == 3 and d2 == 3:
                    lines.append("🏆 Chord quality: Diminished triad — tense and unstable")
                elif d1 == 4 and d2 == 4:
                    lines.append("🏆 Chord quality: Augmented triad — dreamy and unresolved")
                else:
                    lines.append("🏆 Chord quality: Non-standard voicing — experimental texture")
        pitch_var = max(freqs) - min(freqs)
        if pitch_var < 50:
            lines.append("✅ Pitch analysis: Tight cluster — good unison or close harmony")
        elif pitch_var < 200:
            lines.append("✅ Pitch analysis: Moderate spread — balanced voicing")
        else:
            lines.append("⚠️ Pitch analysis: Wide spread — check for intonation drift")
        if len(set(notes)) == 1:
            lines.append("🎯 Timing tip: Unison passage — ensure all players lock rhythmically")
        elif len(notes) > 4:
            lines.append("🎯 Timing tip: Dense passage — conductor should subdivide beats clearly")
    if tempo:
        lines.append(f"⏱️ Tempo: {tempo.capitalize()} (~{bpm} BPM)")
        if bpm < 70:
            lines.append("💡 Slow tempo detected — watch for pitch sag on sustained notes")
        elif bpm > 160:
            lines.append("💡 Fast tempo detected — prioritize rhythmic precision over dynamics")
        else:
            lines.append("💡 Comfortable tempo — focus on expression and phrasing")
    if not notes and not tempo:
        keywords = {"violin": "strings", "viola": "strings", "cello": "strings", "bass": "strings", "flute": "woodwinds", "oboe": "woodwinds", "clarinet": "woodwinds", "bassoon": "woodwinds", "trumpet": "brass", "horn": "brass", "trombone": "brass", "tuba": "brass", "timpani": "percussion", "drum": "percussion", "piano": "keyboard", "harp": "strings"}
        found_instruments = [k for k in keywords if k in lower]
        if found_instruments:
            sections = set(keywords[i] for i in found_instruments)
            lines.append(f"🎻 Instruments: {', '.join(found_instruments)}")
            lines.append(f"📋 Sections involved: {', '.join(sections)}")
            if "strings" in sections and "brass" in sections:
                lines.append("⚖️ Balance tip: Brass may overpower strings — adjust dynamics")
            if "woodwinds" in sections:
                lines.append("🌬️ Woodwinds: Check tuning — temperature affects pitch")
            lines.append("🎯 Recommendation: Start with sectional rehearsal before full ensemble")
        else:
            words = text.split()
            lines.append(f"🎵 Input received: \"{text[:80]}\"")
            lines.append(f"📝 Word count: {len(words)}")
            tips = [
                "🎼 Tip: Try entering note names like C D E F G A B",
                "⏱️ Tip: Include tempo markings like 'allegro' or '120 bpm'",
                "🎻 Tip: Mention instruments for section-specific advice",
                "🎹 Tip: Enter chord patterns like 'C E G' for harmony analysis",
            ]
            lines.append(random.choice(tips))
            sentiments = {"beautiful": "positive", "great": "positive", "good": "positive", "bad": "negative", "wrong": "negative", "off": "negative", "sharp": "sharp", "flat": "flat", "fast": "fast", "slow": "slow", "loud": "loud", "soft": "soft", "quiet": "soft"}
            found_s = [sentiments[w] for w in lower.split() if w in sentiments]
            if found_s:
                feedback_map = {"positive": "👍 Performance sounds good — maintain current approach", "negative": "🔧 Issues noted — isolate problem sections and drill slowly", "sharp": "📐 Sharp intonation — relax embouchure or extend tuning slide", "flat": "📐 Flat intonation — increase air support or shorten tuning", "fast": "⏩ Rushing detected — use metronome and internalize subdivision", "slow": "⏪ Dragging detected — listen to the pulse and stay ahead slightly", "loud": "🔊 Dynamic too loud — back off and listen to the ensemble", "soft": "🔉 Dynamic too soft — project more but maintain tone quality"}
                for s in set(found_s):
                    lines.append(feedback_map.get(s, ""))
    return "\n".join(lines) if lines else "🎵 Symphony Conductor ready! Enter notes (C D E), tempo (allegro, 120 bpm), or instrument names for analysis."

class Req(BaseModel):
    data: str = ""

async def try_ai(data):
    prompt = f"You are a symphony orchestra conductor AI. Analyze this musical input and give concise, expert feedback on pitch, timing, harmony, and performance. Use music emoji. Input: {data}"
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {groq_key}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500})
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {openrouter_key}"}, json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500})
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")
    if hf_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", headers={"Authorization": f"Bearer {hf_key}"}, json={"inputs": prompt, "parameters": {"max_new_tokens": 300}})
                return r.json()[0]["generated_text"]
        except Exception:
            pass
    return None

@app.post("/solve")
async def solve(req: Req):
    data = req.data
    result = await try_ai(data)
    if not result:
        result = analyze_local(data)
    return JSONResponse({"output": result})

@app.get("/")
async def home():
    with open("index.html") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
