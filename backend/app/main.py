from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cart, chat, reviews
from app.config import settings

app = FastAPI(title="AI Multi-Agent Shopping Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router)
app.include_router(cart.router)
app.include_router(reviews.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
