from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import Base, engine, SessionLocal
from models import AirQualityData
from datetime import datetime

# Създай таблиците
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality API")

class DataEntry(BaseModel):
    agent_id: str
    timestamp: str
    source: str
    parameter: str
    value: float

@app.post("/data")
async def receive_data(entries: List[DataEntry]):
    db = SessionLocal()
    try:
        for entry in entries:
            ts = datetime.fromisoformat(entry.timestamp)
            db_entry = AirQualityData(
                agent_id=entry.agent_id,
                timestamp=ts,
                source=entry.source,
                parameter=entry.parameter,
                value=entry.value
            )
            db.add(db_entry)
        db.commit()
        return {"status": "success", "received": len(entries)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/data")
async def get_data():
    db = SessionLocal()
    try:
        entries = db.query(AirQualityData).all()
        return [
            {
                "agent_id": e.agent_id,
                "timestamp": e.timestamp.isoformat(),
                "source": e.source,
                "parameter": e.parameter,
                "value": e.value
            } for e in entries
        ]
    finally:
        db.close()
