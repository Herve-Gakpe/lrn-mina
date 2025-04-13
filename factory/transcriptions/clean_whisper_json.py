import json

# === 1. CHARGE LE FICHIER WHISPER JSON ===
with open("mina1_salutations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === 2. CRITÈRES DE NETTOYAGE ===
def is_valid_segment(segment):
    text = segment["text"].strip().lower()
    if not text or text in ["...", "…", ".", ".."]:
        return False
    if len(text) < 10:  # On écarte les phrases trop courtes
        return False
    if all(char in ".?!," for char in text):  # Juste ponctuation
        return False
    return True

# === 3. FILTRE LES SEGMENTS ===
clean_segments = [seg for seg in data["segments"] if is_valid_segment(seg)]

# === 4. SAUVEGARDE LE NOUVEAU JSON ===
output = {
    "language": data.get("language", "unknown"),
    "segments": clean_segments
}

with open("mina1_salutations_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Fichier nettoyé généré avec {len(clean_segments)} segments utiles.")
