"""Optional Gradio browser demo."""
import tempfile
import gradio as gr
from rinvo.audio import to_wav_bytes
from rinvo.config import get_settings
from rinvo.engine import BackendUnavailableError, get_engine


def generate(text: str):
    settings = get_settings()
    if not text or not text.strip():
        raise gr.Error("Enter some text first.")
    if len(text) > settings.max_text_chars:
        raise gr.Error(f"Text exceeds the {settings.max_text_chars}-character limit.")
    try:
        result = get_engine().synthesize(text.strip())
        audio_bytes = to_wav_bytes(result.audio, result.sample_rate)
    except BackendUnavailableError as exc:
        raise gr.Error(str(exc)) from exc
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        handle.write(audio_bytes)
        return handle.name


with gr.Blocks(title="Rinvo — Give your words a voice") as demo:
    gr.Markdown("# Rinvo\nGive your words a voice. Self-hostable text-to-speech.")
    text_input = gr.Textbox(label="Text", placeholder="Welcome to Rinvo.", lines=5, max_lines=12)
    generate_button = gr.Button("Generate speech", variant="primary")
    output = gr.Audio(label="Generated speech", type="filepath")
    generate_button.click(generate, inputs=text_input, outputs=output)

if __name__ == "__main__":
    demo.launch()
