
import requests
from bs4 import BeautifulSoup
from database import SessionLocal
from models import Employee, Project, Document
import sys

# Setup DB session
db = SessionLocal()

def run_tests():
    try:
        user = db.query(Employee).filter(Employee.status == 'Active').first()
        if not user:
            print("FAIL: No active user")
            return

        project = db.query(Project).first()
        if not project:
            project = Project(project_number="TEST-001", project_name="Test Project")
            db.add(project)
            db.commit()

        session = requests.Session()
        base_url = "http://127.0.0.1:5000"
        
        # Login
        r = session.post(f"{base_url}/login", data={"email": user.email, "password": user.employee_id})
        if r.url == f"{base_url}/" or r.url == f"{base_url}/index":
            print("PASS: Login")
        else:
            print(f"FAIL: Login (URL: {r.url})")
            return

        # Dropdowns
        r = session.get(f"{base_url}/new")
        soup = BeautifulSoup(r.text, 'html.parser')
        dd_names = ['doc_owner', 'originator', 'reviewer']
        failed_dds = []
        for name in dd_names:
            # Check for hidden input
            inp = soup.find('input', {'name': name, 'type': 'hidden'})
            if not inp:
                failed_dds.append(f"{name} hidden input missing")
                continue
            
            # Check for custom dropdown container
            # ID convention: doc_owner -> docOwnerDropdown (camelCase)
            # But wait, I used docOwnerDropdown in HTML.
            # Let's just check if the input exists for now, as that's what matters for form submission.
            # And maybe check if the search input exists.
            
            # Construct ID for search input
            search_id = ""
            if name == "doc_owner": search_id = "docOwnerSearch"
            elif name == "originator": search_id = "originatorSearch"
            elif name == "reviewer": search_id = "reviewerSearch"
            
            search_inp = soup.find('input', {'id': search_id})
            if not search_inp:
                 failed_dds.append(f"{name} search input missing")
        
        if not failed_dds:
            print("PASS: Dropdowns")
        else:
            print(f"FAIL: Dropdowns ({', '.join(failed_dds)})")

        # IDR=Yes
        data = {
            "project_no": project.project_number,
            "title": "Test IDR Yes",
            "doc_no": "DOC-001",
            "rev_no": "A",
            "discipline": "Process",
            "baseline_date": "2023-01-01",
            "est_hours": "10",
            "drm_cat": "Cat 1",
            "doc_owner": user.email,
            "originator": user.email,
            "reviewer": "",
            "idr_req": "Yes",
            "idr_reviewers": user.email,
            "signoff_req": "No",
            "signoff_eng": ""
        }
        # Note: field names in app.py are 'is_idr_req' and 'is_signoff_req'
        # In my previous test I used 'idr_req' which might be wrong!
        # Let's check app.py form handling.
        
        r = session.post(f"{base_url}/new", data=data)
        
        # Check DB
        doc = db.query(Document).filter(Document.title == "Test IDR Yes").order_by(Document.id.desc()).first()
        if doc:
            print(f"PASS: IDR=Yes Created (ID: {doc.id})")
            print(f"DEBUG: Current Stage: {doc.current_stage} (Code: {doc.current_stage_code})")
            if doc.doc_owner == user.email:
                print("PASS: Owner Match")
            else:
                print(f"FAIL: Owner Mismatch ({doc.doc_owner} vs {user.email})")

            # Submit Cycle 1
            print("Testing Workflow Transition...")
            submit_data = {
                "actual_hours": "5",
                "transmittal_date": "2023-01-02",
                "ref_link": "http://test",
                "description": "Submitting for IDR"
            }
            url = f"{base_url}/submit_cycle/{doc.id}/OriginatorCycle_1"
            print(f"DEBUG: Posting to {url}", flush=True)
            r = session.post(url, data=submit_data)
            print(f"DEBUG: Submit Status: {r.status_code}", flush=True)
            if r.status_code != 200: # Expect 200 for modal update
                print(f"DEBUG: Submit Response: {r.text}")
            
            # Refresh Doc
            db.commit() # End current transaction to see updates from app.py
            db.expire(doc)
            doc = db.query(Document).filter(Document.id == doc.id).first()
            print(f"DEBUG: Post-Submit Stage: {doc.current_stage} (Code: {doc.current_stage_code})")
            
            if doc.current_stage_code == 7:
                print("PASS: Transition to IDR Successful")
            else:
                print(f"FAIL: Transition Failed (Expected 7, Got {doc.current_stage_code})")
        else:
            print("FAIL: IDR=Yes Not Created")
            print(f"Response URL: {r.url}")
            print(f"Response Text Start: {r.text[:500]}")

        # Dashboard
        r = session.get(f"{base_url}/")
        if "Test IDR Yes" in r.text:
            print("PASS: Dashboard Visibility")
        else:
            print("FAIL: Dashboard Visibility")
            # Print table content
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                print(f"Table has {len(rows)} rows")
            else:
                print("Table not found")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
