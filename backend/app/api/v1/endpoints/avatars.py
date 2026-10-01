from typing import Any, Dict, List
from fastapi import APIRouter
from backend.app.integrations.avatar.providers.video_presenter import get_available_personas

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
async def list_avatars():
    """
    List all available studio video presenter avatar personas
    with explicit gender classifications (Male/Female), roles, badges,
    accent themes, and recommended neural voice models.
    """
    return get_available_personas()
