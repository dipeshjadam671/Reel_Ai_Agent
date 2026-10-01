from typing import Any, Dict
from fastapi import APIRouter, Header, Request, status
from backend.app.core.logging import logger

router = APIRouter()

@router.post("/{provider}", status_code=status.HTTP_200_OK)
async def handle_provider_webhook(
    provider: str,
    request: Request,
    x_signature: str = Header(None, alias="X-Signature")
):
    body = await request.json()
    logger.info(f"Received webhook callback from provider '{provider}': {body}")
    # Updates async task or notifies LangGraph resumption thread if applicable
    return {"status": "received", "provider": provider}
