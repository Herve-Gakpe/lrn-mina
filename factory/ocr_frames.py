import os
import json
from PIL import Image
import pytesseract

# Dossier où se trouvent les images
frames_dir = "frames/salutations1"
output_file = "ocr_output.json"
ocr_results = {}

# OCR sur toutes les images du dossier
for filename in sorted(os.listdir(frames_dir)):
    if filename.endswith(".jpg"):
        filepath = os.path.join(frames_dir, filename)
        try:
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img, lang="fra")  # Utilise le français
            ocr_results[filename] = text.strip()
        except Exception as e:
            print(f"❌ Erreur pour l'image {filename} : {e}")
            ocr_results[filename] = ""

# Écriture dans un fichier JSON bien formé
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(ocr_results, f, indent=2, ensure_ascii=False)

print(f"\n✅ OCR terminé : résultats écrits dans {output_file}")