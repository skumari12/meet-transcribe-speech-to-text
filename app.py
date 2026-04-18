from flask import Flask, render_template, request, send_file
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Limit file size (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("index.html", transcript="⚠️ No file uploaded")

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            # 🔥 API CALL (NO LOCAL MODEL)
            with open(filepath, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file
                )

            transcript = response.text

            # Save transcript
            output_path = os.path.join(OUTPUT_FOLDER, "transcript.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)

        except Exception as e:
            transcript = f"❌ Error: {str(e)}"

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template("index.html", transcript=transcript)


@app.route("/download")
def download():
    path = os.path.join(OUTPUT_FOLDER, "transcript.txt")
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "⚠️ No transcript available"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)