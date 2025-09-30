from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=True)  # <- ново поле за агента
    parameter = Column(String, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
