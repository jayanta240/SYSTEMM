from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector
)
from services.image_service import upload_issue_image
import shutil
import cloudinary.uploader
import re
from services.video_generator import generate_video
from models.schemas import ChatRequest, ChatResponse, SourceItem
from services.translation_service import detect_lang, to_english, translate_back
from services.storage_service import upload_video
from services.rag_engine import (
    init_qdrant,
    search,
    get_client,
    COLLECTION_NAME
)
from services.issue_search_service import (
    search_issue_image
)
from uuid import uuid4
from qdrant_client.models import PointStruct
from services.image_embedding_service import (
    get_image_embedding
)

from services.rag_engine import (
    get_client,
    ISSUE_COLLECTION
)
from fastapi import Form
from fastapi.staticfiles import StaticFiles
from services.file_db import (
    init_db,
    add_file,
    get_all_files,
    delete_file,
    add_issue,
    get_all_issues
)
app = FastAPI()
init_db()
app.mount("/temp_videos", StaticFiles(directory="temp_videos"), name="temp_videos")
# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://monorepo-ebon-eight.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# INIT QDRANT
# -----------------------------
@app.on_event("startup")
def startup():
    print("🚀 Initializing Qdrant...")
    init_qdrant()


# -----------------------------
# GLOBALS
# -----------------------------
os.makedirs("temp", exist_ok=True)
sessions = {"chat-1": []}


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():
    return {"status": "Backend Running"}


# -----------------------------
# HELPER: CHAPTER DETECTION
# -----------------------------
def extract_chapter_number(query: str):
    match = re.search(r"chapter\s*(\d+)", query.lower())
    return int(match.group(1)) if match else None


def classify_intent(message: str):

    msg = message.lower().strip()

    # -----------------------------
    # GREETING RULES
    # -----------------------------
    greetings = [
        "hi", "hello", "hey",
        "hii", "helloo",
        "good morning",
        "good evening",

        # Bengali
        "হ্যালো", "হাই",
        "কেমন আছো",

        # Hindi
        "नमस्ते", "हेलो",
        "क्या हाल"
    ]

    # exact short greeting only
    if msg in greetings:
        return "greeting"

    # very short greeting-like messages
    if len(msg.split()) <= 2 and any(g in msg for g in greetings):
        return "greeting"

    # -----------------------------
    # VIDEO GENERATION
    # -----------------------------
    video_keywords = [
        "generate video",
        "make video",
        "create video",
        "video banao",
        "ভিডিও বানাও",
        "ভিডিও তৈরি"
    ]

    if any(v in msg for v in video_keywords):
        return "video_generation"

    # -----------------------------
    # SUMMARIZATION
    # -----------------------------
    summary_keywords = [
        "summarize",
        "summary",
        "summarise",
        "সংক্ষেপ",
        "সারাংশ",
        "सारांश"
    ]

    if any(s in msg for s in summary_keywords):
        return "summarization"

    # -----------------------------
    # DEFAULT
    # -----------------------------
    return "learning_question"                                    
# -----------------------------
# CHAT
# -----------------------------
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    from services.llm_service import ask_llm

    # -----------------------------
    # LANGUAGE DETECTION
    # -----------------------------
    lang = detect_lang(req.message)
    print("🌐 DETECTED LANGUAGE:", lang)
    if lang == "en":
       english_query = req.message
    else:
      english_query = to_english(req.message)


    language_instruction = {
        "en": "IMPORTANT: Respond ONLY in English. Never use Bengali or Hindi.",
        "bn": "IMPORTANT: শুধুমাত্র বাংলায় উত্তর দাও। ইংরেজি ব্যবহার করবে না।",
        "hi": "IMPORTANT: केवल हिंदी में उत्तर दें। अंग्रेज़ी का उपयोग न करें।"
    }.get(lang, "IMPORTANT: Respond ONLY in English.")
    # ---------------- INTENT DETECTION ----------------
    intent = classify_intent(english_query)

    print("🧠 Intent:", intent)

