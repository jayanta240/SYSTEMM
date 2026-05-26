import os
from uuid import uuid4
from pypdf import PdfReader

from services.rag_engine import get_client, get_embed_model, COLLECTION_NAME


def process_document(file_path: str, filename: str):
    print(f"\n📄 Processing document: {filename}")

    reader = PdfReader(file_path)

    client = get_client()
    embed_model = get_embed_model()

    points = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()

        if not text:
            continue

        # simple chunking
        chunks = text.split("\n")

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            embedding = embed_model.get_text_embedding(chunk)

            points.append({
                "id": str(uuid4()),
                "vector": embedding,
                "payload": {
                    "type": "document",
                    "source": filename,
                    "page": page_num + 1,
                    "text": chunk
                }
            })

    print(f"📦 Uploading {len(points)} document chunks...")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("✅ Document stored in Qdrant")