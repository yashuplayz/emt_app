from database import SessionLocal, engine
from models import Base

# This will create any missing tables/columns if using SQLite and they don't exist.
# However, SQLAlchemy `create_all` does NOT migrate existing tables (add columns).
# Since this is dev, we can just use a raw SQL command to add the column if it's missing.
import sqlalchemy

def add_column():
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE documents ADD COLUMN idr_reviewers VARCHAR(255)"))
            print("Added idr_reviewers column.")
        except Exception as e:
            print(f"Column might already exist: {e}")

if __name__ == "__main__":
    add_column()
