from services.image_embedding_service import (
    get_image_embedding
)

from services.rag_engine import (
    get_client,
    ISSUE_COLLECTION
)


def search_issue_image(image_path):

    client = get_client()

    embedding = get_image_embedding(
        image_path
    )

    results = client.query_points(
        collection_name=ISSUE_COLLECTION,
        query=embedding,
        limit=1
    )

    if not results.points:
        return None

    best = results.points[0]

    print(f"🔥 Similarity: {best.score}")

    if best.score < 0.75:
        return None

    payload = best.payload or {}

    return {
        "score": best.score,
        "problem": payload.get("problem"),
        "solution": payload.get("solution"),
        "image_url": payload.get("image_url")
    }