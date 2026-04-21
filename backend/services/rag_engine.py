from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import settings

client = None
store = None
index = None
retriever = None
embed_model = None


def init_qdrant():
    global client, store, index, retriever, embed_model

    if retriever is not None:
        return

    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30
        )

        store = QdrantVectorStore(
            client=client,
            collection_name="video_text",
            dense_vector_name=None
        )

        embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        index = VectorStoreIndex.from_vector_store(
            store,
            embed_model=embed_model
        )

        retriever = index.as_retriever(similarity_top_k=5)

        print("✅ Qdrant Ready")

    except Exception as e:
        print("❌ Qdrant failed:", e)


def get_store():
    init_qdrant()
    return store


def get_embed_model():
    init_qdrant()
    return embed_model


def search(query: str):
    init_qdrant()

    if retriever is None:
        return []

    try:
        return retriever.retrieve(query)
    except Exception as e:
        print("❌ Search error:", e)
        return []