from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .db import get_session
from .models import Client, Asset, Allocation

router = APIRouter(prefix="/allocations", tags=["allocations"])

@router.post("/assets/{ticker}", status_code=201)
async def ensure_asset(ticker: str, session: AsyncSession = Depends(get_session)):
    t = ticker.upper().strip()
    exists = await session.scalar(select(Asset).where(Asset.ticker == t))
    if exists:
        return {"id": exists.id, "ticker": exists.ticker}

    from . import services_price
    quote = services_price.get_quote(t)

    if not quote:
        raise HTTPException(422, detail="ticker inválido ou sem dados")

    if isinstance(quote, dict) and quote.get("error") == "rate_limited":
        raise HTTPException(429, detail="limite de requisições do provedor atingido; tente novamente em instantes")

    asset = Asset(ticker=t)
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return {"id": asset.id, "ticker": asset.ticker}

@router.post("/clients/{client_id}/asset/{ticker}", status_code=201)
async def add_allocation(client_id: int, ticker: str, quantity: float, buy_price: float, buy_date: str,
                         session: AsyncSession = Depends(get_session)):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(404, "cliente não encontrado")
    t = ticker.upper().strip()
    asset = await session.scalar(select(Asset).where(Asset.ticker == t))
    if not asset:
        raise HTTPException(422, "ativo inexistente — crie via /allocations/assets/{ticker}")
    from datetime import date
    alloc = Allocation(client_id=client_id, asset_id=asset.id,
                       quantity=quantity, buy_price=buy_price,
                       buy_date=date.fromisoformat(buy_date))
    session.add(alloc)
    await session.commit()
    await session.refresh(alloc)
    return {"id": alloc.id}

@router.get("/clients/{client_id}")
async def list_client_allocations(client_id: int, session: AsyncSession = Depends(get_session)):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(404, "cliente não encontrado")
    rows = (await session.execute(select(Allocation).where(Allocation.client_id == client_id))).scalars().all()
    out = []
    for a in rows:
        # enriquecer com preço e rentabilidade
        asset = await session.get(Asset, a.asset_id)
        quote = get_quote(asset.ticker) or {"price": None, "previous_close": None, "change_pct": None}
        price = quote["price"]
        pnl_abs = None
        pnl_pct = None
        if price is not None:
            pnl_abs = (price - a.buy_price) * a.quantity
            if a.buy_price > 0:
                pnl_pct = (price/a.buy_price - 1.0) * 100.0
        out.append({
            "allocation_id": a.id,
            "ticker": asset.ticker,
            "quantity": a.quantity,
            "buy_price": a.buy_price,
            "buy_date": str(a.buy_date),
            "price_now": price,
            "day_change_pct": quote["change_pct"],
            "pnl_abs": pnl_abs,
            "pnl_pct": pnl_pct,
        })
    return out