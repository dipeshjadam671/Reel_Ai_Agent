from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    workspace_id: Optional[str] = None
    role: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    workspace_id: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool

class WorkspaceCreate(BaseModel):
    name: str
    monthly_budget_usd: Optional[float] = 50.0

class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    monthly_budget_usd: float
    current_spend_usd: float