# ---------------- GREETING ----------------
    if intent == "greeting":

       greeting_map = {
           "en": "Hello 👋 How can I help you with your learning today?",
           "bn": "হ্যালো 👋 আজ আপনার পড়াশোনায় কীভাবে সাহায্য করতে পারি?",
           "hi": "नमस्ते 👋 आज मैं आपकी पढ़ाई में कैसे मदद कर सकता हूँ?"
       }

       return ChatResponse(
           answer=greeting_map.get(
               lang,
               "Hello 👋 How can I help you today?"
           ),
           sources=[]
       )

# ---------------- SUMMARIZATION ----------------
    if intent == "summarization":
        print("📚 Summarization request detected")

# ---------------- VIDEO GENERATION ----------------
    if intent == "video_generation":
        print("🎬 Video request detected")

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    results = search(english_query)

    if not results:
        return ChatResponse(
            answer="No relevant content found in uploaded materials.",
            sources=[]
        )

    # -----------------------------
    # CHAPTER HANDLING
    # -----------------------------
    chapter_num = extract_chapter_number(english_query)

    if chapter_num:
        results = [
            r for r in results
            if r["metadata"].get("type") == "document"
        ]

        results = [
            r for r in results
            if r["metadata"].get("page") in [chapter_num, chapter_num + 1]
        ]

        top = results[:40] if results else []

    else:
        # 🔥 FIX: remove strict filtering
        ranked = sorted(
           results,
           key=lambda x: x["score"],
           reverse=True
        )
        top = ranked[:3]
    
    best_score = top[0]["score"] if top else 0

    print("🔥 Best Similarity:", best_score)

    MIN_SCORE = 0.60

    relevant_content_found = best_score >= MIN_SCORE    

   

    # -----------------------------
    # CONTEXT (IMPORTANT FIX)
    # -----------------------------
    context_parts = []
    seen_texts = set()

    for r in top:

         text = r.get("text", "")
 
         if text and text not in seen_texts:
            context_parts.append(text)
            seen_texts.add(text)
         current_start = r["metadata"].get("start", 0)

         for neighbor in results:

             neighbor_start = neighbor["metadata"].get("start", 0)

        # nearby transcript chunk
             if abs(neighbor_start - current_start) <= 6:

                neighbor_text = neighbor.get("text", "")

                if neighbor_text and neighbor_text not in seen_texts:

                   context_parts.append(neighbor_text)
                   seen_texts.add(neighbor_text)   

            

    context = "\n\n".join(context_parts)

    print("📚 FINAL CONTEXT:")
    print(context[:2000])

            

    # -----------------------------
    # MODE
    # -----------------------------
    mode = getattr(req, "mode", "normal")

    if mode == "summary":
        instruction = "Summarize ONLY the retrieved context."
    elif mode == "points":
        instruction = "Answer ONLY in concise bullet points from the retrieved context."
    else:
        instruction = "Answer ONLY from the retrieved context. Do not add extra explanations."
    # -----------------------------
    # CONVERSATION MEMORY
    # -----------------------------
    chat_history = sessions.get(req.session_id, [])

    history_text = ""

    for msg in chat_history[-6:]:

        role = msg["role"]

        if role == "user":
            history_text += f"User: {msg['content']}\n"

        else:
            history_text += f"Assistant: {msg['content']}\n"    

    # -----------------------------
    # PROMPT (FIXED)
    # -----------------------------
    if relevant_content_found:
        prompt = f"""
You are an intelligent AI learning assistant.

{language_instruction}

IMPORTANT RULES:
- NEVER switch to another language
- ALWAYS answer in the SAME language as the user
- Answer STRICTLY from the provided context
- Do NOT add outside knowledge if answer exists in context
- Do NOT invent examples
- Do NOT elaborate unnecessarily
- Keep the answer concise and focused
- Ignore unrelated context
- If multiple reasons exist, list ONLY those reasons
- Never hallucinate extra technical explanations

CONVERSATION HISTORY:
{history_text}
CONTEXT:
{context}

QUESTION:
{english_query}

INSTRUCTION:
{instruction}

GUIDELINES:
- Use ONLY uploaded content
- Keep answer precise
- Avoid unnecessary explanation
- Do not add information not present in context
"""

    else:

      prompt = f"""
You are an intelligent AI learning assistant.

{language_instruction}

IMPORTANT:
The uploaded learning materials do NOT contain enough information about this topic.

FIRST clearly mention:
"⚠️ This topic was not found in the uploaded learning materials."

THEN provide:
"A quick general explanation:"

AFTER THAT:
- Explain using your own general knowledge
- Keep explanation educational and simple
- Explain like a teacher
- Keep answer concise but useful
- NEVER switch language unnecessarily
CONVERSATION HISTORY:
{history_text}
QUESTION:
{english_query}
"""

    # 🔥 FIX: single LLM call only
    answer = ask_llm(prompt)

    # -----------------------------
    # SOURCES
    # -----------------------------
    sources = []
    if relevant_content_found:

        for r in top[:5]:
            m = r["metadata"]

            sources.append(
                SourceItem(
                    type=m.get("type"),
                    video=m.get("video"),
                    video_url=m.get("video_url"),
                    start=m.get("start"),
                    end=m.get("end"),
                    source=m.get("source"),
                    page=m.get("page"),
                )
            )

    # -----------------------------
    # SAVE SESSION
    # -----------------------------
    sessions.setdefault(req.session_id, [])
    sessions[req.session_id].append({"role": "user", "content": req.message})
    sessions[req.session_id].append({"role": "assistant", "content": answer})

    return ChatResponse(answer=answer, sources=sources)

