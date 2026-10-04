import os
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"  # no telemetry

import html
import gradio as gr
from judge import describe, judge as run_judge

MODES = {
    "Hype bestie": "hype_bestie",
    "Brutally honest": "brutally_honest",
    "Fashion critic": "fashion_critic",
}
MAX_BYTES = 10 * 1024 * 1024

# (low, high, label, name, blurb) - edit these to change the score guide
TIERS = [
    (1, 3, "1&ndash;3", "Change the clothes", "Back to the wardrobe."),
    (4, 5, "4&ndash;5", "Needs work", "Good bones, rethink a piece or two."),
    (6, 7, "6&ndash;7", "Solid", "One tweak away from great."),
    (8, 8, "8", "Fire", "People will ask where it's from."),
    (9, 10, "9&ndash;10", "Greek god / goddess", "Statue-in-a-museum energy."),
]

MESSAGES = [  # keep exactly 6, the CSS timing assumes it
    "Counting your layers...",
    "Checking if the colors get along...",
    "Consulting the style council (it's one small model)...",
    "Judging the shoes, respectfully...",
    "Everything runs on this laptop. No cloud involved.",
    "Good fits take a minute. Almost there...",
]
SLOT = 4  # seconds each message stays on screen

CSS = """
body, .gradio-container { background: #faf9f6 !important; color-scheme: light;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif !important; }
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
footer { display: none !important; }
.fc-top { display: flex; align-items: center; justify-content: space-between; padding: 18px 4px 6px; }
.fc-logo { display: flex; align-items: center; gap: 10px; font-size: 1.7rem; font-weight: 800; color: #0b1626; }
.fc-logo b { color: #1b6b45; }
.fc-local { font-size: .85rem; color: #1b6b45; background: #e6f2ec; padding: 6px 14px; border-radius: 999px; font-weight: 600; }
.fc-badge { display: inline-block; background: #e6f2ec; color: #1b6b45; padding: 6px 14px; border-radius: 999px; font-weight: 600; font-size: .9rem; }
.fc-hero { font-size: 3rem; font-weight: 800; line-height: 1.08; color: #0b1626; margin: 14px 0 10px; }
.fc-hero span { color: #1b6b45; }
.fc-sub { color: #5a6577; font-size: 1.1rem; margin-bottom: 10px; }
#fc-upload { border: 2px dashed #a9cdb9 !important; border-radius: 20px !important; background: #f2f7f4 !important; }
.fc-hint { color: #7a8494; font-size: .85rem; text-align: center; margin: 4px 0 8px; }
#fc-btn { background: #1b6b45 !important; color: #fff !important; border: none !important;
  border-radius: 14px !important; font-weight: 700 !important; padding: 14px !important; }
.fc-card { background: #fff; border-radius: 24px; padding: 28px; box-shadow: 0 10px 40px rgba(15, 27, 45, .08); }
.fc-row { display: flex; justify-content: space-between; align-items: center; }
.fc-label { color: #3b4657; font-weight: 600; }
.fc-pill { background: #e6f2ec; border-radius: 16px; padding: 8px 20px; }
.fc-num { font-size: 2.6rem; font-weight: 800; color: #1b6b45; }
.fc-den { color: #5a6577; font-size: 1.2rem; }
.fc-bar { height: 10px; border-radius: 999px; background: #e8ece9; margin: 16px 0 22px; overflow: hidden; }
.fc-fill { height: 100%; background: #46c27d; border-radius: 999px; }
.fc-sec { display: flex; align-items: center; gap: 10px; font-size: 1.05rem; font-weight: 700; color: #0b1626; margin: 18px 0 6px; }
.fc-dot { width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: .8rem; background: #2fa66a; color: #fff; }
.fc-dot.tip { background: #fff3cf; }
.fc-copy { color: #4a5568; margin: 0 0 0 34px; line-height: 1.5; }
.fc-summary { background: #eef4f0; border-radius: 14px; padding: 14px 16px; color: #2d3b4e; font-weight: 600; }
.fc-seen { color: #8a93a1; font-size: .8rem; margin-top: 16px; }
.fc-empty { color: #7a8494; text-align: center; padding: 70px 10px; line-height: 1.7; }

/* loading state */
.fc-load { text-align: center; padding: 34px 10px 26px; }
.fc-spin { width: 54px; height: 54px; margin: 0 auto 18px; border-radius: 50%;
  border: 5px solid #e1ece5; border-top-color: #1b6b45; animation: fc-rot 1s linear infinite; }
.fc-step { color: #1b6b45; font-weight: 700; font-size: .85rem; letter-spacing: .06em; text-transform: uppercase; }
.fc-steplabel { color: #0b1626; font-weight: 700; font-size: 1.2rem; margin: 4px 0 18px; }
.fc-shimmer { height: 8px; border-radius: 999px; margin: 0 auto 22px; max-width: 320px;
  background: linear-gradient(90deg, #e8ece9 0%, #46c27d 50%, #e8ece9 100%); background-size: 200% 100%;
  animation: fc-slide 1.6s ease-in-out infinite; }
.fc-msgs { position: relative; height: 3.2em; }
.fc-msg { position: absolute; left: 0; right: 0; color: #5a6577; font-size: 1rem; line-height: 1.4;
  opacity: 0; animation-name: fc-cycle; animation-iteration-count: infinite; animation-fill-mode: both; }
@keyframes fc-rot { to { transform: rotate(360deg); } }
@keyframes fc-slide { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
@keyframes fc-cycle {
  0% { opacity: 0; transform: translateY(6px); }
  2% { opacity: 1; transform: none; }
  13% { opacity: 1; transform: none; }
  16% { opacity: 0; transform: translateY(-6px); }
  100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) { .fc-spin, .fc-shimmer, .fc-msg { animation-duration: 0s; } }

/* score guide */
.fc-legend-title { text-align: center; font-weight: 800; color: #0b1626; font-size: 1.2rem; margin: 34px 0 14px; }
.fc-legend { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.fc-tier { background: #fff; border: 1px solid #e3e8e5; border-radius: 18px; padding: 16px 12px; text-align: center; transition: all .2s; }
.fc-range { font-size: 1.5rem; font-weight: 800; color: #1b6b45; }
.fc-tname { font-weight: 700; color: #0b1626; margin: 4px 0; }
.fc-tblurb { color: #6b7686; font-size: .85rem; line-height: 1.35; }
.fc-tier.active { background: #1b6b45; border-color: #1b6b45; transform: scale(1.04); box-shadow: 0 8px 24px rgba(27, 107, 69, .3); }
.fc-tier.active .fc-range, .fc-tier.active .fc-tname { color: #fff; }
.fc-tier.active .fc-tblurb { color: #d6eadf; }
.fc-foot { text-align: center; color: #8a93a1; font-size: .8rem; margin: 22px 0 10px; }
@media (max-width: 760px) { .fc-legend { grid-template-columns: 1fr 1fr; } .fc-hero { font-size: 2.2rem; } }
/* score guide in right column */
.fc-legend-title { text-align: left; font-size: 1.1rem; margin: 24px 4px 12px; }
.fc-legend { display: flex; flex-direction: column; gap: 10px; }
.fc-tier { display: grid; grid-template-columns: 84px 1fr; column-gap: 14px; align-items: center;
  text-align: left; padding: 12px 16px; border-radius: 16px; }
.fc-range { grid-row: 1 / span 2; font-size: 1.35rem; text-align: center; }
.fc-tname { margin: 0; }
.fc-tier.active { transform: scale(1.02); }
"""

