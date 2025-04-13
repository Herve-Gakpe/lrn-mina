import json
import os

# Paramètres
ocr_path = "ocr_output.json"
whisper_path = "transcriptions/mina1_salutations_cleaned.json"
output_path = "vocab_mina.json"
frame_rate = 0.25  # 1 image toutes les 4 secondes

# Chargement des données
with open(ocr_path, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

with open(whisper_path, "r", encoding="utf-8") as f:
    whisper_data = json.load(f)

segments = whisper_data.get("segments", [])

# Création de la sortie enrichie
output = []

for segment in segments:
    start_time = segment["start"]
    end_time = segment["end"]
    text = segment["text"].strip()

    # On choisit une frame correspondant au milieu du segment
    mid_time = (start_time + end_time) / 2
    frame_index = int(mid_time / 4)  # une frame toutes les 4 secondes
    frame_filename = f"frame_{frame_index:04d}.jpg"
    text_ocr = ocr_data.get(frame_filename, "")

    output.append({
        "start": start_time,
        "end": end_time,
        "text_whisper": text,
        "text_ocr": text_ocr,
        "text_mina": "",       # à remplir manuellement
        "note": ""             # à remplir manuellement
    })

# Sauvegarde
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Fusion OCR + Whisper terminée. Fichier généré :", output_path)

#Fonction merge_data from GPT
def merge_data(whisper_path, ocr_path, frame_rate=0.25):
    # Chargement des données OCR
    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    # Chargement des données Whisper
    with open(whisper_path, "r", encoding="utf-8") as f:
        whisper_data = json.load(f)

    segments = whisper_data.get("segments", [])
    output = []

    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()

        # Frame correspondant au milieu du segment
        mid_time = (start_time + end_time) / 2
        frame_index = int(mid_time / (1 / frame_rate))  # spacing inverse du framerate
        frame_filename = f"frame_{frame_index:04d}.jpg"

        text_ocr = ocr_data.get(frame_filename, "")

        output.append({
            "start": start_time,
            "end": end_time,
            "text_whisper": text,
            "text_ocr": text_ocr,
            "text_mina": "",
            "note": ""
        })

    return output