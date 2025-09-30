from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import AirQuality

# Създаваме таблиците
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
