import csv
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Employee

# MySQL Connection (Update password if needed)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:641364@localhost/emt_db"

def import_employees():
    print("--- Starting Employee Import ---")
    
    # 1. Connect to DB
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Create table if it doesn't exist
        Base.metadata.create_all(bind=engine)
        print("Connected to database.")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    # 2. Read CSV
    csv_file = "employee.csv"
    count = 0
    skipped = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            # Skip first 3 lines (empty/garbage)
            for _ in range(3):
                next(f)
                
            reader = csv.DictReader(f)
            
            for row in reader:
                # Skip empty rows or rows without SystemID
                if not row.get('SystemID') or not row.get('Employee Name'):
                    continue
                    
                # Check if employee already exists
                sys_id = row['SystemID'].strip()
                existing = session.query(Employee).filter(Employee.system_id == sys_id).first()
                
                if existing:
                    print(f"Skipping existing employee: {sys_id}")
                    skipped += 1
                    continue
                
                # Create Employee Object
                new_emp = Employee(
                    system_id=sys_id,
                    employee_id=row.get('EMPID', '').strip(),
                    name=row.get('Employee Name', '').strip(),
                    email=row.get('Veolia Email Id', '').strip(),
                    role=row.get('Role', '').strip(),
                    discipline=row.get('Discipline', '').strip(),
                    department=row.get('Sub Discipline', '').strip(),
                    reporting_manager=row.get('ReportingManager', '').strip(),
                    employee_type=row.get('EmployeeType', '').strip(),
                    status=row.get('CurrentEmployeeStatus', 'Active').strip()
                )
                
                session.add(new_emp)
                count += 1
                
                if count % 50 == 0:
                    print(f"Processed {count} employees...")
                    session.commit()

        session.commit()
        print(f"\n--- Import Complete ---")
        print(f"Added: {count}")
        print(f"Skipped (Already Exists): {skipped}")
        
    except FileNotFoundError:
        print(f"[ERROR] File '{csv_file}' not found.")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import_employees()
