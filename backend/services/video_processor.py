import os
import subprocess
from faster_whisper import WhisperModel
from llama_index.core import Document, VectorStoreIndex
from services.rag_engine import get_store, get_embed_model

# Load model once
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


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
    wav = extract_audio(video_path)

    # faster-whisper output
    segments, info = model.transcribe(wav)

    docs = []

    for seg in segments:
        text = seg.text.strip()

        if not text:
            continue

        docs.append(
            Document(
                text=text,
                metadata={
                    "video": filename,
                    "video_url": video_url,
                    "start": float(seg.start),
                    "end": float(seg.end),
                }
            )
        )

    if docs:
        store = get_store()
        embed_model = get_embed_model()

        VectorStoreIndex.from_documents(
            docs,
            vector_store=store,
            embed_model=embed_model
        )

    if os.path.exists(wav):
        os.remove(wav)