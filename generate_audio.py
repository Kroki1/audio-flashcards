import hashlib
import io
import os
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv
from pydub import AudioSegment

# ==============================================================================
# CONFIGURATION & TIMING CONTROLS (Edit these to calibrate pacing)
# ==============================================================================
load_dotenv()

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
CARTESIA_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_VERSION = "2025-04-16"
MODEL_ID = "sonic-3.6"  # Update to "sonic-3" if your account uses the alias

# Replace these with your chosen Voice IDs from the Cartesia Playground
VOICE_IDS = {
    "en": "47c38ca4-5f35-497b-b1a3-415245fb35e1",  # Daniel - Modern Assistant (English)
    "sv": "bcdcad6d-4eb6-4a71-89fd-1ae2ce9f95d8",  # Freja - Informative Host (Swedish)
}

# Pause durations in milliseconds
PAUSES_MS = {
    "after_intro": 1500,        # After episode intro or section transition
    "after_en_prompt": 600,     # English prompt -> Swedish infinitive
    "between_forms": 500,       # Infinitive -> Imperative -> Present -> Past -> Perfect
    "between_verbs": 1800,      # Perfect -> Next verb's English prompt
}

SAMPLE_RATE = 44100
MP3_BITRATE = "192k"

INPUT_YAML = Path("sample_5_verbs.yaml")
OUTPUT_DIR = Path("output")
CACHE_DIR = Path(".cache_tts")


# ==============================================================================
# TTS & AUDIO HELPERS
# ==============================================================================
def silence(duration_ms: int) -> AudioSegment:
    """Generates exact digital silence matching our target sample rate."""
    return AudioSegment.silent(duration=duration_ms, frame_rate=SAMPLE_RATE)


def synthesize_speech(text: str, lang: str) -> AudioSegment:
    """Fetches TTS audio from Cartesia with local disk caching."""
    if not CARTESIA_API_KEY:
        raise RuntimeError("Missing CARTESIA_API_KEY in environment or .env file.")

    voice_id = VOICE_IDS[lang]
    cache_key = hashlib.sha256(
        f"{MODEL_ID}|{voice_id}|{lang}|{SAMPLE_RATE}|{text}".encode("utf-8")
    ).hexdigest()
    cache_path = CACHE_DIR / f"{cache_key}.wav"

    if cache_path.exists():
        return AudioSegment.from_wav(cache_path)

    headers = {
        "X-API-Key": CARTESIA_API_KEY,
        "Cartesia-Version": CARTESIA_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "model_id": MODEL_ID,
        "transcript": text,
        "voice": {
            "mode": "id",
            "id": voice_id,
        },
        "language": lang,
        "output_format": {
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": SAMPLE_RATE,
        },
    }

    response = requests.post(CARTESIA_URL, headers=headers, json=payload, timeout=30)
    if not response.ok:
        raise RuntimeError(
            f"Cartesia API error ({response.status_code}) for '{text}': {response.text}"
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(response.content)
    return AudioSegment.from_wav(io.BytesIO(response.content))


# ==============================================================================
# EPISODE BUILDER
# ==============================================================================
def build_episode(episode_data: dict) -> Path:
    ep_num = episode_data["episode"]
    print(f"\n--- Building Episode {ep_num}: {episode_data['title']} ---")

    track = silence(500)  # Brief leading buffer

    # 1. Episode Intro
    intro = episode_data.get("intro")
    if intro:
        print(f"[INTRO - {intro['lang']}] {intro['text']}")
        track += synthesize_speech(intro["text"], intro["lang"])
        track += silence(PAUSES_MS["after_intro"])

    # 2. Iterate through verbs (and any mid-episode section transitions)
    verbs = episode_data.get("verbs", [])
    for idx, item in enumerate(verbs, start=1):
        # Handle merged-group transition markers (e.g., Group 4 -> Group 5)
        if "section_transition" in item:
            trans = item["section_transition"]
            print(f"\n[TRANSITION - {trans['lang']}] {trans['text']}")
            track += synthesize_speech(trans["text"], trans["lang"])
            track += silence(PAUSES_MS["after_intro"])
            continue

        print(f"({idx}/{len(verbs)}) {item['en']} -> {item['infinitive']['text']}")

        # Step A: English prompt
        track += synthesize_speech(item["en"], "en")
        track += silence(PAUSES_MS["after_en_prompt"])

        # Step B: Five grammatical slots in sequence
        slots = ["infinitive", "imperative", "present", "past", "perfect"]
        for slot_idx, slot_name in enumerate(slots):
            slot = item[slot_name]
            track += synthesize_speech(slot["text"], slot["lang"])

            if slot_idx < len(slots) - 1:
                track += silence(PAUSES_MS["between_forms"])
            else:
                track += silence(PAUSES_MS["between_verbs"])

    # 3. Export to MP3
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"episode_{ep_num:02d}.mp3"
    track.export(out_file, format="mp3", bitrate=MP3_BITRATE)
    duration_sec = len(track) / 1000.0
    print(f"Exported: {out_file} ({duration_sec:.1f}s)")
    return out_file


def main():
    with open(INPUT_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for ep in data.get("episodes", []):
        build_episode(ep)


if __name__ == "__main__":
    main()