HEADER = """
<div class="fc-top">
  <div class="fc-logo">
    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#0b1626" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7a2.5 2.5 0 1 0-2.5-2.5"/><path d="M12 7v2.2"/><path d="M12 9.2 3.2 15.4a1.6 1.6 0 0 0 .95 2.9h15.7a1.6 1.6 0 0 0 .95-2.9L12 9.2z"/></svg>
    <span>Fit<b>Check</b></span>
  </div>
  <span class="fc-local">Runs locally &middot; Gemma + moondream</span>
</div>
"""

HERO = """
<span class="fc-badge">&#10022; AI Outfit Review</span>
<h1 class="fc-hero">Upload Your Outfit,<br><span>Get Honest Feedback.</span></h1>
<p class="fc-sub">Find out how your outfit looks and get simple, practical suggestions to look better. Runs on this laptop, so your photo never leaves it.</p>
"""

FOOT = '<div class="fc-foot">Open models on a CPU-only laptop &middot; Ollama serves Gemma 3 1B (writes the verdict) and moondream (reads the photo)</div>'

def card(inner):
    return '<div class="fc-card">' + inner + '</div>'

def note(text):
    return card('<div class="fc-empty">' + text + '</div>')

def loading(step, label):
    total = len(MESSAGES) * SLOT
    msgs = "".join(
        f'<span class="fc-msg" style="animation-duration:{total}s;animation-delay:{i * SLOT}s">{m}</span>'
        for i, m in enumerate(MESSAGES)
    )
    return card(
        '<div class="fc-load"><div class="fc-spin"></div>'
        f'<div class="fc-step">{step}</div><div class="fc-steplabel">{label}</div>'
        f'<div class="fc-shimmer"></div><div class="fc-msgs">{msgs}</div></div>'
    )

