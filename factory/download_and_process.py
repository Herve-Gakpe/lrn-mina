import os
import json
import subprocess
from typing import Dict, Any
from urllib.parse import parse_qs, urlparse
import pytesseract
from PIL import Image
from factory.fusion_ocr_whisper import merge_data

# Base directory for all file operations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
    raise ValueError(f"Invalid YouTube URL: {url}")

def download_video(url: str) -> str:
    """
    Download YouTube video using yt-dlp.
    Returns the path to the downloaded file.
    """
    video_id = get_video_id(url)
    downloads_dir = os.path.join(BASE_DIR, "downloads", video_id)
    output_template = os.path.join(downloads_dir, "%(title)s.%(ext)s")
    
    # Create downloads directory if it doesn't exist
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Download video using yt-dlp
    cmd = [
        "yt-dlp",
        "-f", "best",  # Best quality
        "-o", output_template,
        url
    ]
    subprocess.run(cmd, check=True)
    
    # Get the downloaded file path (should be only one file)
    files = os.listdir(downloads_dir)
    if not files:
        raise FileNotFoundError("Video download failed")
    
    return os.path.join(downloads_dir, files[0])

def transcribe_video(video_path: str) -> str:
    """
    Transcribe video using Whisper CLI.
    Returns path to the JSON output.
    """
    output_dir = os.path.dirname(video_path)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.json")
    
    cmd = [
        "whisper",
        video_path,
        "--language", "fr",
        "--model", "medium",
        "--output_format", "json",
        "--output_dir", output_dir
    ]
    subprocess.run(cmd, check=True)
    
    return output_path

def extract_frames(video_path: str) -> str:
    """
    Extract frames from video every 4 seconds using ffmpeg.
    Returns path to frames directory.
    """
    frames_dir = os.path.join(os.path.dirname(video_path), "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "fps=1/4",
        "-frame_pts", "1",
        os.path.join(frames_dir, "frame_%04d.jpg")
    ]
    subprocess.run(cmd, check=True)
    
    return frames_dir

def process_frames_ocr(frames_dir: str) -> Dict[str, str]:
    """
    Perform OCR on all frames in directory.
    Returns dict mapping frame filenames to OCR text.
    """
    ocr_results = {}
    
    for frame in sorted(os.listdir(frames_dir)):
        if not frame.endswith(('.jpg', '.png')):
            continue
            
        frame_path = os.path.join(frames_dir, frame)
        try:
            image = Image.open(frame_path)
            text = pytesseract.image_to_string(image, lang='fra')
            ocr_results[frame] = text.strip()
        except Exception as e:
            print(f"Error processing frame {frame}: {e}")
            ocr_results[frame] = ""
    
    return ocr_results

def save_ocr_results(ocr_results: Dict[str, str], output_dir: str) -> str:
    """Save OCR results to JSON file."""
    output_path = os.path.join(output_dir, "ocr_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_results, f, indent=2, ensure_ascii=False)
    return output_path

def full_pipeline(video_url: str) -> Dict[str, Any]:
    """
    Process a YouTube video through the complete pipeline:
    1. Download video
    2. Transcribe audio
    3. Extract frames
    4. OCR frames
    5. Merge Whisper + OCR data
    
    Returns a summary of the processing.
    """
    try:
        # Download video
        video_path = download_video(video_url)
        video_dir = os.path.dirname(video_path)
        
        # Transcribe video
        whisper_json = transcribe_video(video_path)
        
        # Extract and process frames
        frames_dir = extract_frames(video_path)
        ocr_results = process_frames_ocr(frames_dir)
        ocr_json = save_ocr_results(ocr_results, video_dir)
        
        # Merge Whisper and OCR data
        output_path = os.path.join(video_dir, "vocab_mina.json")
        merge_data(
            whisper_path=whisper_json,
            ocr_path=ocr_json,
            output_path=output_path
        )
        
        # Generate summary
        with open(output_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
            
        summary = {
            "status": "success",
            "video_id": get_video_id(video_url),
            "processed_frames": len(ocr_results),
            "vocabulary_entries": len(vocab_data),
            "output_path": output_path
        }
        
        return summary
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python download_and_process.py <youtube_url>")
        sys.exit(1)
        
    video_url = sys.argv[1]
    result = full_pipeline(video_url)
    print(json.dumps(result, indent=2))
