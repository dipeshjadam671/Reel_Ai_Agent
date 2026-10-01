from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import BudgetExceededError
from backend.app.db.models.workspace import Workspace
from backend.app.db.models.spend import SpendLedger
from backend.app.core.logging import logger

# Cost catalog per unit (USD)
UNIT_COSTS = {
    "llm_token_input": 0.00000015,   # $0.15 per 1M tokens
    "llm_token_output": 0.00000060,  # $0.60 per 1M tokens
    "tts_character": 0.000015,       # $15 per 1M characters
    "avatar_video_second": 0.015,    # ~$0.90 per minute
    "stock_video_clip": 0.05,        # $0.05 per asset lookup/download
    "render_minute": 0.01,           # Compute render cost
    "mock_operation": 0.00,          # Zero cost in mock mode
}

class CostService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workspace_spend(self, workspace_id: str) -> float:
        stmt = select(func.sum(SpendLedger.amount)).where(SpendLedger.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        total = result.scalar_one_or_none()
        return float(total) if total is not None else 0.0

    async def check_budget_available(self, workspace_id: str, estimated_amount: float = 0.0) -> bool:
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        result = await self.session.execute(stmt)
        workspace = result.scalars().first()
        if not workspace:
            return False

        current_spend = await self.get_workspace_spend(workspace_id)
        if current_spend + estimated_amount > workspace.monthly_budget_usd:
            logger.warning(
                f"Budget exceeded for workspace {workspace_id}: current=${current_spend:.2f}, estimated=${estimated_amount:.2f}, cap=${workspace.monthly_budget_usd:.2f}",
                extra={"workspace_id": workspace_id, "event": "budget_check", "status": "exceeded", "duration": 0, "cost": current_spend}
            )
            return False
        return True

    async def record_spend(
        self,
        workspace_id: str,
        provider: str,
        operation: str,
        units: float,
        cycle_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        is_mock: bool = False
    ) -> SpendLedger:
        # Check idempotency
        if idempotency_key:
            stmt = select(SpendLedger).where(SpendLedger.idempotency_key == idempotency_key)
            existing = (await self.session.execute(stmt)).scalars().first()
            if existing:
                return existing

        unit_cost = 0.0 if is_mock else UNIT_COSTS.get(operation, 0.001)
        amount = units * unit_cost

        # Verify budget before committing spend
        if not is_mock and amount > 0:
            allowed = await self.check_budget_available(workspace_id, amount)
            if not allowed:
                raise BudgetExceededError(f"Workspace monthly budget cap reached. Cannot proceed with {operation}.")

        entry = SpendLedger(
            workspace_id=workspace_id,
            cycle_id=cycle_id,
            provider=provider,
            operation=operation,
            units=units,
            unit_cost=unit_cost,
            amount=amount,
            currency="USD",
            idempotency_key=idempotency_key
        )
        self.session.add(entry)

        # Update cached workspace spend
        ws_stmt = select(Workspace).where(Workspace.id == workspace_id)
        workspace = (await self.session.execute(ws_stmt)).scalars().first()
        if workspace:
            workspace.current_spend_usd += amount

        await self.session.flush()
        return entry
