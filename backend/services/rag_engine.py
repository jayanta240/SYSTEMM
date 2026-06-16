from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import settings

COLLECTION_NAME = "learning_content"
ISSUE_COLLECTION = "issue_images"
client = None
embed_model = None


def init_qdrant():
    global client, embed_model

    if client is not None:
        return

    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=30
    )

    # create collection if not exists
    collections = [c.name for c in client.get_collections().collections]
    if ISSUE_COLLECTION not in collections:

     print("⚡ Creating issue image collection...")

     client.create_collection(
         collection_name=ISSUE_COLLECTION,
         vectors_config=VectorParams(
             size=512,
             distance=Distance.COSINE
 )
     )

     print("✅ Issue image collection created")

    if COLLECTION_NAME not in collections:
        print("⚡ Creating Qdrant collection...")

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE,
            ),
        )

        print("✅ Collection created")
        client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="video",
                field_schema="keyword"
        )

        client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="source",
                field_schema="keyword"
        )

        print("✅ Payload indexes created")    

    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-en-v1.5"
    )

    print("✅ Qdrant Ready")


def get_client():
    init_qdrant()
    return client


def get_embed_model():
    init_qdrant()
    return embed_model


# 🔥 DIRECT SEARCH (NO LlamaIndex)
def search(query: str):
    init_qdrant()

    query_vector = embed_model.get_text_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=5
    )
    
    formatted = []

    for r in results.points:
        payload = r.payload or {}

        formatted.append({
            "text": payload.get("text", ""),
            "metadata": payload,
            "score": r.score
        })

    print("\n🔍 DEBUG RESULTS ------------------")
    for r in formatted:
        print("TEXT:", r["text"][:50])
        print("META:", r["metadata"])
        print("SCORE:", r["score"])
        print("----------------------------------")

    return formatted