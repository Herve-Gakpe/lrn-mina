# 🛡️ SRC SHIELD — Flask API for triggering the video processing pipeline
# This file runs a server to receive YouTube links and launch download_and_process.py

from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route("/")
def health_check():
    return "✅ LRN-MINA server is running"

@app.route("/process", methods=["POST"])
def process_video():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    try:
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "download_and_process.py"))
        result = subprocess.run(
            ["python", script_path, url],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        output_json = json.loads(result.stdout)
        return jsonify(output_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    