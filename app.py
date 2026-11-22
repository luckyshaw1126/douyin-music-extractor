from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def home():
    return "Douyin Music Extractor API is Running!"

@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    if not data or "link" not in data:
        return jsonify({"error": "Missing link"}), 400

    url = data.get("link")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "/tmp/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            # 核心修正：强制提取音频并转为MP3，音质设为192kbps
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
            title = info.get("title", "audio")
            
            # 转换后的MP3路径
            mp3_path = f"/tmp/{video_id}.mp3"

            if os.path.exists(mp3_path):
                # 核心修正：将MP3读入内存并以文件流形式返回
                with open(mp3_path, "rb") as f:
                    audio_data = BytesIO(f.read())
                
                # 清理服务器上的临时文件
                os.remove(mp3_path)
                
                # 返回真正的MP3文件流
                return send_file(
                    audio_data,
                    mimetype="audio/mpeg",
                    as_attachment=True,
                    download_name=f"{title}.mp3"
                )
            else:
                return jsonify({"error": "Audio conversion failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
