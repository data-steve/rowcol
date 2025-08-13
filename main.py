from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import engagements, services, tasks, correction, suggestion, policy_profile, document, document_type, user, firm, client, staff, business_entity, engagement_entities,automation,ingest,csv,documents,review,kpi
from database import engine, SessionLocal
from models import Service, Engagement, Task, Rule, VendorCanonical, Correction, Suggestion, PolicyProfile, Document, DocumentType, User, Firm, Client, Staff, BusinessEntity, EngagementEntities
from models.base import Base
import sqlite3  
import asyncio

app = FastAPI(
    title="BookClose API",
    description="Automation and document engine for bookkeeping firms",
    version="0.1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def seed_database():
    """Seed database if empty."""
    try:
        conn = sqlite3.connect("bookclose.db")
        # Check if tables exist and have data
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engagements'")
        if cursor.fetchone():
            # Table exists, check if it has data
            cursor.execute("SELECT COUNT(*) FROM engagements")
            count = cursor.fetchone()[0]
            if count == 0:  # Only seed if empty
                with open("data/seed_data.sql", "r") as f:
                    conn.executescript(f.read())
                conn.commit()
                print("Database seeded successfully.")
        else:
            # Table doesn't exist, seed it
            with open("data/seed_data.sql", "r") as f:
                conn.executescript(f.read())
            conn.commit()
            print("Database seeded successfully.")
        conn.close()
    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.close()

@app.on_event("startup")
async def startup():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Seed database if empty
    seed_database()

app.include_router(engagements.router)
app.include_router(services.router)
app.include_router(tasks.router)
app.include_router(correction.router)
app.include_router(suggestion.router)
app.include_router(policy_profile.router)
app.include_router(document.router)
app.include_router(document_type.router)
app.include_router(user.router)
app.include_router(firm.router)
app.include_router(client.router)
app.include_router(staff.router)
app.include_router(business_entity.router)
app.include_router(engagement_entities.router)
app.include_router(automation.router)
app.include_router(ingest.router)
app.include_router(csv.router)
app.include_router(documents.router)
app.include_router(review.router)
app.include_router(kpi.router)

# In-memory pub/sub simulation
SUBSCRIBERS = []

@app.get("/templates/{template_name}", response_class=HTMLResponse)
async def serve_template(template_name: str):
    return templates.TemplateResponse(f"{template_name}", {"request": {}})

@app.websocket("/ws/engagements")
async def websocket_engagements(websocket: WebSocket):
    await websocket.accept()
    SUBSCRIBERS.append([])
    subscriber_id = len(SUBSCRIBERS) - 1
    try:
        while True:
            if SUBSCRIBERS[subscriber_id]:
                message = SUBSCRIBERS[subscriber_id].pop(0)
                await websocket.send_text(message)
            await asyncio.sleep(0.1)
    finally:
        SUBSCRIBERS.pop(subscriber_id)