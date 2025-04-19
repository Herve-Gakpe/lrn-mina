import json
import os
import sys
from typing import Dict, List, Any

# Base directory for all file operations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default parameters
DEFAULT_WHISPER_PATH = os.path.join(BASE_DIR, "transcriptions", "mina1_salutations_cleaned.json")
DEFAULT_OCR_PATH = os.path.join(BASE_DIR, "ocr_output.json")
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, "vocab_mina.json")
DEFAULT_FRAME_RATE = 0.25  # 1 image every 4 seconds

class FusionError(Exception):
    """Custom exception for fusion-related errors"""
    pass

def validate_file_path(file_path: str, file_type: str) -> None:
    """
    Validate that a file exists and is readable.
    
    Args:
        file_path: Path to the file to validate
        file_type: Type of file for error message
    
    Raises:
        FusionError: If the file is not found or not readable
    """
    if not os.path.exists(file_path):
        raise FusionError(f"{file_type} file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise FusionError(f"Cannot read {file_type} file: {file_path}")

def load_json_file(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Load and validate a JSON file.
    
    Args:
        file_path: Path to the JSON file
        file_type: Type of file for error message
    
    Returns:
        The loaded JSON data
    
    Raises:
        FusionError: If the file cannot be read or contains invalid JSON
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise FusionError(f"Invalid JSON in {file_type} file: {e}")
    except Exception as e:
        raise FusionError(f"Error reading {file_type} file: {e}")

def merge_data(
    whisper_path: str,
    ocr_path: str,
    output_path: str = DEFAULT_OUTPUT_PATH,
    frame_rate: float = DEFAULT_FRAME_RATE
) -> None:
    """
    Merge Whisper transcription data with OCR output into a vocabulary JSON file.
    
    Args:
        whisper_path: Path to the Whisper JSON file
        ocr_path: Path to the OCR output JSON file
        output_path: Path where to save the merged output
        frame_rate: Frame rate used to calculate frame index (default: 0.25)
    
    Raises:
        FusionError: If there are any issues with the fusion process
    """
    try:
        # Validate input files
        validate_file_path(whisper_path, "Whisper")
        validate_file_path(ocr_path, "OCR")
        
        # Load and validate data
        ocr_data = load_json_file(ocr_path, "OCR")
        whisper_data = load_json_file(whisper_path, "Whisper")
        
        if not isinstance(ocr_data, dict):
            raise FusionError("OCR data must be a dictionary")
        
        segments = whisper_data.get("segments", [])
        if not segments:
            raise FusionError("No segments found in Whisper data")

        # Create enriched output
        output: List[Dict[str, Any]] = []
        for segment in segments:
            try:
                start_time = float(segment["start"])
                end_time = float(segment["end"])
                text = str(segment["text"]).strip()

                # Choose a frame corresponding to the middle of the segment
                mid_time = (start_time + end_time) / 2
                frame_index = int(mid_time / frame_rate)
                frame_filename = f"frame_{frame_index:04d}.jpg"
                text_ocr = str(ocr_data.get(frame_filename, "")).strip()

                output.append({
                    "start": start_time,
                    "end": end_time,
                    "text_whisper": text,
                    "text_ocr": text_ocr,
                    "text_mina": "",  # to be filled manually
                    "note": "",       # to be filled manually
                    "frame": frame_filename
                })
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid segment: {e}", file=sys.stderr)
                continue

        if not output:
            raise FusionError("No valid segments were processed")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save output
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise FusionError(f"Error saving output file: {e}")
        
    except FusionError as e:
        raise
    except Exception as e:
        raise FusionError(f"Unexpected error during fusion: {e}")

if __name__ == "__main__":
    try:
        merge_data(
            whisper_path=DEFAULT_WHISPER_PATH,
            ocr_path=DEFAULT_OCR_PATH,
            output_path=DEFAULT_OUTPUT_PATH,
            frame_rate=DEFAULT_FRAME_RATE
        )
    except FusionError as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        exit(1)