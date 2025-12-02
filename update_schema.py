from database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        # Check if columns exist in 'documents' table
        # This is a bit hacky for MySQL/SQLite but works for adding columns if missing
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN current_stage VARCHAR(255) DEFAULT 'Pending (Originator Cycle 1)'"))
            print("Added current_stage column")
        except Exception as e:
            print(f"current_stage might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN current_status VARCHAR(255) DEFAULT 'Pending'"))
            print("Added current_status column")
        except Exception as e:
            print(f"current_status might already exist: {e}")

        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN doc_owner VARCHAR(255)"))
            print("Added doc_owner column")
        except: pass
        
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN originator VARCHAR(255)"))
            print("Added originator column")
        except: pass

        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN reviewer VARCHAR(255)"))
            print("Added reviewer column")
        except: pass

        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN signoff_eng VARCHAR(255)"))
            print("Added signoff_eng column")
        except: pass

if __name__ == "__main__":
    update_schema()
