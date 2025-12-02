import requests
import re

# 1. Login
session = requests.Session()
login_url = "http://127.0.0.1:5000/login"
# Assuming 'admin' or similar exists, or I can just pick an employee from CSV
# I'll use the one from the debug output: vineela.m.ext@veolia.com
# Wait, I need the Employee ID as password.
# I'll check employee.csv
with open("employee.csv", "r") as f:
    for line in f:
        if "vineela.m.ext@veolia.com" in line:
            parts = line.split(",")
            # SystemID, EMPID, Name, Email...
            # Assuming CSV format.
            # Let's just try to find the email and pick the 2nd column?
            pass

# Actually, I can just look at the database using python.
from database import SessionLocal
from models import Employee
db = SessionLocal()
emp = db.query(Employee).filter(Employee.email == "vineela.m.ext@veolia.com").first()
if not emp:
    print("Employee not found")
    exit()

print(f"Logging in as {emp.name} ({emp.email}) with pass {emp.employee_id}")
response = session.post(login_url, data={"email": emp.email, "password": emp.employee_id})
print(f"Login Status: {response.status_code}")

# 2. Create New Doc
new_url = "http://127.0.0.1:5000/new"
data = {
    "project_no": "P123",
    "doc_no": "D123",
    "rev_no": "A",
    "title": "Test Doc",
    "discipline": "Process",
    "baseline_date": "2023-01-01",
    "est_hours": "10",
    "idr_req": "No",
    "signoff_req": "No",
    "doc_owner": emp.email,
    "originator": emp.email,
    "reviewer": emp.email, # Self-review for testing
    "signoff_eng": "",
    "drm_cat": "Cat1"
}
response = session.post(new_url, data=data)
print(f"Create Status: {response.status_code}")

# Get the new doc ID
from models import Document
doc = db.query(Document).order_by(Document.id.desc()).first()
print(f"Created Doc ID: {doc.id}, Stage: {doc.current_stage_code}")

# 3. Submit Originator Cycle 1
submit_url = f"http://127.0.0.1:5000/submit_cycle/{doc.id}/OriginatorCycle_1"
data = {
    "actual_hours": "5",
    "transmittal_date": "2023-01-02",
    "ref_link": "http://test",
    "description": "Submitted by Orig"
}
response = session.post(submit_url, data=data)
print(f"Submit Orig 1 Status: {response.status_code}")

# Refresh doc
db.expire_all()
doc = db.query(Document).filter(Document.id == doc.id).first()
print(f"Stage after Orig 1: {doc.current_stage_code} ({doc.current_stage})")

# 4. Submit Reviewer Cycle 1 (ACCEPTED)
submit_url = f"http://127.0.0.1:5000/submit_cycle/{doc.id}/ReviewerCycle_1"
data = {
    "action": "Accepted",
    "review_hours": "2",
    "major_tool": "0",
    "major_tech": "0",
    "major_std": "0",
    "minor_typo": "0",
    "description": "LGTM"
}
response = session.post(submit_url, data=data)
print(f"Submit Rev 1 (Accepted) Status: {response.status_code}")

# Refresh doc
db.expire_all()
doc = db.query(Document).filter(Document.id == doc.id).first()
print(f"Stage after Rev 1 Accepted: {doc.current_stage_code} ({doc.current_stage})")
