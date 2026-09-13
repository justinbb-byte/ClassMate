from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..chat.intents import reply
from ..schemas import ChatRequest, ChatResponse
from .common import get_store, state_out

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, store=Depends(get_store)):
    state = state_out(store)
    # state_out uses API names; the rule engine intentionally reads only these
    # fields, so this conversion keeps chat behaviour close to client data.
    internal = store.snapshot()
    return reply(payload.message, internal, datetime.now(timezone.utc))
