from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    is_active: bool = True

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class ClientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    model_config = {"from_attributes": True}