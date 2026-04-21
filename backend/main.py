from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil

from models.schemas import ChatRequest, ChatResponse, SourceItem
from services.translation_service import detect_lang, to_english, translate_back
from services.rag_engine import search
from services.llm_service import ask_llm
from services.storage_service import upload_video
from services.video_processor import process_video

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STORAGE ----------------
os.makedirs("temp", exist_ok=True)

# Duplicate detection (temporary memory)
processed_files = set()

# In-memory chat sessions
sessions = {
    "chat-1": []
}


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Backend Running"}


# ---------------- CHAT ----------------
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Detect language
    lang = detect_lang(req.message)

    # Translate user query to English for retrieval
    query = req.message
    if lang != "en":
        query = to_english(req.message)

    # Greeting handling
    greetings = ["hi", "hello", "hey", "hii"]

    if query.lower().strip() in greetings:
        answer = "Hello 👋 How can I help you with your videos?"

        if lang != "en":
            answer = translate_back(answer, lang)

        sessions.setdefault(req.session_id, [])
        sessions[req.session_id].append(
            {"role": "user", "content": req.message}
        )
        sessions[req.session_id].append(
            {"role": "assistant", "content": answer}
        )

        return ChatResponse(answer=answer, sources=[])

    # Search in vector DB
    nodes = search(query)

    if not nodes:
        answer = "I couldn't find relevant information in uploaded videos."

        if lang != "en":
            answer = translate_back(answer, lang)

        sessions.setdefault(req.session_id, [])
        sessions[req.session_id].append(
            {"role": "user", "content": req.message}
        )
        sessions[req.session_id].append(
            {"role": "assistant", "content": answer}
        )

        return ChatResponse(answer=answer, sources=[])

    # Top matches
    top = sorted(nodes, key=lambda x: x.score, reverse=True)[:3]

    # Build transcript context
    context = "\n".join([n.node.text for n in top])

    # Always generate in English first
    prompt = f"""
Answer ONLY from the transcript context below.

Context:
{context}

Question:
{query}

Rules:
- Use only the context
- Keep answer clear and concise
- If not found, say not found in uploaded videos
"""

    # Generate answer
    answer = ask_llm(prompt)

    # Final translate back to original language
    if lang != "en":
        answer = translate_back(answer, lang)

    # Save messages to session
    sessions.setdefault(req.session_id, [])
    sessions[req.session_id].append(
        {"role": "user", "content": req.message}
    )
    sessions[req.session_id].append(
        {"role": "assistant", "content": answer}
    )

    # Build sources
    sources = []
    for n in top:
        m = n.node.metadata
        sources.append(
            SourceItem(
                video=m.get("video"),
                start=m.get("start"),
                end=m.get("end"),
                video_url=m.get("video_url")
            )
        )

    return ChatResponse(answer=answer, sources=sources)


# ---------------- UPLOAD ----------------
@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    uploaded = []
    skipped = []

    for file in files:
        if file.filename in processed_files:
            skipped.append(file.filename)
            continue

        temp_path = os.path.join("temp", file.filename)

        # Save locally
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to Cloudinary
        cloud = upload_video(temp_path)

        # Process video
        process_video(
            temp_path,
            cloud["url"],
            file.filename
        )

        processed_files.add(file.filename)

        # Delete temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        uploaded.append(file.filename)

    return {
        "uploaded": uploaded,
        "skipped": skipped
    }


# ---------------- SESSIONS ----------------
@app.get("/api/sessions")
def get_sessions():
    return [{"id": k, "name": k} for k in sessions.keys()]


@app.post("/api/sessions")
def create_session():
    sid = f"chat-{len(sessions) + 1}"
    sessions[sid] = []
    return {"id": sid, "name": sid}


@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: str):
    return sessions.get(session_id, [])