from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from domains import router
from database import engine, seed_database

from domains.core.models.base import Base
import asyncio

app = FastAPI(
    title="Oodaloo Runway API",
    description="Cash runway management for single-business agencies",
    version="0.1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Seed database if empty
    seed_database()

# Include all routes via consolidated router
app.include_router(router)

# In-memory pub/sub simulation
SUBSCRIBERS = []

@app.get("/templates/{template_name}", response_class=HTMLResponse)
async def serve_template(template_name: str):
    return templates.TemplateResponse(f"{template_name}", {"request": {}})

# @app.websocket("/ws/engagements")
# async def websocket_engagements(websocket: WebSocket):
#     await websocket.accept()
#     SUBSCRIBERS.append([])
#     subscriber_id = len(SUBSCRIBERS) - 1
#     try:
#         while True:
#             if SUBSCRIBERS[subscriber_id]:
#                 message = SUBSCRIBERS[subscriber_id].pop(0)
#                 await websocket.send_text(message)
#             await asyncio.sleep(0.1)
#     finally:
#         SUBSCRIBERS.pop(subscriber_id)