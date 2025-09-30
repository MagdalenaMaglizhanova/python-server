from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class AirQualityMeasurement(Base):
    __tablename__ = "air_quality_measurements"  # името на таблицата според предложението


    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=False)          # задължително, защото всеки агент трябва да се идентифицира
    source = Column(String, nullable=False)            # AQICN / IQAir
    parameter = Column(String, index=True, nullable=False)  # PM2.5, PM10, Temperature, ...
    value = Column(Float, nullable=True)              # стойност, може да е NULL ако липсва
    timestamp = Column(DateTime, nullable=False)       # дата и час на измерването
