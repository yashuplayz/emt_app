import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Document, CycleData, Project

# --- CONFIGURATION ---
# 1. SQLite (Source)
SQLITE_URL = "sqlite:///./emt.db"

# 2. MySQL (Destination) - UPDATE THESE CREDENTIALS!
# Format: mysql+pymysql://<username>:<password>@<host>/<database_name>
MYSQL_USER = "root"
MYSQL_PASSWORD = "641364"  # <--- CHANGE THIS to your MySQL password
MYSQL_HOST = "localhost"
MYSQL_DB = "emt_db"

MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

def migrate():
    print("--- Starting Migration ---")
    
    # 1. Connect to SQLite (Source)
    print(f"Connecting to Source: {SQLITE_URL}")
    sqlite_engine = create_engine(SQLITE_URL)
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    source_session = SQLiteSession()
    
    # 2. Connect to MySQL (Destination)
    # First, create the DB if it doesn't exist
    MYSQL_ROOT_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}"
    try:
        root_engine = create_engine(MYSQL_ROOT_URL)
        with root_engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"))
        print(f"Database '{MYSQL_DB}' checked/created.")
    except Exception as e:
        with open("db_creation_error.txt", "w") as f:
            f.write(str(e))
        print(f"[WARNING] Could not create database automatically: {e}")

    print(f"Connecting to Destination: {MYSQL_URL}")
    try:
        mysql_engine = create_engine(MYSQL_URL)
        MySQLSession = sessionmaker(bind=mysql_engine)
        dest_session = MySQLSession()
        
        # Test connection
        with mysql_engine.connect() as conn:
            pass
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(str(e))
        print(f"\n[ERROR] Could not connect to MySQL: {e}")
        print("Please check your username, password, and ensure the database 'emt_db' exists.")
        return

    # 3. Create Tables in MySQL (if they don't exist)
    print("Creating tables in MySQL...")
    try:
        Base.metadata.drop_all(bind=mysql_engine) # Clean start
        Base.metadata.create_all(bind=mysql_engine)
    except Exception as e:
        with open("create_tables_error.txt", "w") as f:
            f.write(str(e))
        print(f"Error creating tables: {e}")
        return
    
    # 4. Fetch Data from Source
    try:
        print("Fetching data from SQLite...", flush=True)
        projects = source_session.query(Project).all()
        documents = source_session.query(Document).all()
        
        # --- MIGRATE PROJECTS ---
        print(f"Migrating {len(projects)} Projects...", flush=True)
        for p in projects:
            new_p = Project(
                project_number=p.project_number,
                project_name=p.project_name,
                region=p.region,
                description=p.description,
                status=p.status
            )
            dest_session.add(new_p)
        
        # --- MIGRATE DOCUMENTS & CYCLES ---
        print(f"Migrating {len(documents)} Documents...", flush=True)
        for d in documents:
            # Create Document
            new_doc = Document(
                request_id=d.request_id,
                project_no=d.project_no,
                doc_number=d.doc_number,
                revision_number=d.revision_number,
                title=d.title,
                discipline=d.discipline,
                baseline_date=d.baseline_date,
                estimation_hours=d.estimation_hours,
                is_idr_required=d.is_idr_required,
                is_signoff_required=d.is_signoff_required,
                drm_category=d.drm_category,
                doc_owner=d.doc_owner,
                originator=d.originator,
                reviewer=d.reviewer,
                signoff_eng=d.signoff_eng,
                current_status=d.current_status,
                current_stage_code=d.current_stage_code,
                record_status=d.record_status
            )
            dest_session.add(new_doc)
            dest_session.flush() # Generate ID for new_doc to use in cycles
            
            # Migrate Cycles for this document
            for c in d.cycles:
                new_cycle = CycleData(
                    doc_id=new_doc.id, # Link to the NEW document ID
                    stage_name=c.stage_name,
                    actual_hours=c.actual_hours,
                    transmittal_date=c.transmittal_date,
                    ref_link=c.ref_link,
                    description=c.description,
                    action=c.action,
                    review_hours=c.review_hours,
                    major_tool=c.major_tool,
                    major_tech=c.major_tech,
                    major_std=c.major_std,
                    minor_typo=c.minor_typo,
                    signoff_decision=c.signoff_decision,
                    signoff_hours=c.signoff_hours,
                    signoff_comments=c.signoff_comments,
                    timestamp=c.timestamp
                )
                dest_session.add(new_cycle)

        # 5. Commit
        print("Saving to MySQL...", flush=True)
        dest_session.commit()
        print("SUCCESS! Migration complete.", flush=True)

    except Exception as e:
        with open("migration_error.txt", "w") as f:
            f.write(str(e))
        print(f"[ERROR] Migration failed: {e}", flush=True)
        dest_session.rollback()
    finally:
        source_session.close()
        dest_session.close()

if __name__ == "__main__":
    migrate()
