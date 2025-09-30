import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("postgresql://air_quality_rghr_user:ycp2dcRlLPI1fbKk3ygiS6RdrmMHmkj0@dpg-d3e2i07diees73fqfvhg-a.frankfurt-postgres.render.com/air_quality_rghr")  # Вече ще има стойност

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
