import gradio as gr
import os
from openai import OpenAI

# Load API key from environment
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


def transcribe_audio(file):
    if not client:
        return "❌ API key not set"

    if file is None:
        return "⚠️ Please upload an audio file"

    try:
        with open(file, "rb") as audio:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio
            )
        return response.text

    except Exception as e:
        return f"❌ Error: {str(e)}"


# Gradio UI
app = gr.Interface(
    fn=transcribe_audio,
    inputs=gr.Audio(type="filepath", label="Upload Audio (.mp3, .wav, .m4a)"),
    outputs=gr.Textbox(label="Transcript"),
    title="🎤 Meet Transcribe AI",
    description="Upload audio and get instant transcription"
)

app.launch()