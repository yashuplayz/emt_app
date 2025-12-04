from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from database import SessionLocal, init_db
from models import Document, CycleData, Project, Employee, User, IDRReview
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from functools import wraps

app = Flask(__name__)
app.secret_key = "veolia_secret_key" # Required for flashing messages

import logging

# Initialize DB
init_db()

def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- AUTHENTICATION ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def log_request_info():
    print(f"DEBUG: Request: {request.method} {request.url}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        email = request.form['email'].strip()
        password = request.form['password'] # This will be the Employee ID
        
        # Authenticate against Employee table directly
        # Check if employee exists with this email
        employee = db.query(Employee).filter(Employee.email == email).first()
        
        if employee:
            # Check if the provided password matches the Employee ID (as requested)
            # Note: In a real app, this is insecure, but fine for this dev stage request
            if employee.employee_id == password:
                session['user_id'] = employee.id
                session['user_email'] = employee.email
                session['user_name'] = employee.name
                return redirect(url_for('index'))
            else:
                flash("Invalid Password (Use your Employee ID).")
        else:
            flash("Employee not found with this email.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- EMAIL NOTIFICATION ---
def send_email(to_email, subject, body):
    # Placeholder for SMTP logic
    # In a real app, you would configure this with actual credentials
    try:
        # msg = MIMEText(body)
        # msg['Subject'] = subject
        # msg['From'] = "emt_tool@veolia.com"
        # msg['To'] = to_email
        
        # s = smtplib.SMTP('smtp.gmail.com', 587) # Example
        # s.starttls()
        # s.login("your_email@gmail.com", "your_password")
        # s.send_message(msg)
        # s.quit()
        print(f"--- EMAIL SIMULATION ---\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n------------------------")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- WORKFLOW LOGIC ---
STAGE_MAP = {
    "DocumentDetails": 0,
    "OriginatorCycle_1": 1,
    "ReviewerCycle_1": 2,
    "OriginatorCycle_2": 3,
    "ReviewerCycle_2": 4,
    "OriginatorCycle_3": 5,
    "ReviewerCycle_3": 6,
    "IDR_Review": 7,
    "SignOffEngineer": 8,
    "Completed": 99
}

def advance_workflow(doc, action, db):
    print(f"DEBUG: Entering advance_workflow. Current Code: {doc.current_stage_code} (Type: {type(doc.current_stage_code)}), Action: {action}")
    current_stage_code = doc.current_stage_code
    next_stage_code = current_stage_code
    next_status = doc.current_status
    next_stage_name = doc.current_stage # Default

    # --- ORIGINATOR STAGES (1, 3, 5) ---
    if current_stage_code in [1, 3, 5]:
        print("DEBUG: Processing Originator Stage")
        
        # Special Case: If IDR is Required and we are in Cycle 1, skip to IDR
        print(f"DEBUG: Checking IDR Req: {doc.is_idr_required} (Type: {type(doc.is_idr_required)})")
        if current_stage_code == 1 and (doc.is_idr_required or "").strip() == "Yes":
            print("DEBUG: IDR Condition Met! Setting next stage to 7.")
            next_stage_code = 7
            next_stage_name = "IDR_Review"
            next_status = "Pending (IDR Review)"
            # Notify IDR Reviewers
            idr_emails = (doc.idr_reviewers or "").split(',')
            # Create IDR Review records
            for email in idr_emails:
                if email.strip():
                    # Check if exists
                    existing = db.query(IDRReview).filter_by(doc_id=doc.id, reviewer_email=email.strip()).first()
                    if not existing:
                        new_review = IDRReview(doc_id=doc.id, reviewer_email=email.strip())
                        db.add(new_review)
                    send_email(email.strip(), f"IDR Required: {doc.request_id}", "IDR Review pending.")
            db.commit()
        else:
            print("DEBUG: IDR Condition NOT Met. Proceeding to Reviewer Cycle.")
            # Originator -> Reviewer (Simply +1)
            next_stage_code = current_stage_code + 1
            cycle_num = (next_stage_code // 2) # 2->1, 4->2, 6->3
            next_stage_name = f"ReviewerCycle_{cycle_num}"
            next_status = f"Pending (Reviewer Cycle {cycle_num})"
            
            # Notify Reviewer
            send_email(doc.reviewer, f"Action Required: {doc.request_id}", f"Please review document {doc.doc_number}.")

    # --- REVIEWER STAGES (2, 4, 6) ---
    elif current_stage_code in [2, 4, 6]:
        print("DEBUG: Processing Reviewer Stage")
        cycle_num = current_stage_code // 2
        
        if action == "SendBack":
            if current_stage_code == 6: # Max Cycles (Reviewer C3)
                next_status = "Rejected/Max Cycles"
                next_stage_code = 99
                next_stage_name = "Completed" # Or Rejected
                send_email(doc.originator, f"Rejected: {doc.request_id}", "Max cycles reached.")
            else:
                # Go to next Originator Cycle
                next_stage_code = current_stage_code + 1
                next_cycle_num = (next_stage_code // 2) + 1 # 3->2, 5->3
                next_stage_name = f"OriginatorCycle_{next_cycle_num}"
                next_status = f"Pending (Originator Cycle {next_cycle_num})"
                send_email(doc.originator, f"Action Required: {doc.request_id}", f"Document sent back for revision.")
                
        elif action == "Accepted":
            # Step A: Check IDR
            if doc.is_idr_required == "Yes":
                next_stage_code = 7
                next_stage_name = "IDR_Review"
                next_status = "Pending (IDR Review)"
                # Notify IDR Reviewers
                idr_emails = (doc.idr_reviewers or "").split(',')
                for email in idr_emails:
                    if email.strip():
                        # Check if exists
                        existing = db.query(IDRReview).filter_by(doc_id=doc.id, reviewer_email=email.strip()).first()
                        if not existing:
                            new_review = IDRReview(doc_id=doc.id, reviewer_email=email.strip())
                            db.add(new_review)
                        send_email(email.strip(), f"IDR Required: {doc.request_id}", "IDR Review pending.")
                db.commit()
            
            # Step B: Check SignOff
            elif doc.is_signoff_required == "Yes":
                next_stage_code = 8
                next_stage_name = "SignOffEngineer"
                next_status = "Pending (SignOff Engineer)"
                send_email(doc.signoff_eng, f"SignOff Required: {doc.request_id}", "SignOff pending.")
            
            # Step C: Completed
            else:
                next_stage_code = 99
                next_stage_name = "Completed"
                next_status = "Completed"
                send_email(doc.doc_owner, f"Completed: {doc.request_id}", "Document workflow completed.")

    # --- IDR STAGE (7) ---
    elif current_stage_code == 7:
        print("DEBUG: Processing IDR Stage")
        # Check if ALL IDR reviewers have submitted
        pending_reviews = db.query(IDRReview).filter(IDRReview.doc_id == doc.id, IDRReview.status != "Submitted").count()
        
        if pending_reviews == 0:
            print("DEBUG: All IDR Reviews Submitted. Moving to Next Stage.")
            if doc.is_signoff_required == "Yes":
                next_stage_code = 8
                next_stage_name = "SignOffEngineer"
                next_status = "Pending (SignOff Engineer)"
                send_email(doc.signoff_eng, f"SignOff Required: {doc.request_id}", "SignOff pending.")
            else:
                next_stage_code = 99
                next_stage_name = "Completed"
                next_status = "Completed"
                send_email(doc.doc_owner, f"Completed: {doc.request_id}", "Document workflow completed.")
        else:
            print(f"DEBUG: {pending_reviews} IDR Reviews still pending. Staying in Stage 7.")
            return # Do not update stage yet

    # --- SIGNOFF STAGE (8) ---
    elif current_stage_code == 8:
        print("DEBUG: Processing SignOff Stage")
        if action == "Approved":
            next_stage_code = 99
            next_stage_name = "Completed"
            next_status = "Completed"
            send_email(doc.doc_owner, f"Completed: {doc.request_id}", "Document workflow completed.")
        else: # Hold
            next_status = "Pending (SignOff Hold)"
            # Stay at 8

    print(f"DEBUG: Updating Doc to Stage Code: {next_stage_code}, Name: {next_stage_name}")
    # Update Document
    doc.current_stage = next_stage_name
    doc.current_stage_code = next_stage_code
    doc.current_status = next_status
    db.commit()



@app.route('/')
@login_required
def index():
    db = get_db()
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    
    # Filter documents where the current user is involved
    print(f"DEBUG: Current User Email: '{user_email}'")
    
    docs = db.query(Document).filter(
        Document.record_status == "Active",
        (Document.doc_owner == user_email) | 
        (Document.originator == user_email) | 
        (Document.reviewer.like(f"%{user_email}%")) | 
        (Document.idr_reviewers.like(f"%{user_email}%")) |
        (Document.signoff_eng == user_email)
    ).all()
    
    print(f"DEBUG: Found {len(docs)} documents for user {user_email}")
    for d in docs:
        print(f"DEBUG: Doc {d.request_id} - Owner: {d.doc_owner}, Orig: {d.originator}, Rev: {d.reviewer}")
    
    return render_template('dashboard.html', docs=docs, current_user=user_name)

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    db = get_db()
    if request.method == 'POST':
        req_id = f"S_{random.randint(10000,99999)}_{random.randint(1000,9999)}"
        
        doc_owner = request.form['doc_owner'].strip()
        originator = request.form['originator'].strip()
        reviewer = request.form.get('reviewer', '').strip()
        signoff_eng = request.form.get('signoff_eng', '').strip()
        is_signoff_req = request.form['signoff_req']

        is_idr_req = request.form['idr_req']
        idr_reviewers = request.form.get('idr_reviewers', '').strip()

        # Validation: SignOff Eng is optional if SignOff Req is "No"
        # Validation: IDR Reviewers is mandatory if IDR Req is "Yes"
        # Validation: Reviewer is mandatory ONLY if IDR Req is "No"
        if not all([doc_owner, originator]) or \
           (is_idr_req == "No" and not reviewer) or \
           (is_signoff_req == "Yes" and not signoff_eng) or \
           (is_idr_req == "Yes" and not idr_reviewers):
            flash("Error: Please select valid employees for all required roles.")
            projects = db.query(Project).all()
            employees = db.query(Employee).filter(Employee.status == 'Active').all()
            return render_template('document.html', mode='new', doc=None, cycles={}, current_user=session.get('user_email'), projects=projects, employees=employees)

        new_doc = Document(
            request_id=req_id,
            project_no=request.form['project_no'],
            doc_number=request.form['doc_no'],
            revision_number=request.form['rev_no'],
            title=request.form['title'],
            discipline=request.form['discipline'],
            baseline_date=request.form['baseline_date'],
            estimation_hours=float(request.form['est_hours'] or 0),
            is_idr_required=request.form['idr_req'],
            is_signoff_required=is_signoff_req,
            doc_owner=doc_owner,
            originator=originator,
            reviewer=reviewer,
            signoff_eng=signoff_eng,
            idr_reviewers=request.form.get('idr_reviewers', ''),
            drm_category=request.form['drm_cat'],
            current_stage="OriginatorCycle_1", # Initial Stage
            current_stage_code=1,
            current_status="Pending (Originator Cycle 1)"
        )
        db.add(new_doc)
        db.commit()
        
        # Send Email to Originator
        send_email(new_doc.originator, f"New Assignment: {req_id}", "You have been assigned as Originator.")
        
        return redirect(url_for('index'))
        
    projects = db.query(Project).all()
    employees = db.query(Employee).filter(Employee.status == 'Active').all()
    return render_template('document.html', mode='new', doc=None, cycles={}, current_user=session.get('user_email'), projects=projects, employees=employees)

@app.route('/doc/<int:doc_id>')
@login_required
def view_doc(doc_id):
    db = get_db()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    cycles_dict = {c.stage_name: c for c in doc.cycles}
    
    employees = db.query(Employee).filter(Employee.status == 'Active').all()
    projects = db.query(Project).all()

    idr_reviews = db.query(IDRReview).filter(IDRReview.doc_id == doc.id).all()

    if request.headers.get('HX-Request'):
        return render_template('document_modal.html', doc=doc, cycles=cycles_dict, current_user=session.get('user_email'), idr_reviews=idr_reviews)
    else:
        return render_template('document.html', mode='edit', doc=doc, cycles=cycles_dict, current_user=session.get('user_email'), employees=employees, projects=projects, idr_reviews=idr_reviews)

@app.route('/submit_cycle/<int:doc_id>/<stage>', methods=['POST'])
@login_required
def submit_cycle(doc_id, stage):
    print(f"DEBUG: submit_cycle called for Doc {doc_id}, Stage {stage}")
    print(f"DEBUG: Form Data: {request.form}")
    db = get_db()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    # Access Control Check
    user_email = session.get('user_email')
    
    # Map stage to required role email
    required_email = None
    if "Originator" in stage:
        required_email = doc.originator
    elif "Reviewer" in stage:
        required_email = doc.reviewer
    elif "SignOff" in stage:
        required_email = doc.signoff_eng
    # IDR check omitted for simplicity or needs specific logic
        
    # Strict Access Control (Uncomment to enforce)
    # if required_email and user_email != required_email:
    #     return "Unauthorized", 403

    # IDR Special Handling
    if stage == "IDR_Review":
        # Find the review for this user
        review = db.query(IDRReview).filter(
            IDRReview.doc_id == doc.id, 
            IDRReview.reviewer_email == user_email
        ).first()
        
        if review:
            review.review_hours = float(request.form.get('review_hours') or 0)
            # Legacy fields (keep as 0 or map if needed, but we use new string fields now)
            review.major_tool = int(request.form.get('major_tool') or 0)
            review.major_tech = int(request.form.get('major_tech') or 0)
            review.major_std = int(request.form.get('major_std') or 0)
            review.minor_typo = int(request.form.get('minor_typo') or 0)
            
            # New String Fields
            review.major_issues = request.form.get('major_issues')
            review.minor_issues = request.form.get('minor_issues')
            
            review.comment_link = request.form.get('comment_link')
            review.comments = request.form.get('comments')
            review.status = "Submitted"
            review.timestamp = datetime.now()
            db.commit()
            
            # Try to advance workflow
            advance_workflow(doc, "Accepted", db)
        else:
            flash("Error: You are not an assigned IDR reviewer for this document.")
            
        cycles_dict = {c.stage_name: c for c in doc.cycles}
        # Also pass idr_reviews
        idr_reviews = db.query(IDRReview).filter(IDRReview.doc_id == doc.id).all()
        return render_template('document_modal.html', doc=doc, cycles=cycles_dict, current_user=session.get('user_email'), idr_reviews=idr_reviews)

    # Save Cycle Data (For non-IDR stages)
    data = CycleData(
        doc_id=doc.id,
        stage_name=stage,
        timestamp=datetime.now(),
        actual_hours=float(request.form.get('actual_hours') or 0) if request.form.get('actual_hours') else None,
        transmittal_date=request.form.get('transmittal_date'),
        ref_link=request.form.get('ref_link'),
        description=request.form.get('description'),
        action=request.form.get('action'),
        review_hours=float(request.form.get('review_hours') or 0) if request.form.get('review_hours') else None,
        major_tool=int(request.form.get('major_tool') or 0),
        major_tech=int(request.form.get('major_tech') or 0),
        major_std=int(request.form.get('major_std') or 0),
        minor_typo=int(request.form.get('minor_typo') or 0),
        signoff_decision=request.form.get('signoff_decision'),
        signoff_hours=float(request.form.get('signoff_hours') or 0) if request.form.get('signoff_hours') else None,
        signoff_comments=request.form.get('signoff_comments')
    )
    db.add(data)
    
    # Advance Workflow
    action = request.form.get('action') or request.form.get('signoff_decision')
    advance_workflow(doc, action, db)
    
    db.commit()
    
    cycles_dict = {c.stage_name: c for c in doc.cycles}
    idr_reviews = db.query(IDRReview).filter(IDRReview.doc_id == doc.id).all()
    return render_template('document_modal.html', doc=doc, cycles=cycles_dict, current_user=session.get('user_email'), idr_reviews=idr_reviews)

@app.route('/delete/<int:doc_id>')
@login_required
def soft_delete(doc_id):
    db = get_db()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    doc.record_status = "Inactive"
    db.commit()
    flash("Document marked as Inactive")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
