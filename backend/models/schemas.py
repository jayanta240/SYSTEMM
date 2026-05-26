from pydantic import BaseModel
from typing import List, Optional


# -----------------------------
# REQUEST MODEL
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str
    mode: Optional[str] = "normal"


# -----------------------------
# SOURCE MODEL (FIXED)
# -----------------------------
class SourceItem(BaseModel):
    type: str

    # video
    video: Optional[str] = None
    video_url: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None

    # document
    source: Optional[str] = None
    page: Optional[int] = None


# -----------------------------
# RESPONSE MODEL
# -----------------------------
class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]