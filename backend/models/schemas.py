from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: str

class SourceItem(BaseModel):
    video: str
    start: float
    end: float
    video_url: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

class SessionCreate(BaseModel):
    name: str