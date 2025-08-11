from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    allocations = relationship("Allocation", back_populates="client", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(Date, nullable=False)
    __table_args__ = (UniqueConstraint("client_id", "asset_id", name="uq_client_asset"),)
    client = relationship("Client", back_populates="allocations")
    asset = relationship("Asset")

class DailyReturn(Base):
    __tablename__ = "daily_returns"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    close_price = Column(Float, nullable=False)