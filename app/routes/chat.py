from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, AnalyticsResponse
from app.services.agent import chat
from app.services.analytics import generate_analytics


router = APIRouter()


conversations = {}


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):

    session_id = request.session_id

    if session_id not in conversations:
        conversations[session_id] = []

    conversations[session_id].append({
        "role": "user",
        "content": request.message
    })

    response = chat(
        conversations[session_id]
    )

    conversations[session_id].append({
        "role": "assistant",
        "content": response
    })

    return {
        "session_id": session_id,
        "response": response
    }


@router.get("/analytics/{session_id}", response_model=AnalyticsResponse)
def analytics_endpoint(session_id: str):

    if session_id not in conversations or not conversations[session_id]:
        raise HTTPException(
            status_code=404,
            detail="No conversation found for this session_id"
        )

    analytics = generate_analytics(conversations[session_id])

    return {
        "session_id": session_id,
        "analytics": analytics
    }


@router.delete("/session/{session_id}")
def end_session(session_id: str):

    conversations.pop(session_id, None)

    return {
        "session_id": session_id,
        "status": "ended"
    }
