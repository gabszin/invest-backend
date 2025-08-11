from fastapi import FastAPI
from .routers_clients import router as clients_router
from .routers_allocations import router as allocations_router

app = FastAPI()
app.include_router(clients_router)
app.include_router(allocations_router)

@app.get("/health")
def health():
    return {"status": "ok"}