# -----------------------------
# UPLOAD
# -----------------------------
@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    from services.video_processor import process_video
    from services.document_processor import process_document

    init_qdrant()  # 🔥 important

    uploaded = []
    failed = []

    for file in files:
        try:
            temp_path = os.path.join("temp", file.filename)

            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # -----------------------------
            # VIDEO
            # -----------------------------
            if file.filename.endswith((".mp4", ".mov", ".avi")):

               cloud = upload_video(temp_path)

               process_video(
                   temp_path,
                   cloud["url"],
                   file.filename
               )

    # -----------------------------
    # SAVE FILE METADATA
    # -----------------------------
               size_mb = round(
                   os.path.getsize(temp_path) / (1024 * 1024),
                   2
               )

               add_file(
                   filename=file.filename,
                   filetype="video",
                   cloudinary_url=cloud["url"],
                   size_mb=size_mb
               )
            # -----------------------------
            # DOCUMENT
            # -----------------------------
            elif file.filename.endswith((".pdf", ".docx")):
                process_document(temp_path, file.filename)

            else:
                raise Exception("Unsupported file type")

            uploaded.append(file.filename)

            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            failed.append({
                "file": file.filename,
                "error": str(e)
            })

    return {
        "uploaded": uploaded,
        "failed": failed
    }

# -----------------------------
# FILE MANAGEMENT
# -----------------------------
@app.get("/api/files")
def list_files():

    files = get_all_files()

    formatted = []

    for f in files:

        formatted.append({
            "id": f[0],
            "filename": f[1],
            "filetype": f[2],
            "cloudinary_url": f[3],
            "size_mb": f[4],
            "uploaded_at": f[5]
        })

    return formatted

