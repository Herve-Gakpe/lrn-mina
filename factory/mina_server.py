# 🛡️ SRC SHIELD — Flask API for triggering the video processing pipeline
# This file runs a server to receive YouTube links and launch download_and_process.py

from flask import Flask, request, jsonify
import subprocess
import json
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory for file access
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

@app.route("/")
def health_check() -> str:
    return "✅ LRN-MINA server is running"

@app.route("/process", methods=["POST"])
def process_video() -> Dict[str, Any]:
    """
    Process a YouTube video URL through the pipeline.
    
    Returns:
        Dict containing the processing results or error message
    """
    data = request.get_json()
    url = data.get("url")

    if not url:
        logger.warning("Received request without URL")
        return jsonify({"error": "Missing 'url' in request body"}), 400

    try:
        # Construct absolute path to the script
        script_path = os.path.join(BASE_DIR, "factory", "download_and_process.py")
        logger.info(f"Processing video from URL: {url}")
        logger.info(f"Using script path: {script_path}")

        # Run the processing script
        result = subprocess.run(
            ["python", script_path, url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=BASE_DIR  # Ensure script runs from project root
        )

        # Log the result
        if result.returncode != 0:
            logger.error(f"Script execution failed with return code {result.returncode}")
            logger.error(f"Script stderr: {result.stderr}")
            return jsonify({
                "error": "Script execution failed",
                "details": result.stderr
            }), 500

        # Parse and return the output
        try:
            # Clean and inspect stdout before parsing
            cleaned_stdout = result.stdout.strip()
            logger.warning(f"🧪 Cleaned stdout preview: {repr(cleaned_stdout[:300])}")
            
            try:
                output_json = json.loads(cleaned_stdout)
                logger.info(f"Successfully processed video: {output_json.get('video_id', 'unknown')}")
                return jsonify(output_json)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode failed: {e}")
                logger.error(f"💥 Full raw stdout:\n{result.stdout}")
                return jsonify({
                    "error": "Invalid JSON from script",
                    "details": str(e)
                }), 500

        except Exception as e:
            logger.error(f"Failed to parse script output: {e}")
            logger.error(f"Script stdout: {result.stdout}")
            return jsonify({
                "error": "Invalid output from processing script",
                "details": str(e)
            }), 500

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e}")
        return jsonify({
            "error": "Failed to execute processing script",
            "details": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    # Get port from environment variable for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
    