# FitCheck: Google Gemma 3 writes the verdict

Upload a photo of your outfit and get a score out of 10, a tagline, what works, and one tweak. **Every score and every line of feedback is written by Google Gemma 3, Google's open-weight model**, running locally on a CPU-only laptop with 8 GB of RAM. No cloud, no API key, no GPU.

Built for a friend for the DEV Hacktoberfest 2026 "Build for a Friend" challenge (Best Use of Gemma)

## Google Gemma is the core

- **Google Gemma 3 1B is the judge.** It reads an outfit description and returns the score, tagline, "what looks good", and the suggestion as structured JSON, in the personality you pick.
- **Google Gemma's personality is plain text.** Hype bestie, brutally honest, and fashion critic are prompt strings in `modes.py`. Changing how Google Gemma judges is a text edit, with no retraining and no account.
- **Google Gemma 3 4B came first.** It can look at the photo itself and worked, but took about 4.5 minutes per photo on this laptop. Giving Google Gemma 1B only the text part cut that to about 72 seconds. With more RAM, change `TEXT_MODEL` in `judge.py` to a bigger Google Gemma and compare.
- **A small helper reads the photo.** Google Gemma 3 1B is text-only, so moondream first lists the clothes in the picture, then unloads to free memory. It is the only non-Gemma model in the app.

## Why open-weight Google Gemma mattered here

- Runs fully offline once the weights are downloaded.
- The photo stays on the machine. The page listens on 127.0.0.1 only, with no share link and analytics turned off.
- Swapping the model or rewriting the judge takes one line, not a new vendor.

## Measured on an 8 GB, CPU-only laptop

| Setup | Time per photo |
|---|---|
| Google Gemma 3 4B alone (sees the photo directly) | about 4.5 minutes |
| moondream + Google Gemma 3 1B (this repo) | about 72 seconds |

## Setup (Windows)

1. Install [Ollama](https://ollama.com/download) (it downloads and runs the models locally).
2. Get the models:

```
ollama pull gemma3:1b
ollama pull moondream
```

3. Install the Python packages. Use `python -m pip` so they go into the same Python you will run the app with:

```
python -m pip install -r requirements.txt
```

4. Start the app and open http://127.0.0.1:7860

```
python app.py
```

Command-line test: `python judge.py your-photo.jpg hype_bestie` (modes: `hype_bestie`, `brutally_honest`, `fashion_critic`).

## Known limits

- About a minute per photo on CPU.
- moondream's descriptions are thin and can miss items, and Google Gemma 1B can only judge what it is told.
- Small models tend to be generous with scores. The personas help, but they are not a fix.

## Files

- `app.py`: web page
- `judge.py`: moondream describes, Google Gemma judges, with JSON parsing and one retry
- `modes.py`: Google Gemma's prompts and personalities

Photos are git-ignored on purpose. Please do not commit anyone's pictures.
