import os
from faster_whisper import WhisperModel

# FFmpeg
ffmpeg_path = r"C:\Users\iluva\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Carpetas
folder_path = r"C:\Users\iluva\OneDrive\Documentos\AGENTE_VENTAS_IA\Insumos_crudos"
output_dir = "Transcripciones"
os.makedirs(output_dir, exist_ok=True)

# Cargar modelo (float16 para RTX 50xx con faster-whisper)
print("Cargando modelo Whisper...")
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

extensiones_validas = (".mp4", ".mkv", ".mov", ".mp3")

for filename in os.listdir(folder_path):
    if filename.lower().endswith(extensiones_validas):
        video_path = os.path.join(folder_path, filename)
        base_name = filename.rsplit('.', 1)[0]
        output_txt = os.path.join(output_dir, base_name + ".txt")

        if os.path.exists(output_txt):
            print(f"⏭ Saltando {filename}, ya existe la transcripción.")
            continue

        print(f"🎙 Transcribiendo: {filename}...")
        try:
            segments, info = model.transcribe(video_path, beam_size=5)
            with open(output_txt, "w", encoding="utf-8") as f:
                for segment in segments:
                    f.write(segment.text + "\n")
            print(f"✅ Transcripción guardada en: {output_txt}")
        except Exception as e:
            print(f"❌ Error al transcribir {filename}: {e}")

print("🟢 Proceso terminado.")