# -----------------------------
# DELETE FILE
# -----------------------------
@app.delete("/api/files/{file_id}")
def delete_uploaded_file(file_id: int):

    files = get_all_files()

    target = None

    for f in files:

        if f[0] == file_id:
            target = f
            break

    if not target:
        return {
            "success": False,
            "message": "File not found"
        }

    filename = target[1]
    cloudinary_url = target[3]

    try:

        # --------------------------------
        # DELETE FROM QDRANT
        # --------------------------------
        client = get_client()

        client.delete(
            collection_name=COLLECTION_NAME,
            wait=True,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="video",
                            match=MatchValue(value=filename)
                        )
                    ]
                )
            )
        )

        print("✅ Deleted Qdrant vectors")

    except Exception as e:
        print("❌ Qdrant delete error:", e)

    try:

        # --------------------------------
        # DELETE FROM CLOUDINARY
        # --------------------------------
        public_id = (
            cloudinary_url
            .split("/")[-1]
            .split(".")[0]
        )

        cloudinary.uploader.destroy(
            public_id,
            resource_type="video"
        )

        print("✅ Deleted Cloudinary video")

    except Exception as e:
        print("❌ Cloudinary delete error:", e)

    try:

        # --------------------------------
        # DELETE SQLITE ENTRY
        # --------------------------------
        delete_file(file_id)

        print("✅ Deleted SQLite entry")

    except Exception as e:
        print("❌ SQLite delete error:", e)

    return {
        "success": True,
        "message": "File deleted successfully"
    }

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...)
):

    temp_path = f"temp/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cloud = upload_issue_image(temp_path)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "success": True,
        "image_url": cloud["url"],
        "public_id": cloud["public_id"]
    }
@app.post("/api/upload-issue")
async def upload_issue(
    file: UploadFile = File(...),
    problem: str = Form(...),
    solution: str = Form(...)
):

    temp_path = f"temp/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    cloud = upload_issue_image(temp_path)
    embedding = get_image_embedding(
         temp_path
    )

    client = get_client()

    client.upsert(
        collection_name=ISSUE_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "problem": problem,
                    "solution": solution,
                    "image_url": cloud["url"]
                }
            )
        ]
    )

    print("✅ Issue image stored in Qdrant")

    add_issue(
        image_url=cloud["url"],
        public_id=cloud["public_id"],
        problem=problem,
        solution=solution
    )

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "success": True,
        "image_url": cloud["url"]
    }
@app.get("/api/issues")
def list_issues():

    issues = get_all_issues()

    result = []

    for i in issues:

        result.append({
            "id": i[0],
            "image_url": i[1],
            "public_id": i[2],
            "problem": i[3],
            "solution": i[4],
            "created_at": i[5]
        })

    return result
@app.post("/api/diagnose-image")
async def diagnose_image(
    file: UploadFile = File(...)
):

    temp_path = f"temp/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = search_issue_image(
        temp_path
    )

    if os.path.exists(temp_path):
        os.remove(temp_path)

    if not result:
        return {
            "success": False,
            "message": "No matching issue found"
        }

    return {
        "success": True,
        "similarity": result["score"],
        "problem": result["problem"],
        "solution": result["solution"]
    }
@app.post("/api/generate-video")
def generate_video_api(req: ChatRequest):
    from services.rag_engine import search
    from services.llm_service import ask_llm
    import json

    try:
        # ---------------- SEARCH ----------------
        results = search(req.message)

        if not results:
            return {"error": "No relevant content"}

        top = sorted(results, key=lambda x: x["score"], reverse=True)[:8]

        context = "\n".join([r["text"] for r in top])

        # ---------------- AI SCENE CREATION ----------------
        prompt = f"""
You are an AI educational video creator.

Create short explainer video scenes.

Return ONLY valid JSON.

Format:
[
  {{
    "scene_title": "Scene title",
    "narration": "Educational narration for students"
  }}
]

Rules:
- 4 to 6 scenes
- educational style
- easy for students
- short narration
- no markdown
- make scenes flow naturally

Context:
{context}

Topic:
{req.message}
"""

        response = ask_llm(prompt)

        response = response.strip()

        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "")

        scenes = json.loads(response)

        # ---------------- VIDEO ----------------
        video_path = generate_video(scenes)

        return {
            "video_path": video_path,
            "scenes": scenes
        }

    except Exception as e:
        print("❌ Video generation error:", e)
        return {"error": str(e)}
# -----------------------------
# SESSIONS
# -----------------------------
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