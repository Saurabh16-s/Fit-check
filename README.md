# FitCheck

Upload a photo of your outfit and get a score out of 10, a short tagline, what works, and one tweak. It runs entirely on a laptop through open models, with no GPU and no cloud, so the photo never leaves the machine.

Built for a friend for the DEV Hacktoberfest 2026 "Build for a Friend" challenge.

## How it works

1. **moondream** (via Ollama) looks at the photo and lists only the clothes and accessories.
2. **gemma3:1b** (via Ollama) reads that description and writes the score, tagline, and tips as JSON.
3. A **Gradio** page ties it together. Pick a personality: hype bestie, brutally honest, or fashion critic. A score guide shows what each range means.

Each model is unloaded right after use (`keep_alive=0`), so only one is in RAM at a time.

## Why open models

- Everything runs offline once the models are downloaded.
- The photo stays on the machine. The Gradio app listens on 127.0.0.1 only, with no share link and analytics turned off.
- The judge's personality is just a string in `modes.py`, so changing it or swapping a model is a one-line edit with no retraining.

## Setup (Windows, tested on 8 GB RAM, no GPU)

1. Install Ollama from https://ollama.com/download
2. Pull the models:

        ollama pull moondream
        ollama pull gemma3:1b

3. Install the Python packages. Use `python -m pip` so they go into the same Python you will run the app with:

        python -m pip install -r requirements.txt

4. Start the app and open http://127.0.0.1:7860

        python app.py

You can also test from the command line:

    python judge.py your-photo.jpg hype_bestie

Modes: `hype_bestie`, `brutally_honest`, `fashion_critic`.

## Measured on my laptop (8 GB RAM, CPU only)

| Setup | Time per photo |
|---|---|
| gemma3:4b alone (sees the photo directly) | about 4.5 minutes |
| moondream + gemma3:1b (this repo) | about 72 seconds |

## Known limits

- About a minute per photo on CPU.
- Moondream's descriptions are thin and can miss items, and the 1B text model can only judge what it is told.
- Small models tend to be generous with scores. The personas help, but they are not a fix.
- No fine-tuning was done. Behavior comes from prompts only.

## Files

- `app.py`: Gradio UI
- `judge.py`: describe, then judge, with JSON parsing and one retry
- `modes.py`: prompts and personalities

Photos are git-ignored on purpose. Please do not commit anyone's pictures.
