from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import AirQuality
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Създаваме таблиците
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- GET endpoints ---
@app.get("/")
def read_root():
    return {"message": "API работи успешно!"}

@app.get("/air_quality")
def get_all_air_quality(db: Session = Depends(get_db)):
    data = db.query(AirQuality).all()
    return data

@app.get("/air_quality/{parameter}")
def get_parameter_data(parameter: str, db: Session = Depends(get_db)):
    data = db.query(AirQuality).filter(AirQuality.parameter == parameter).all()
    if not data:
        raise HTTPException(status_code=404, detail="Няма данни за този параметър")
    return data

# --- POST endpoint за получаване на данни от агента ---
class AirQualityPayload(BaseModel):
    agent_id: str
    timestamp: datetime
    source: str
    parameter: str
    value: float

@app.post("/air_quality")
def receive_air_quality(payload: List[AirQualityPayload], db: Session = Depends(get_db)):
    records_added = 0
    for item in payload:
        record = AirQuality(
            agent_id=item.agent_id,
            timestamp=item.timestamp,
            source=item.source,
            parameter=item.parameter,
            value=item.value
        )
        db.add(record)
        records_added += 1
    db.commit()
    return {"message": f"{records_added} записа успешно добавени."}
