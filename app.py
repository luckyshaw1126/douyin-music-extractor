from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Douyin Music Extractor Running!"

@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    url = data.get("link")

    if not url:
        return jsonify({"error": "Missing link"}), 400

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "/tmp/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return jsonify({
            "title": info.get("title"),
            "audio_file": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
