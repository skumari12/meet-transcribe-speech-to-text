import streamlit as st
import whisper
import tempfile
import os
from transformers import pipeline

# Fix for ffmpeg
os.environ["PATH"] += os.pathsep + "ffmpeg"

st.set_page_config(page_title="Meet Transcribe", layout="centered")

st.title("🎤 Meet Transcribe (Live)")

# Load model
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# Load summarizer
@st.cache_resource
def load_summary():
    return pipeline("summarization")

summarizer = load_summary()

# Upload
uploaded_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        path = tmp.name

    # Transcription
    with st.spinner("Transcribing..."):
        result = model.transcribe(path)
        text = result["text"]

    st.subheader("📝 Transcription")
    st.write(text)

    # Summary
    with st.spinner("Generating Summary..."):
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]

    st.subheader("📌 Summary")
    st.write(summary)

    # Download
    st.download_button("Download Text", text, file_name="output.txt")

    os.remove(path)