from database import SessionLocal
from models import Document

db = SessionLocal()
doc = db.query(Document).order_by(Document.id.desc()).first()

if doc:
    print(f"ID: {doc.id}")
    print(f"Request ID: {doc.request_id}")
    print(f"Current Stage Code: {doc.current_stage_code} (Type: {type(doc.current_stage_code)})")
    print(f"Current Stage Name: {doc.current_stage}")
    print(f"Originator: '{doc.originator}'")
    print(f"Doc Owner: '{doc.doc_owner}'")
    print(f"Reviewer: '{doc.reviewer}'")
else:
    print("No documents found.")
