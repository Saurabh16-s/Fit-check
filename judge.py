import io, json, re, sys, time
import ollama
from PIL import Image
from modes import DESCRIBE_PROMPT, get_prompt

VISION_MODEL = "moondream"
TEXT_MODEL = "gemma3:1b"

def prepare(path, max_side=384):
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

def describe(path):
    r = ollama.chat(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": DESCRIBE_PROMPT, "images": [prepare(path)]}],
        options={"num_ctx": 2048},
        keep_alive=0,  # unload right away to free RAM
    )
    return r["message"]["content"].strip()

def parse(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)  # strips ``` fences
    data = json.loads(match.group(0))
    data["score"] = max(1, min(10, int(data["score"])))
    return data

def judge(description, mode):
    for _ in range(2):  # one retry on bad JSON
        r = ollama.chat(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": get_prompt(mode, description)}],
            options={"num_ctx": 2048, "temperature": 0.4},
            keep_alive=0,
        )
        try:
            return parse(r["message"]["content"])
        except Exception:
            continue
    return {"score": 0, "tagline": "Judge got confused", "what_works": "", "one_tweak": "Try again."}

def rate(path, mode="hype_bestie"):
    print('Step 1/2: looking at the photo (about 1 minute)...', flush=True)
    description = describe(path)
    print('Step 2/2: writing the rating...', flush=True)
    result = judge(description, mode)
    result["description"] = description
    return result

if __name__ == "__main__":
    path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "hype_bestie"
    start = time.time()
    print(json.dumps(rate(path, mode), indent=2))
    print(f"\nTotal time: {time.time() - start:.1f}s")
