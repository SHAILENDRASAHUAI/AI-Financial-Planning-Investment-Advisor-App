from fastapi import FastAPI

from .api import router
from .models import DISCLAIMER

app = FastAPI(title="Smart Wealth Planner AI API", version="1.0.0")
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "app": "Smart Wealth Planner AI",
        "disclaimer": DISCLAIMER,
    }
