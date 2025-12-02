
import requests
from bs4 import BeautifulSoup
from database import SessionLocal
from models import Employee, Project, Document

# Setup DB session
db = SessionLocal()

def get_test_user():
    user = db.query(Employee).filter(Employee.status == 'Active').first()
    if not user:
        print("No active employees found in DB. Cannot run tests.")
        exit(1)
    return user

def get_test_project():
    proj = db.query(Project).first()
    if not proj:
        # Create dummy project if needed
        proj = Project(project_number="TEST-001", project_name="Test Project")
        db.add(proj)
        db.commit()
    return proj

def run_tests():
    user = get_test_user()
    project = get_test_project()
    
    print(f"Testing with User: {user.name} ({user.email})")
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5000"
    
    # 1. Login
    print("\n[Test 1] Logging in...")
    login_data = {
        "email": user.email,
        "password": user.employee_id
    }
    r = session.post(f"{base_url}/login", data=login_data)
    if r.url == f"{base_url}/" or r.url == f"{base_url}/index":
        print("Login Successful.")
    else:
        print(f"Login Failed. URL: {r.url}")
        # exit(1) # Continue anyway to see what happens, maybe already logged in?

    # 2. Check Dropdowns
    print("\n[Test 2] Checking Dropdown Formats...")
    r = session.get(f"{base_url}/new")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    dropdowns = ['doc_owner', 'originator', 'reviewer']
    all_good = True
    for dd_name in dropdowns:
        select = soup.find('select', {'name': dd_name})
        if not select:
            print(f"ERROR: Dropdown {dd_name} not found!")
            all_good = False
            continue
            
        options = select.find_all('option')
        # Skip the first "Select..." option
        if len(options) > 1:
            first_opt = options[1].text.strip()
            print(f"  {dd_name} first option: '{first_opt}'")
            if "(" in first_opt and ")" in first_opt and "@" in first_opt:
                pass # Good
            else:
                print(f"  ERROR: {dd_name} format seems wrong. Expected 'Name (Email)'")
                all_good = False
        else:
            print(f"  WARNING: {dd_name} has no employees.")
            
    if all_good:
        print("Dropdown formats verified.")

    # 3. Test IDR=Yes Logic (Reviewer should be optional)
    print("\n[Test 3] Testing IDR=Yes (Reviewer Optional)...")
    data_idr_yes = {
        "project_no": project.project_number,
        "title": "Test IDR Yes",
        "doc_owner": user.email,
        "originator": user.email,
        "reviewer": "", # Empty reviewer
        "idr_req": "Yes",
        "idr_reviewers": user.email, # Self as IDR reviewer
        "signoff_req": "No",
        "signoff_eng": ""
    }
    r = session.post(f"{base_url}/new", data=data_idr_yes)
    if "New Request" in r.text and "Document Details" in r.text:
         # If we are back at the form, it might be an error or success (if redirect failed)
         # But usually success redirects to index.
         # Let's check for error flash
         if "Error:" in r.text:
             print("FAILED: Got error message when submitting IDR=Yes with empty reviewer.")
         else:
             # Check if we are on index?
             if r.url == f"{base_url}/":
                 print("SUCCESS: Request created.")
             else:
                 # It might have rendered the form again?
                 print(f"Result URL: {r.url}")
    elif r.status_code == 200 and "Dashboard" in r.text: # Assuming index has Dashboard
        print("SUCCESS: Request created (Redirected to Dashboard).")
    else:
        print(f"Unknown state. Status: {r.status_code}, URL: {r.url}")
    
    # Verify in DB
    created_doc = db.query(Document).filter(Document.title == "Test IDR Yes").first()
    if created_doc:
        print(f"DB CHECK: Document found. ID: {created_doc.id}")
        print(f"  Status: '{created_doc.record_status}'")
        print(f"  Owner: '{created_doc.doc_owner}'")
        print(f"  IDR Reviewers: '{created_doc.idr_reviewers}'")
        print(f"  User Email: '{user.email}'")
        
        if created_doc.doc_owner == user.email:
            print("  MATCH: Owner matches User Email.")
        else:
            print("  MISMATCH: Owner does NOT match User Email.")
            
        if created_doc.record_status != "Active":
            print("  WARNING: Record status is not Active.")
    else:
        print("DB CHECK: Document NOT found in DB.")

    # 4. Test IDR=No Logic (Reviewer should be mandatory)
    print("\n[Test 4] Testing IDR=No (Reviewer Mandatory)...")
    data_idr_no = {
        "project_no": project.project_number,
        "title": "Test IDR No",
        "doc_owner": user.email,
        "originator": user.email,
        "reviewer": "", # Empty reviewer, SHOULD FAIL
        "idr_req": "No",
        "idr_reviewers": "",
        "signoff_req": "No",
        "signoff_eng": ""
    }
    r = session.post(f"{base_url}/new", data=data_idr_no)
    if "Please select valid employees" in r.text or "Error" in r.text:
        print("SUCCESS: Validation caught missing reviewer.")
    else:
        print("FAILED: Submission succeeded (or different error) despite missing reviewer.")

    # 5. Dashboard Visibility
    print("\n[Test 5] Checking Dashboard Visibility...")
    r = session.get(f"{base_url}/")
    if "Test IDR Yes" in r.text:
        print("SUCCESS: 'Test IDR Yes' document is visible on dashboard.")
    else:
        print(f"FAILED: 'Test IDR Yes' document NOT found on dashboard.")
        print(f"User Email: {user.email}")
        print(f"Dashboard HTML content length: {len(r.text)}")
        # Check if table exists
        if "<table" in r.text:
            print("Table found.")
        else:
            print("Table NOT found.")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
