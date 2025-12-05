from database import SessionLocal, init_db
from models import Employee

init_db()
db = SessionLocal()

# Add test users
emp1 = db.query(Employee).filter(Employee.email == 'alice@example.com').first()
if not emp1:
    db.add(Employee(email='alice@example.com', name='Alice Smith', employee_id='EMP001'))
    
emp2 = db.query(Employee).filter(Employee.email == 'bob@example.com').first()
if not emp2:
    db.add(Employee(email='bob@example.com', name='Bob Johnson', employee_id='EMP002'))

db.commit()
print('Added test users')
