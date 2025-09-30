from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    parameter = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime)
