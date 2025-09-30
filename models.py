from sqlalchemy import Column, Integer, String, Float
from database import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    parameter = Column(String, index=True)  # напр. pm25, pm10
    value = Column(Float)
    timestamp = Column(String)  # или DateTime, ако предпочиташ
