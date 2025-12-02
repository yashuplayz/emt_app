from database import SessionLocal
from models import Document, CycleData

db = SessionLocal()
doc = db.query(Document).filter(Document.id == 12).first()

if doc:
    print(f"Doc ID: {doc.id}")
    print(f"Current Stage: {doc.current_stage} ({doc.current_stage_code})")
    print(f"IDR: {doc.is_idr_required}, SO: {doc.is_signoff_required}")
    cycles = db.query(CycleData).filter(CycleData.doc_id == doc.id).order_by(CycleData.id).all()
    for c in cycles:
        print(f"[{c.id}] {c.stage_name}: {c.action}")
else:
    print("No documents found.")
