import os
import subprocess
import whisper

from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from services.rag_engine import get_store, get_embed_model

model = whisper.load_model("base")

def extract_audio(video_path: str):
    wav_path = video_path.rsplit(".", 1)[0] + ".wav"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ])

    return wav_path

def process_video(video_path: str, video_url: str, filename: str):
    wav = extract_audio(video_path)

    result = model.transcribe(wav)

    docs = []

    for seg in result["segments"]:
        docs.append(
            Document(
                text=seg["text"],
                metadata={
                    "video": filename,
                    "video_url": video_url,
                    "start": seg["start"],
                    "end": seg["end"]
                }
            )
        )
    store = get_store()
    embed_model = get_embed_model()
    VectorStoreIndex.from_documents(
        docs,
        vector_store=store,
        embed_model=embed_model
    )

    os.remove(wav)