def legend(score=None):
    items = ""
    for lo, hi, rng, name, blurb in TIERS:
        active = " active" if score and lo <= score <= hi else ""
        items += (f'<div class="fc-tier{active}"><div class="fc-range">{rng}</div>'
                  f'<div class="fc-tname">{name}</div><div class="fc-tblurb">{blurb}</div></div>')
    return '<div class="fc-legend-title">What the score means</div><div class="fc-legend">' + items + '</div>'

EMPTY = note("Your rating will show up here.<br>Upload a photo and press <b>Rate my fit</b>.")

def render(r):
    e = html.escape
    score = int(r.get("score", 0))
    if score == 0:
        return note("The judge got confused. Try again or pick another photo.")
    return card(f"""
      <div class="fc-row">
        <span class="fc-label">Overall Rating</span>
        <span class="fc-pill"><span class="fc-num">{score}</span><span class="fc-den"> / 10</span></span>
      </div>
      <div class="fc-bar"><div class="fc-fill" style="width:{score * 10}%"></div></div>
      <div class="fc-sec"><span class="fc-dot">&#10003;</span> What Looks Good</div>
      <p class="fc-copy">{e(str(r.get("what_works", "")))}</p>
      <div class="fc-sec"><span class="fc-dot tip">&#128161;</span> Suggestions</div>
      <p class="fc-copy">{e(str(r.get("one_tweak", "")))}</p>
      <div class="fc-sec">Style Summary</div>
      <div class="fc-summary">{e(str(r.get("tagline", "")))}</div>
      <details class="fc-seen"><summary>What the AI saw</summary>{e(str(r.get("description", "")))}</details>
    """)

def run(image_path, mode_label):
    if not image_path:
        yield note("Upload a photo first."), legend()
        return
    if os.path.getsize(image_path) > MAX_BYTES:
        yield note("That file is over 10 MB. Try a smaller photo."), legend()
        return
    try:
        yield loading("Step 1 of 2", "Looking at your outfit (about a minute)"), legend()
        description = describe(image_path)
        yield loading("Step 2 of 2", "Writing your verdict (about 10 seconds)"), legend()
        result = run_judge(description, MODES[mode_label])
        result["description"] = description
    except Exception as ex:
        yield note("Could not reach the models. Is Ollama running?<br><small>" + html.escape(str(ex)) + "</small>"), legend()
        return
    yield render(result), legend(int(result.get("score", 0)))

with gr.Blocks(title="FitCheck", css=CSS, theme=gr.themes.Base(),
               js="() => { document.body.classList.remove('dark'); }") as demo:
    gr.HTML(HEADER)
    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            gr.HTML(HERO)
            img = gr.Image(type="filepath", show_label=False, sources=["upload"], height=300, elem_id="fc-upload")
            gr.HTML('<div class="fc-hint">Supports JPG, PNG (max 10 MB)</div>')
            mode = gr.Dropdown(list(MODES.keys()), value="Hype bestie", label="Judge personality")
            btn = gr.Button("Rate my fit", variant="primary", elem_id="fc-btn")
        with gr.Column(scale=5):
            out = gr.HTML(EMPTY)
            legend_out = gr.HTML(legend())
    gr.HTML(FOOT)
    btn.click(run, inputs=[img, mode], outputs=[out, legend_out], show_progress="hidden")

demo.launch(server_name="127.0.0.1", share=False)
