from database import SessionLocal, engine
from models import Base, IDRReview
from sqlalchemy import text

def migrate():
    print("Dropping old IDRReview table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS idr_reviews"))
        conn.commit()
    
    print("Creating new IDRReview table...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    migrate()
