import os, re, random, math, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NOTES = {"C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13, "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00, "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88}
NOTE_LIST = list(NOTES.keys())
INTERVALS = {0: "unison", 1: "minor 2nd", 2: "major 2nd", 3: "minor 3rd", 4: "major 3rd", 5: "perfect 4th", 6: "tritone", 7: "perfect 5th", 8: "minor 6th", 9: "major 6th", 10: "minor 7th", 11: "major 7th", 12: "octave"}
TEMPO_MARKS = {"grave": (20, 40), "largo": (40, 60), "adagio": (60, 80), "andante": (80, 100), "moderato": (100, 120), "allegretto": (112, 130), "allegro": (120, 160), "vivace": (160, 180), "presto": (180, 220), "prestissimo": (220, 280)}
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "natural minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic minor": [0, 2, 3, 5, 7, 9, 11],
    "pentatonic major": [0, 2, 4, 7, 9],
    "pentatonic minor": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "whole tone": [0, 2, 4, 6, 8, 10],
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}
DYNAMICS = {"ppp": ("pianississimo", 1), "pp": ("pianissimo", 2), "p": ("piano", 3), "mp": ("mezzo-piano", 4), "mf": ("mezzo-forte", 5), "f": ("forte", 6), "ff": ("fortissimo", 7), "fff": ("fortississimo", 8)}
INSTRUMENTS = {"violin": ("strings", "A3-E7", "soprano"), "viola": ("strings", "C3-E6", "alto"), "cello": ("strings", "C2-C6", "tenor/bass"), "double bass": ("strings", "E1-G4", "bass"), "bass": ("strings", "E1-G4", "bass"), "flute": ("woodwinds", "C4-D7", "soprano"), "piccolo": ("woodwinds", "D5-C8", "soprano"), "oboe": ("woodwinds", "Bb3-A6", "soprano"), "clarinet": ("woodwinds", "D3-Bb6", "soprano"), "bassoon": ("woodwinds", "Bb1-Eb5", "bass"), "saxophone": ("woodwinds", "Bb3-F#6", "alto"), "trumpet": ("brass", "F#3-D6", "soprano"), "french horn": ("brass", "B1-F5", "alto"), "horn": ("brass", "B1-F5", "alto"), "trombone": ("brass", "E2-F5", "tenor"), "tuba": ("brass", "D1-F4", "bass"), "timpani": ("percussion", "D2-C4", "bass"), "snare": ("percussion", "N/A", "unpitched"), "drum": ("percussion", "N/A", "unpitched"), "cymbal": ("percussion", "N/A", "unpitched"), "triangle": ("percussion", "N/A", "unpitched"), "xylophone": ("percussion", "F4-C8", "soprano"), "marimba": ("percussion", "C2-C7", "full"), "piano": ("keyboard", "A0-C8", "full"), "harp": ("strings", "Cb1-G#7", "full"), "organ": ("keyboard", "C2-C7", "full"), "guitar": ("strings", "E2-E6", "alto"), "celesta": ("keyboard", "C4-C8", "soprano")}

def parse_notes(text):
    found = []
    for token in re.findall(r'[A-Ga-g][#b]?\d?', text):
        note = token[0].upper()
        if len(token) > 1 and token[1] in '#b':
            if token[1] == 'b':
                idx = NOTE_LIST.index(note) - 1 if note in NOTE_LIST else -1
                if idx >= 0:
                    note = NOTE_LIST[idx]
                else:
                    continue
            else:
                note += '#'
        if note in NOTES:
            found.append(note)
    return found

def detect_key(notes):
    if len(notes) < 3:
        return None
    indices = list(set(NOTE_LIST.index(n) for n in notes))
    best_key, best_scale, best_score = None, None, -1
    for root_idx in range(12):
        for scale_name, pattern in SCALES.items():
            shifted = set((root_idx + p) % 12 for p in pattern)
            score = len(set(indices) & shifted)
            if score > best_score:
                best_score = score
                best_key = NOTE_LIST[root_idx]
                best_scale = scale_name
    match_pct = round(best_score / len(set(indices)) * 100) if indices else 0
    return {"key": best_key, "scale": best_scale, "match": match_pct}

