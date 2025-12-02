import urllib.request
import urllib.parse
import json
from http.cookiejar import CookieJar

# Setup
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
from database import SessionLocal
from models import Employee, Document
db = SessionLocal()
emp = db.query(Employee).filter(Employee.email == "vineela.m.ext@veolia.com").first()

login_data = urllib.parse.urlencode({"email": emp.email, "password": emp.employee_id}).encode()
opener.open("http://127.0.0.1:5000/login", data=login_data)
print("Logged in.")

# Create New Doc
new_data = urllib.parse.urlencode({
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
    "reviewer": emp.email,
    "signoff_eng": "",
    "drm_cat": "Cat1"
}).encode()
opener.open("http://127.0.0.1:5000/new", data=new_data)
print("Created doc.")

# Get Doc ID
doc = db.query(Document).filter(Document.id == 13).first()
print(f"Doc ID: {doc.id}, Stage: {doc.current_stage_code}")

# Submit Orig 1
orig_data = urllib.parse.urlencode({
    "actual_hours": "5",
    "transmittal_date": "2023-01-02",
    "ref_link": "http://test",
    "description": "Submitted by Orig"
}).encode()
opener.open(f"http://127.0.0.1:5000/submit_cycle/{doc.id}/OriginatorCycle_1", data=orig_data)

db.expire_all()
doc = db.query(Document).filter(Document.id == doc.id).first()
print(f"Stage after Orig 1: {doc.current_stage_code}")

# Submit Rev 1 (Accepted)
rev_data = urllib.parse.urlencode({
    "action": "Accepted",
    "review_hours": "2",
    "major_tool": "0",
    "major_tech": "0",
    "major_std": "0",
    "minor_typo": "0",
    "description": "LGTM"
}).encode()
opener.open(f"http://127.0.0.1:5000/submit_cycle/{doc.id}/ReviewerCycle_1", data=rev_data)

db.expire_all()
doc = db.query(Document).filter(Document.id == doc.id).first()
print(f"Stage after Rev 1 Accepted: {doc.current_stage_code} ({doc.current_stage})")
