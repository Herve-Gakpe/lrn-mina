import json
import os

# Default parameters
DEFAULT_WHISPER_PATH = "transcriptions/mina1_salutations_cleaned.json"
DEFAULT_OCR_PATH = "ocr_output.json"
DEFAULT_OUTPUT_PATH = "vocab_mina.json"
DEFAULT_FRAME_RATE = 0.25  # 1 image every 4 seconds

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
        output_path: Path where to save the merged output (default: vocab_mina.json)
        frame_rate: Frame rate used to calculate frame index (default: 0.25)
    """
    # Load OCR data
    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    # Load Whisper data
    with open(whisper_path, "r", encoding="utf-8") as f:
        whisper_data = json.load(f)

    segments = whisper_data.get("segments", [])

    # Create enriched output
    output = []
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()

        # Choose a frame corresponding to the middle of the segment
        mid_time = (start_time + end_time) / 2
        frame_index = int(mid_time / 4)  # one frame every 4 seconds
        frame_filename = f"frame_{frame_index:04d}.jpg"
        text_ocr = ocr_data.get(frame_filename, "")

        output.append({
            "start": start_time,
            "end": end_time,
            "text_whisper": text,
            "text_ocr": text_ocr,
            "text_mina": "",  # to be filled manually
            "note": ""       # to be filled manually
        })

    # Save output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("✅ Fusion OCR + Whisper terminée. Fichier généré :", output_path)

if __name__ == "__main__":
    merge_data(
        whisper_path=DEFAULT_WHISPER_PATH,
        ocr_path=DEFAULT_OCR_PATH,
        output_path=DEFAULT_OUTPUT_PATH,
        frame_rate=DEFAULT_FRAME_RATE
    )