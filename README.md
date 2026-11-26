# audio-flashcards

A Python pipeline that generates bilingual (English + Swedish) audio lessons for Swedish irregular verbs. The output is MP3 episodes intended for publishing as an audio course on Spotify.

## Purpose

Learners hear an English meaning, then the Swedish forms of the verb, spoken with clear pauses in between. Each episode covers a group of about 25 verbs, and the verbs are grouped by their irregular conjugation pattern. The target is roughly 120–150 verbs, published as 5–6 episodes.

### Audio format (per verb)

| Step | Content | Language | Pause after |
|------|---------|----------|-------------|
| 1 | English prompt (e.g. `to write`) | `en` | 600 ms      |
| 2 | Swedish infinitive (`att skriva`) | `sv` | 600 ms      |
| 3 | Imperative (`skriv!`) | `sv` | 600 ms      |
| 4 | Present tense example (`Jag skriver nu.`) | `sv` | 600 ms      |
| 5 | Past tense example (`Jag skrev igår.`) | `sv` | 600 ms      |
| 6 | Perfect tense example (`Jag har skrivit idag.`) | `sv` | 1800 ms     |

Each episode may also start with an English intro, and a spoken section transition may separate verb groups. Pause lengths are configurable because the timing is still being calibrated with the sample set.

## How it works

1. Verb data is defined in a YAML file, grouped by episode (see `sample_5_verbs.yaml`).
2. `generate_audio.py` sends every spoken segment to the [Cartesia](https://cartesia.ai) TTS API (`sonic-3.6` model). English segments use `language="en"`, Swedish segments use `language="sv"`.
3. Returned WAV chunks are joined with digital silence of the configured lengths.
4. Each episode is exported to `output/episode_NN.mp3`.
5. Synthesized clips are cached in `.cache_tts/` (keyed by model, voice, language, sample rate and text), so re-running the script does not re-bill unchanged lines.

## Repository contents

| File | Description |
|------|-------------|
| `generate_audio.py` | Main pipeline: reads YAML, calls Cartesia, builds the audio track and exports MP3 episodes. |
| `list_voices.py` | Utility that lists Swedish-tagged Cartesia voices so you can pick voice IDs. |
| `sample_5_verbs.yaml` | Calibration sample with 5 verbs (write, become, crawl, scream, can) used to test pacing. |
| `requirements.txt` | Python dependencies. |
| `output/` | Generated MP3 episodes. |
| `LICENSE` | MIT License. |

## Input data format

```yaml
episodes:
  - episode: 0
    title: "Calibration Sample: 5 Verbs"
    intro:
      lang: "en"
      text: "Calibration sample. Five Swedish irregular verbs."
    verbs:
      - en: "to write"
        common: true
        infinitive: { lang: "sv", text: "att skriva" }
        imperative: { lang: "sv", text: "skriv!" }
        present:    { lang: "sv", text: "Jag skriver nu." }
        past:       { lang: "sv", text: "Jag skrev igår." }
        perfect:    { lang: "sv", text: "Jag har skrivit idag." }
```

Verbs with no imperative (e.g. modal verbs) can use an English note in the `imperative` slot, which is then spoken in English.

## Setup

Requirements:

- Python 3.9+
- [FFmpeg](https://ffmpeg.org) installed (required by `pydub` for MP3 export), e.g. `brew install ffmpeg` on macOS
- A Cartesia API key

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root (do not commit it):

```env
CARTESIA_API_KEY=your_api_key_here
```

## Usage

1. Find Swedish voice IDs (optional):

   ```bash
   python list_voices.py
   ```

2. Set `VOICE_IDS` (English and Swedish) in `generate_audio.py` to the voices you chose.

3. Generate episodes from the sample file:

   ```bash
   python generate_audio.py
   ```

   The script currently reads `sample_5_verbs.yaml` (set by `INPUT_YAML`) and writes `output/episode_00.mp3`.

Pause durations are defined in `PAUSES_MS` at the top of `generate_audio.py`.

## Notes

- Cartesia requests can incur costs. The local cache avoids repeating identical requests.
- `audioop-lts` is only needed on Python 3.13 and newer; it is harmless on older versions.
- `requirements.txt` currently starts with a stray `UNKNOWN` line, which should be removed before installing with pip.

## License

Released under the MIT License. See [LICENSE](LICENSE).
