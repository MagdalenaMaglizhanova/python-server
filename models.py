from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import AirQuality

# Създаваме таблиците, ако не съществуват
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality API")

# Зависимост за DB сесия
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Тестов endpoint ---
@app.get("/")
def read_root():
    return {"message": "API работи успешно!"}

# --- Вземане на всички данни ---
@app.get("/air_quality")
def get_all_air_quality(db: Session = Depends(get_db)):
    data = db.query(AirQuality).all()
    return data

# --- Филтриране по параметър ---
@app.get("/air_quality/{parameter}")
def get_parameter_data(parameter: str, db: Session = Depends(get_db)):
    data = db.query(AirQuality).filter(AirQuality.parameter == parameter).all()
    if not data:
        raise HTTPException(status_code=404, detail="Няма данни за този параметър")
    return data
