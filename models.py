from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class AirQualityData(Base):
    __tablename__ = "air_quality"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True)
    timestamp = Column(DateTime)
    source = Column(String)
    parameter = Column(String)
    value = Column(Float)
