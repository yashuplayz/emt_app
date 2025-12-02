import csv
import os
from database import SessionLocal, init_db
from models import Project

# 1. Initialize Database (Creates tables if missing)
init_db()
db = SessionLocal()

def import_projects():
    csv_file = 'projects.csv'
    print(f"🚀 Reading {csv_file}...")

    if not os.path.exists(csv_file):
        print(f"❌ Error: '{csv_file}' not found in the current folder.")
        return

    try:
        # 'utf-8-sig' handles BOM characters often found in Excel exports
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            headers = []
            header_row_index = 0
            
            # --- STEP 1: FIND THE HEADER ROW (Scanning for 'Project Number') ---
            print("🔍 Scanning for headers...")
            for index, row in enumerate(reader):
                # Join row to string for easy case-insensitive searching
                row_str = ",".join(row).lower()
                
                # Check for key columns to identify the header row
                if "project number" in row_str and "project name" in row_str:
                    headers = row
                    header_row_index = index
                    print(f"✅ Found Headers on Row {index + 1}")
                    # print(f"   Headers: {headers}") # Uncomment to see exact headers
                    break
            
            if not headers:
                print("❌ Error: Could not find a valid header row containing 'Project Number' and 'Project Name'.")
                return

            # --- STEP 2: RESET FILE & SKIP TO DATA ---
            f.seek(0) # Go back to start of file
            # Skip all lines up to and including the header row
            for _ in range(header_row_index + 1):
                next(f)
            
            # Use DictReader to map columns automatically based on found headers
            dict_reader = csv.DictReader(f, fieldnames=headers)
            
            count = 0
            skipped = 0
            updated = 0
            
            # Track IDs seen in this specific run to handle duplicates inside the CSV
            seen_in_csv = set()

            print("🔄 Processing rows...")

            for i, row in enumerate(dict_reader):
                # --- STEP 3: MAP DATA (Using your specific column names) ---
                
                # Primary ID
                p_num = row.get('Project Number')
                
                # Name (Fallback to 'Project Number Name' if Name is empty)
                p_name = row.get('Project Name')
                if not p_name or p_name.strip() == "":
                    p_name = row.get('Project Number Name')

                # Extra Fields (From your screenshot)
                p_region = row.get('Exe Proj Region')
                p_desc = row.get('Project Description')
                p_status = row.get('Project Status')
                p_category = row.get('Category')

                # --- STEP 4: VALIDATION & CLEANING ---
                
                # A. Check for garbage data (Empty IDs or '0')
                if not p_num or p_num.strip() == "" or p_num.strip() == "0":
                    skipped += 1
                    continue

                # Clean whitespace
                p_num = p_num.strip()
                p_name = p_name.strip() if p_name else p_num # Fallback name to ID if still empty
                
                # B. Check for duplicates INSIDE the CSV file
                if p_num in seen_in_csv:
                    skipped += 1
                    continue
                seen_in_csv.add(p_num)

                # --- STEP 5: DATABASE OPERATION ---
                
                # Check if project already exists in SQL
                existing_project = db.query(Project).filter_by(project_number=p_num).first()
                
                try:
                    if not existing_project:
                        # CREATE NEW
                        new_proj = Project(
                            project_number=p_num, 
                            project_name=p_name,
                            region=p_region,
                            description=p_desc,
                            status=p_status
                        )
                        db.add(new_proj)
                        count += 1
                    else:
                        # OPTIONAL: UPDATE EXISTING (If you want to sync changes)
                        # existing_project.project_name = p_name
                        # existing_project.region = p_region
                        # existing_project.description = p_desc
                        # existing_project.status = p_status
                        # updated += 1
                        skipped += 1 # Counting existing as skipped for now
                    
                    # Commit in batches or per row (safer per row for import scripts)
                    db.commit()

                except Exception as e:
                    db.rollback() # Undo the failed insert
                    print(f"   ❌ Database Error on {p_num}: {e}")
                    skipped += 1

            print("-" * 30)
            print(f"✅ IMPORT COMPLETE")
            print(f"   Added New: {count}")
            print(f"   Skipped (Duplicates/Bad Data): {skipped}")
            print("-" * 30)

    except Exception as e:
        print(f"❌ Critical Script Error: {e}")

if __name__ == "__main__":
    import_projects()