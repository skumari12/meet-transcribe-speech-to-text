from flask import Flask, render_template, request, send_file
import os
from openai import OpenAI

# Ensure API key exists
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)

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
        try:
            file = request.files.get("file")

            if not file or file.filename == "":
                return render_template("index.html", transcript="⚠️ Please upload a valid file")

            # Save file safely
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Call API
            with open(filepath, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio
                )

            transcript = response.text

            # Save transcript
            output_path = os.path.join(OUTPUT_FOLDER, "transcript.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)

        except Exception as e:
            transcript = f"❌ ERROR: {str(e)}"

        finally:
            # Always delete uploaded file
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)

    return render_template("index.html", transcript=transcript)


@app.route("/download")
def download():
    try:
        path = os.path.join(OUTPUT_FOLDER, "transcript.txt")
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        return "⚠️ No transcript available"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)