def get_chord_name(notes):
    if len(notes) < 3:
        return None
    indices = [NOTE_LIST.index(n) % 12 for n in notes[:4]]
    root = notes[0]
    ints = [(indices[i] - indices[0]) % 12 for i in range(len(indices))]
    chords = {(0, 4, 7): "major", (0, 3, 7): "minor", (0, 3, 6): "diminished", (0, 4, 8): "augmented", (0, 4, 7, 11): "major 7th", (0, 4, 7, 10): "dominant 7th", (0, 3, 7, 10): "minor 7th", (0, 3, 6, 9): "diminished 7th", (0, 3, 6, 10): "half-diminished 7th", (0, 4, 7, 9): "major 6th", (0, 5, 7): "sus4", (0, 2, 7): "sus2", (0, 4, 7, 14): "add9"}
    t = tuple(sorted(set(ints)))
    name = chords.get(t, None)
    if name:
        return f"{root} {name}"
    if len(ints) >= 3:
        d1 = ints[1]
        d2 = ints[2] - ints[1] if len(ints) > 2 else 0
        if d1 == 4 and d2 == 3:
            return f"{root} major"
        elif d1 == 3 and d2 == 4:
            return f"{root} minor"
        elif d1 == 3 and d2 == 3:
            return f"{root} diminished"
        elif d1 == 4 and d2 == 4:
            return f"{root} augmented"
    return f"{root} (unclassified voicing)"

def cents_between(f1, f2):
    if f1 <= 0 or f2 <= 0:
        return 0
    return round(1200 * math.log2(f2 / f1), 1)

