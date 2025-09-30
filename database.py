import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Вземаме URL за базата от environment variable
# Ако няма, ползваме локално fallback (например PostgreSQL на localhost)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://air_quality_rghr_user:ycp2dcRlLPI1fbKk3ygiS6RdrmMHmkj0@dpg-d3e2i07diees73fqfvhg-a.frankfurt-postgres.render.com/air_quality_rghr"
)

# Създаваме engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True показва SQL в конзолата (може да се махне)

# Създаваме сесии
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Декларативна база за модели
Base = declarative_base()
