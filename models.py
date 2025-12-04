from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# User Model for Authentication
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False) # No hashing for dev
    name = Column(String(255), nullable=False)

# Document Model
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    request_id = Column(String(50), unique=True)  # e.g. S_12334_6740
    
    # Document Details Section
    project_no = Column(String(255))
    doc_number = Column(String(255))
    revision_number = Column(String(255))
    title = Column(String(255))
    discipline = Column(String(255))
    baseline_date = Column(String(255))
    estimation_hours = Column(Float)
    
    # Dropdowns / Logic
    is_idr_required = Column(String(255)) # Yes/No
    is_signoff_required = Column(String(255)) # Yes/No
    drm_category = Column(String(255))
    
    # People (Storing Emails)
    doc_owner = Column(String(255))
    originator = Column(String(255))
    reviewer = Column(String(255))
    signoff_eng = Column(String(255))
    idr_reviewers = Column(String(255)) # Comma-separated emails

    # Status Tracking
    current_status = Column(String(255), default="Pending")
    current_stage = Column(String(255), default="Pending (Originator Cycle 1)")
    current_stage_code = Column(Integer, default=1) # 1=Orig1, 2=Rev1, 3=Orig2, etc.
    record_status = Column(String(255), default="Active") # Active/Inactive
    
    # Relationships
    cycles = relationship("CycleData", back_populates="document", cascade="all, delete-orphan")
    idr_reviews = relationship("IDRReview", back_populates="document", cascade="all, delete-orphan")

class CycleData(Base):
    __tablename__ = 'cycle_data'
    
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('documents.id'))
    
    stage_name = Column(String(255)) # OriginatorCycle_1, ReviewerCycle_1, etc.
    
    # Originator Data
    actual_hours = Column(Float, nullable=True)
    transmittal_date = Column(String(255), nullable=True)
    ref_link = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Reviewer Data
    action = Column(String(255), nullable=True) # Accepted/SendBack
    review_hours = Column(Float, nullable=True)
    
    # Issues (Strict Integers)
    major_tool = Column(Integer, default=0)
    major_tech = Column(Integer, default=0)
    major_std = Column(Integer, default=0)
    minor_typo = Column(Integer, default=0)
    
    # SignOff Data
    signoff_decision = Column(String(255), nullable=True)
    signoff_hours = Column(Float, nullable=True)
    signoff_comments = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=datetime.now)
    
    document = relationship("Document", back_populates="cycles")

class IDRReview(Base):
    __tablename__ = 'idr_reviews'
    
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('documents.id'))
    reviewer_email = Column(String(255))
    
    review_hours = Column(Float, nullable=True)
    major_tool = Column(Integer, default=0)
    major_tech = Column(Integer, default=0)
    major_std = Column(Integer, default=0)
    minor_typo = Column(Integer, default=0)
    
    major_issues = Column(String(255), nullable=True)
    minor_issues = Column(String(255), nullable=True)

    comment_link = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    
    status = Column(String(50), default="Pending") # Pending, Submitted
    timestamp = Column(DateTime, nullable=True)
    
    document = relationship("Document", back_populates="idr_reviews")

# Project Model
class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    project_number = Column(String(255), unique=True)
    project_name = Column(String(255))
    region = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(255), nullable=True)

# Employee Model
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    system_id = Column(String(255), unique=True) # SystemID
    employee_id = Column(String(255)) # EMPID
    name = Column(String(255)) # Employee Name
    email = Column(String(255)) # Veolia Email Id
    role = Column(String(255)) # Role
    discipline = Column(String(255)) # Discipline
    department = Column(String(255)) # Sub Discipline
    reporting_manager = Column(String(255)) # ReportingManager
    employee_type = Column(String(255)) # EmployeeType
    status = Column(String(255)) # CurrentEmployeeStatus (Active/Inactive)