def analyze_local(data):
    if not data or not data.strip():
        return "🎼 Welcome to Symphony Conductor AI!\n\n🎯 What you can do:\n• Enter notes: C E G B\n• Add tempo: allegro, 120 bpm\n• Name instruments: violin, trumpet, flute\n• Describe issues: sounds flat, too fast, brass too loud\n• Try dynamics: ff, pp, crescendo\n• Ask for scales: C major scale, A minor\n\n💡 Combine them: \"C E G allegro violin ff\""
    text = data.strip()
    lines = []
    notes = parse_notes(text)
    lower = text.lower()

    tempo = None
    bpm = None
    for mark, (lo, hi) in TEMPO_MARKS.items():
        if mark in lower:
            tempo = mark
            bpm = (lo + hi) // 2
            break
    bpm_match = re.search(r'(\d+)\s*bpm', lower)
    if bpm_match:
        bpm = int(bpm_match.group(1))
        for mark, (lo, hi) in TEMPO_MARKS.items():
            if lo <= bpm <= hi:
                tempo = mark
                break

    if notes:
        lines.append(f"━━━ 🎼 PITCH ANALYSIS ━━━")
        lines.append(f"Notes: {' → '.join(notes)}")
        freqs = [NOTES[n] for n in notes]
        lines.append(f"Frequencies: {', '.join(f'{f:.1f} Hz' for f in freqs)}")

        if len(notes) >= 2:
            lines.append("")
            lines.append("━━━ 🎹 INTERVAL ANALYSIS ━━━")
            for i in range(len(notes) - 1):
                idx1 = NOTE_LIST.index(notes[i])
                idx2 = NOTE_LIST.index(notes[i + 1])
                semitones = (idx2 - idx1) % 12
                name = INTERVALS.get(semitones, f"{semitones} semitones")
                c = cents_between(NOTES[notes[i]], NOTES[notes[i + 1]])
                consonance = "consonant" if semitones in [0, 3, 4, 5, 7, 8, 9, 12] else "dissonant"
                lines.append(f"  {notes[i]} → {notes[i+1]}: {name} ({semitones} st, {abs(c)} cents) [{consonance}]")

        if len(notes) >= 3:
            lines.append("")
            lines.append("━━━ 🏛️ HARMONY ━━━")
            chord = get_chord_name(notes)
            if chord:
                lines.append(f"Chord: {chord}")
            key_info = detect_key(notes)
            if key_info:
                lines.append(f"Likely key: {key_info['key']} {key_info['scale']} ({key_info['match']}% match)")
                if key_info['match'] < 70:
                    lines.append("⚠️ Low key confidence — chromatic or atonal passage detected")

        lines.append("")
        lines.append("━━━ 🎯 CONDUCTOR FEEDBACK ━━━")
        pitch_range = max(freqs) - min(freqs)
        if pitch_range < 30:
            lines.append("✅ Very tight voicing — excellent unison potential")
        elif pitch_range < 100:
            lines.append("✅ Close harmony — warm ensemble blend expected")
        elif pitch_range < 250:
            lines.append("📊 Moderate spread — ensure inner voices balance")
        else:
            lines.append("⚠️ Wide register spread ({:.0f} Hz) — watch intonation across octaves".format(pitch_range))

        unique_notes = list(set(notes))
        if len(unique_notes) != len(notes):
            doubled = [n for n in unique_notes if notes.count(n) > 1]
            lines.append(f"🔁 Doubled notes: {', '.join(doubled)} — check octave placement")

        if len(notes) == 1:
            lines.append("🎵 Single note — try adding more for harmony analysis")
        elif len(notes) == 2:
            lines.append("🎵 Dyad — add a third note for full chord identification")
        elif len(notes) <= 4:
            lines.append("🎵 Standard voicing — well suited for ensemble writing")
        else:
            lines.append("🎵 Dense voicing ({} notes) — subdivide for clarity".format(len(notes)))

    if tempo:
        lines.append("")
        lines.append("━━━ ⏱️ TEMPO & TIMING ━━━")
        lines.append(f"Marking: {tempo.capitalize()} (~{bpm} BPM)")
        beat_ms = round(60000 / bpm) if bpm else 0
        lines.append(f"Beat duration: {beat_ms} ms | Subdivision (16th): {beat_ms // 4} ms")
        if bpm < 60:
            lines.append("🐢 Very slow — sustain control and breath management critical")
            lines.append("💡 Risk: Pitch sag on long notes, loss of pulse")
        elif bpm < 100:
            lines.append("🚶 Moderate pace — room for expressive rubato")
            lines.append("💡 Focus on legato phrasing and dynamic shaping")
        elif bpm < 140:
            lines.append("🏃 Energetic tempo — maintain clean articulation")
            lines.append("💡 Ensure offbeats stay precise, avoid rushing")
        elif bpm < 180:
            lines.append("🏎️ Fast — prioritize rhythmic accuracy over nuance")
            lines.append("💡 Simplify bowings/tonguing for clarity at speed")
        else:
            lines.append("🚀 Extreme speed — technical precision paramount")
            lines.append("💡 Reduce dynamics to maintain control, rehearse slowly first")

    dyn_found = []
    for d, (name, level) in DYNAMICS.items():
        if re.search(r'\b' + re.escape(d) + r'\b', lower):
            dyn_found.append((d, name, level))
    cresc = "crescendo" in lower or "cresc" in lower
    decresc = "decrescendo" in lower or "decresc" in lower or "diminuendo" in lower
    if dyn_found or cresc or decresc:
        lines.append("")
        lines.append("━━━ 🔊 DYNAMICS ━━━")
        for d, name, level in dyn_found:
            bar = "█" * level + "░" * (8 - level)
            lines.append(f"  {d} ({name}): [{bar}] {level}/8")
        if cresc:
            lines.append("  📈 Crescendo — gradually increase intensity, keep pitch stable")
        if decresc:
            lines.append("  📉 Diminuendo — reduce volume while maintaining tone quality")

    found_instruments = {}
    for inst, (section, rng, voice) in INSTRUMENTS.items():
        if inst in lower:
            found_instruments[inst] = (section, rng, voice)
    if found_instruments:
        lines.append("")
        lines.append("━━━ 🎻 INSTRUMENTATION ━━━")
        sections = {}
        for inst, (sec, rng, voice) in found_instruments.items():
            sections.setdefault(sec, []).append(inst)
            lines.append(f"  {inst.title()}: {sec} | Range: {rng} | Voice: {voice}")
        lines.append("")
        lines.append("Section breakdown: " + " | ".join(f"{s}: {', '.join(i)}" for s, i in sections.items()))
        sec_keys = set(sections.keys())
        if "brass" in sec_keys and "strings" in sec_keys:
            lines.append("⚖️ Balance: Brass naturally louder — mark strings mf+ or brass p/mp")
        if "woodwinds" in sec_keys and "brass" in sec_keys:
            lines.append("⚖️ Balance: Woodwinds need exposed moments or dynamic support")
        if "percussion" in sec_keys:
            lines.append("🥁 Percussion will define rhythmic clarity — ensure tight coordination")
        if len(sec_keys) >= 3:
            lines.append("🎭 Full orchestration — conductor must shape balance between sections")
        if any(v == "soprano" for _, (_, _, v) in found_instruments.items()) and any(v == "bass" for _, (_, _, v) in found_instruments.items()):
            lines.append("📐 Wide voice range — middle voices (alto/tenor) crucial for blend")

    if not notes and not tempo and not found_instruments and not dyn_found:
        sentiments = {"beautiful": "positive", "great": "positive", "good": "positive", "excellent": "positive", "nice": "positive", "perfect": "positive", "bad": "negative", "wrong": "negative", "off": "negative", "terrible": "negative", "poor": "negative", "sharp": "sharp", "flat": "flat", "fast": "fast", "rushing": "fast", "slow": "slow", "dragging": "slow", "loud": "loud", "quiet": "soft", "soft": "soft", "muddy": "muddy", "thin": "thin", "bright": "bright", "dark": "dark", "harsh": "harsh", "warm": "warm"}
        found_s = []
        for w in lower.split():
            if w in sentiments:
                found_s.append(sentiments[w])

        scale_match = re.search(r'([A-Ga-g][#b]?)\s*(major|minor|blues|pentatonic|dorian|mixolydian|phrygian|chromatic|whole tone)', lower)
        if scale_match:
            root = scale_match.group(1)[0].upper()
            if len(scale_match.group(1)) > 1 and scale_match.group(1)[1] == '#':
                root += '#'
            scale_type = scale_match.group(2)
            scale_key = scale_type
            if scale_type == "major":
                scale_key = "major"
            elif scale_type == "minor":
                scale_key = "natural minor"
            if scale_key in SCALES and root in NOTE_LIST:
                root_idx = NOTE_LIST.index(root)
                scale_notes = [NOTE_LIST[(root_idx + s) % 12] for s in SCALES[scale_key]]
                lines.append(f"━━━ 🎵 SCALE: {root} {scale_type.upper()} ━━━")
                lines.append(f"Notes: {' '.join(scale_notes)}")
                freqs = [NOTES[n] for n in scale_notes]
                lines.append(f"Frequencies: {', '.join(f'{f:.1f}' for f in freqs)}")
                lines.append(f"Pattern: {' '.join(str(s) for s in SCALES[scale_key])} (semitones from root)")
                if scale_type in ["major", "minor", "natural minor"]:
                    lines.append(f"Relative {'minor' if 'major' in scale_type else 'major'}: {NOTE_LIST[(root_idx + (9 if 'major' in scale_type else 3)) % 12]}")

        if found_s:
            lines.append("")
            lines.append("━━━ 🔧 PERFORMANCE FEEDBACK ━━━")
            feedback_map = {
                "positive": "👍 Positive assessment — maintain current approach and energy",
                "negative": "🔧 Issues detected — isolate problem passages, drill slowly with metronome",
                "sharp": "📐 Sharp intonation — relax embouchure, extend slides, use less air pressure",
                "flat": "📐 Flat intonation — increase air support, shorten slides, firm embouchure",
                "fast": "⏩ Rushing tendency — internalize subdivision, anchor to bass pulse",
                "slow": "⏪ Dragging tendency — feel forward motion, anticipate beats slightly",
                "loud": "🔊 Excessive volume — reduce intensity, listen across the ensemble",
                "soft": "🔉 Insufficient projection — increase air support, maintain tone core",
                "muddy": "🌫️ Lack of clarity — lighten articulation, reduce pedal, separate voices",
                "thin": "📏 Thin sound — add vibrato, use fuller bow/air, check doubling",
                "bright": "☀️ Bright timbre — good for projecting melody; soften for blending",
                "dark": "🌙 Dark timbre — rich and warm; increase for bass, lighten for solos",
                "harsh": "⚡ Harsh tone — ease up on attack, use softer articulation",
                "warm": "🔥 Warm tone — beautiful quality, ideal for lyrical passages",
            }
            for s in set(found_s):
                if s in feedback_map:
                    lines.append(feedback_map[s])

        if not lines:
            lines.append(f"🎵 Input: \"{text[:100]}\"")
            lines.append("")
            lines.append("━━━ 💡 SUGGESTIONS ━━━")
            lines.append("Try any of these inputs:")
            lines.append("  • Notes: C E G B — chord & harmony analysis")
            lines.append("  • Tempo: allegro, 120 bpm — timing feedback")
            lines.append("  • Instruments: violin trumpet flute — orchestration tips")
            lines.append("  • Dynamics: ff pp crescendo — dynamic analysis")
            lines.append("  • Scales: C major scale, A minor — scale reference")
            lines.append("  • Feedback: sounds sharp, too fast, brass loud — conductor advice")
            lines.append("  • Combine: C E G allegro violin ff — full analysis")

    return "\n".join(lines)

class Req(BaseModel):
    data: str = ""

async def try_ai(data):
    if not data or not data.strip():
        return None
    prompt = f"""You are Symphony Conductor AI — an expert orchestra conductor analyzing live performance.

Analyze the following musical input and provide structured, actionable feedback.
Cover these areas as relevant:
- 🎼 Pitch: note accuracy, intonation, intervals, chord quality
- ⏱️ Timing: tempo, rhythm, synchronization
- 🏛️ Harmony: key detection, chord progression, voice leading
- 🎻 Instrumentation: section balance, range, blend
- 🔊 Dynamics: volume control, expression
- 🎯 Conductor recommendations: specific, practical advice

Use section headers with ━━━ formatting. Be concise but thorough. Use music emoji.

Input: {data}"""
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {groq_key}"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 700, "temperature": 0.7})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {openrouter_key}"}, json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 700})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")
    if hf_key:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", headers={"Authorization": f"Bearer {hf_key}"}, json={"inputs": prompt, "parameters": {"max_new_tokens": 400}})
                if r.status_code == 200:
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
