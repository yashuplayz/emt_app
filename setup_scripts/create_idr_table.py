from database import SessionLocal, engine
from models import Base, IDRReview

def migrate():
    print("Creating IDRReview table...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    migrate()
