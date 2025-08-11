from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .db import get_session
from .models import Client
from .schemas import ClientCreate, ClientUpdate, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("", response_model=ClientOut, status_code=201)
async def create_client(payload: ClientCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.scalar(select(Client).where(Client.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="email already exists")
    obj = Client(name=payload.name, email=payload.email, is_active=payload.is_active)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

@router.get("", response_model=List[ClientOut])
async def list_clients(
    q: Optional[str] = Query(None, description="search by name/email"),
    status: Optional[bool] = Query(None, description="filter by active status"),
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Client)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(Client.name.ilike(like), Client.email.ilike(like)))
    if status is not None:
        stmt = stmt.where(Client.is_active == status)
    stmt = stmt.order_by(Client.id).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return rows

@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int, session: AsyncSession = Depends(get_session)):
    obj = await session.get(Client, client_id)
    if not obj:
        raise HTTPException(status_code=404, detail="not found")
    return obj

@router.put("/{client_id}", response_model=ClientOut)
async def update_client(client_id: int, payload: ClientUpdate, session: AsyncSession = Depends(get_session)):
    obj = await session.get(Client, client_id)
    if not obj:
        raise HTTPException(status_code=404, detail="not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj

@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: int, session: AsyncSession = Depends(get_session)):
    obj = await session.get(Client, client_id)
    if obj:
        await session.delete(obj)
        await session.commit()