from flask import Flask, render_template, request, send_file
import whisper
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

model = whisper.load_model("base")  # small/medium for better accuracy

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""

    if request.method == "POST":
        file = request.files["file"]

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            result = model.transcribe(filepath)
            transcript = result["text"]

            # Save output
            output_path = os.path.join(OUTPUT_FOLDER, "transcript.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)

    return render_template("index.html", transcript=transcript)


@app.route("/download")
def download():
    return send_file("output/transcript.txt", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)