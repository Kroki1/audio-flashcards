# Audio Flashcards

A Python pipeline for creating bilingual English–Swedish audio lessons, exported as MP3 files. The initial goal is to cover approximately 120–150 Swedish irregular verbs across five or six episodes, grouped by verb pattern with around 25 verbs per episode.

## Lesson format

For each verb, the recording presents the English meaning, Swedish infinitive, imperative, and present, past, and perfect tense examples. Short pauses separate the phrases, with a longer pause between verbs. The timing can be tuned after reviewing a sample episode.

## Planned workflow

Lesson content will be maintained in a structured JSON or YAML file organized by episode and verb pattern. The Python pipeline will use Cartesia's `sonic-3.6` text-to-speech model, selecting English (`en`) for the English prompt and Swedish (`sv`) for the Swedish phrases. It will combine the generated audio with digital silence between phrases and export each episode as an MP3.