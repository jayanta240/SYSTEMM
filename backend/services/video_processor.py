import os
import subprocess
from faster_whisper import WhisperModel
from services.rag_engine import get_client, get_embed_model, COLLECTION_NAME
from uuid import uuid4
from qdrant_client.models import PointStruct

# load model once
model = WhisperModel("base", device="cpu", compute_type="int8")


def extract_audio(video_path: str):
    wav_path = video_path.rsplit(".", 1)[0] + ".wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            wav_path
        ],
        check=True
    )

    return wav_path


def process_video(video_path: str, video_url: str, filename: str):
    print(f"\n🎬 Processing: {filename}")

    wav = extract_audio(video_path)
    print("🎧 Audio extracted")

    segments, _ = model.transcribe(wav)
    segments = list(segments)

    print(f"🧠 Segments detected: {len(segments)}")

    if len(segments) == 0:
        print("❌ No speech detected")
        return

    client = get_client()
    embed_model = get_embed_model()

    points = []

    WINDOW_SIZE = 3

    for i in range(len(segments)):

        chunk_segments = segments[i:i + WINDOW_SIZE]

        if not chunk_segments:
            continue

        combined_text = " ".join(
            s.text.strip()
            for s in chunk_segments
            if s.text.strip()
        )

        if not combined_text:
            continue

        start_time = float(chunk_segments[0].start)
        end_time = float(chunk_segments[-1].end)

        embedding = embed_model.get_text_embedding(
            combined_text
        )
        points.append(
          PointStruct(
              id=str(uuid4()),
              vector=embedding,
              payload={
                  "type": "video",
                  "video": filename,
                  "video_url": video_url,
                  "start": start_time,
                  "end": end_time,
                  "text": combined_text
              }
          )
        )

    print(f"📦 Uploading {len(points)} points to Qdrant...")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("✅ STORED in Qdrant")

    if os.path.exists(wav):
        os.remove(wav)