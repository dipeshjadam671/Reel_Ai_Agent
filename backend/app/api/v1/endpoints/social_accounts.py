from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from backend.app.schemas.publishing import SocialAccountOut, SocialConnectRequest
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

# In-memory / tenant-scoped connected accounts store
_connected_accounts = {
    "youtube": {"connected": True, "account_name": "@AutonomousAIChannel"},
    "instagram": {"connected": True, "account_name": "@autonomous.ai.reels"},
    "tiktok": {"connected": True, "account_name": "@ai_agent_shorts"}
}

@router.get("", response_model=List[SocialAccountOut])
async def list_social_accounts(workspace_id: str = Depends(get_current_workspace_id)):
    out = []
    for platform, data in _connected_accounts.items():
        out.append(SocialAccountOut(
            platform=platform,
            account_name=data["account_name"],
            connected=data["connected"],
            last_synced=datetime.now(timezone.utc)
        ))
    return out

@router.post("/connect", response_model=SocialAccountOut)
async def connect_social_account(
    req: SocialConnectRequest,
    workspace_id: str = Depends(get_current_workspace_id)
):
    _connected_accounts[req.platform.lower()] = {
        "connected": True,
        "account_name": f"@Connected_{req.platform.title()}"
    }
    return SocialAccountOut(
        platform=req.platform.lower(),
        account_name=f"@Connected_{req.platform.title()}",
        connected=True,
        last_synced=datetime.now(timezone.utc)
    )
