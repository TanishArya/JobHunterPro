import os
import pandas as pd
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define database models
class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(512), unique=True)
    job_type = Column(String(50))
    date_posted = Column(DateTime, default=datetime.datetime.now)
    source = Column(String(50))
    
    saved_job = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")
    applied_job = relationship("AppliedJob", back_populates="job", cascade="all, delete-orphan")

class SavedJob(Base):
    __tablename__ = 'saved_jobs'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    saved_date = Column(DateTime, default=datetime.datetime.now)
    notes = Column(Text)
    
    job = relationship("Job", back_populates="saved_job")

class AppliedJob(Base):
    __tablename__ = 'applied_jobs'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    applied_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String(50), default="Applied")
    notes = Column(Text)
    
    job = relationship("Job", back_populates="applied_job")

class JobAlert(Base):
    __tablename__ = 'job_alerts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    keywords = Column(JSON)
    location = Column(String(255))
    job_type = Column(String(50))
    email = Column(String(255))
    created_date = Column(DateTime, default=datetime.datetime.now)
    last_notified = Column(DateTime)
    alert_id = Column(String(50), unique=True)
    
# Create all tables in the database
Base.metadata.create_all(engine)

# Helper functions for interacting with the database
def load_jobs():
    """
    Load the current job listings from database
    
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    try:
        session = Session()
        jobs = session.query(Job).all()
        
        if not jobs:
            return pd.DataFrame()
        
        # Convert to DataFrame
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'url': job.url,
                'job_type': job.job_type,
                'date_posted': job.date_posted,
                'source': job.source
            })
        
        return pd.DataFrame(jobs_data)
    except Exception as e:
        print(f"Error loading jobs from database: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def save_jobs(jobs_df):
    """
    Save job listings to database
    
    Args:
        jobs_df (pandas.DataFrame): DataFrame containing job listings
    """
    if jobs_df.empty:
        return
    
    try:
        session = Session()
        
        for _, job_data in jobs_df.iterrows():
            # Check if job already exists (by URL)
            existing_job = session.query(Job).filter_by(url=job_data['url']).first()
            
            if existing_job:
                # Update existing job
                existing_job.title = job_data['title']
                existing_job.company = job_data['company']
                existing_job.location = job_data['location']
                existing_job.description = job_data['description']
                existing_job.job_type = job_data['job_type']
                existing_job.source = job_data['source']
            else:
                # Create new job
                new_job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'],
                    url=job_data['url'],
                    job_type=job_data['job_type'],
                    date_posted=job_data['date_posted'],
                    source=job_data['source']
                )
                session.add(new_job)
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving jobs to database: {e}")
    finally:
        session.close()

def load_saved_jobs():
    """
    Load saved jobs from database
    
    Returns:
        pandas.DataFrame: DataFrame containing saved jobs
    """
    try:
        session = Session()
        # Join SavedJob and Job tables to get full job information
        saved_jobs = session.query(SavedJob, Job).join(Job).all()
        
        if not saved_jobs:
            return pd.DataFrame()
        
        # Convert to DataFrame
        saved_jobs_data = []
        for saved_job, job in saved_jobs:
            saved_jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'url': job.url,
                'job_type': job.job_type,
                'date_posted': job.date_posted,
                'source': job.source,
                'saved_date': saved_job.saved_date,
                'notes': saved_job.notes
            })
        
        return pd.DataFrame(saved_jobs_data)
    except Exception as e:
        print(f"Error loading saved jobs from database: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def save_job_to_saved(job):
    """
    Save a job to the saved jobs list
    
    Args:
        job (pandas.Series or dict): Job to save
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    try:
        session = Session()
        
        # First, check if the job exists in the jobs table
        job_record = session.query(Job).filter_by(url=job.get('url')).first()
        
        if not job_record:
            # Job doesn't exist, create it first
            job_record = Job(
                title=job.get('title'),
                company=job.get('company'),
                location=job.get('location'),
                description=job.get('description'),
                url=job.get('url'),
                job_type=job.get('job_type'),
                date_posted=job.get('date_posted') if isinstance(job.get('date_posted'), datetime.datetime) 
                         else datetime.datetime.now(),
                source=job.get('source')
            )
            session.add(job_record)
            session.flush()  # Generate ID for the new job
        
        # Check if job is already in saved jobs
        existing_saved = session.query(SavedJob).filter_by(job_id=job_record.id).first()
        
        if not existing_saved:
            # Add to saved jobs
            saved_job = SavedJob(
                job_id=job_record.id,
                saved_date=datetime.datetime.now(),
                notes=job.get('notes', '')
            )
            session.add(saved_job)
        
        session.commit()
        
        # Update session state if it exists
        import streamlit as st
        if 'saved_jobs' in st.session_state:
            st.session_state.saved_jobs = load_saved_jobs()
            
    except Exception as e:
        session.rollback()
        print(f"Error saving job to saved jobs: {e}")
    finally:
        session.close()

def remove_job_from_saved(job):
    """
    Remove a job from the saved jobs list
    
    Args:
        job (pandas.Series or dict): Job to remove
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    try:
        session = Session()
        
        # Find the job record
        job_record = session.query(Job).filter_by(url=job.get('url')).first()
        
        if job_record:
            # Find and delete the saved job record
            saved_job = session.query(SavedJob).filter_by(job_id=job_record.id).first()
            
            if saved_job:
                session.delete(saved_job)
                session.commit()
        
        # Update session state if it exists
        import streamlit as st
        if 'saved_jobs' in st.session_state:
            st.session_state.saved_jobs = load_saved_jobs()
            
    except Exception as e:
        session.rollback()
        print(f"Error removing job from saved jobs: {e}")
    finally:
        session.close()

def load_applied_jobs():
    """
    Load applied jobs from database
    
    Returns:
        pandas.DataFrame: DataFrame containing applied jobs
    """
    try:
        session = Session()
        # Join AppliedJob and Job tables to get full job information
        applied_jobs = session.query(AppliedJob, Job).join(Job).all()
        
        if not applied_jobs:
            return pd.DataFrame()
        
        # Convert to DataFrame
        applied_jobs_data = []
        for applied_job, job in applied_jobs:
            applied_jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'url': job.url,
                'job_type': job.job_type,
                'date_posted': job.date_posted,
                'source': job.source,
                'applied_date': applied_job.applied_date,
                'status': applied_job.status,
                'notes': applied_job.notes
            })
        
        return pd.DataFrame(applied_jobs_data)
    except Exception as e:
        print(f"Error loading applied jobs from database: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def add_job_to_applied(job):
    """
    Add a job to the applied jobs list
    
    Args:
        job (pandas.Series or dict): Job to add to applied list
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    try:
        session = Session()
        
        # First, check if the job exists in the jobs table
        job_record = session.query(Job).filter_by(url=job.get('url')).first()
        
        if not job_record:
            # Job doesn't exist, create it first
            job_record = Job(
                title=job.get('title'),
                company=job.get('company'),
                location=job.get('location'),
                description=job.get('description'),
                url=job.get('url'),
                job_type=job.get('job_type'),
                date_posted=job.get('date_posted') if isinstance(job.get('date_posted'), datetime.datetime) 
                         else datetime.datetime.now(),
                source=job.get('source')
            )
            session.add(job_record)
            session.flush()  # Generate ID for the new job
        
        # Check if job is already in applied jobs
        existing_applied = session.query(AppliedJob).filter_by(job_id=job_record.id).first()
        
        if not existing_applied:
            # Add to applied jobs
            applied_job = AppliedJob(
                job_id=job_record.id,
                applied_date=datetime.datetime.now(),
                status="Applied",
                notes=job.get('notes', '')
            )
            session.add(applied_job)
        
        session.commit()
        
        # Update session state if it exists
        import streamlit as st
        if 'applied_jobs' in st.session_state:
            st.session_state.applied_jobs = load_applied_jobs()
            
    except Exception as e:
        session.rollback()
        print(f"Error adding job to applied jobs: {e}")
    finally:
        session.close()

def load_alerts():
    """
    Load job alerts from database
    
    Returns:
        list: List of job alert dictionaries
    """
    try:
        session = Session()
        alerts = session.query(JobAlert).all()
        
        if not alerts:
            return []
        
        # Convert to list of dictionaries
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.alert_id,
                'name': alert.name,
                'keywords': alert.keywords,
                'location': alert.location,
                'job_type': alert.job_type,
                'email': alert.email,
                'created_date': alert.created_date,
                'last_notified': alert.last_notified
            })
        
        return alerts_data
    except Exception as e:
        print(f"Error loading job alerts from database: {e}")
        return []
    finally:
        session.close()

def save_alert(alert):
    """
    Save a job alert
    
    Args:
        alert (dict): Job alert to save
    """
    try:
        session = Session()
        
        # Check if alert already exists by alert_id
        existing_alert = session.query(JobAlert).filter_by(alert_id=alert.get('id')).first()
        
        if existing_alert:
            # Update existing alert
            existing_alert.name = alert.get('name')
            existing_alert.keywords = alert.get('keywords')
            existing_alert.location = alert.get('location')
            existing_alert.job_type = alert.get('job_type')
            existing_alert.email = alert.get('email')
        else:
            # Create new alert
            new_alert = JobAlert(
                name=alert.get('name'),
                keywords=alert.get('keywords'),
                location=alert.get('location'),
                job_type=alert.get('job_type'),
                email=alert.get('email'),
                created_date=alert.get('created_date') if isinstance(alert.get('created_date'), datetime.datetime) 
                           else datetime.datetime.now(),
                alert_id=alert.get('id')
            )
            session.add(new_alert)
        
        session.commit()
        
        # Update session state if it exists
        import streamlit as st
        if 'alerts' in st.session_state:
            st.session_state.alerts = load_alerts()
            
    except Exception as e:
        session.rollback()
        print(f"Error saving job alert: {e}")
    finally:
        session.close()

def delete_alert(alert_id):
    """
    Delete a job alert by ID
    
    Args:
        alert_id (str): ID of the alert to delete
    """
    try:
        session = Session()
        
        # Find and delete the alert
        alert = session.query(JobAlert).filter_by(alert_id=alert_id).first()
        
        if alert:
            session.delete(alert)
            session.commit()
        
        # Update session state if it exists
        import streamlit as st
        if 'alerts' in st.session_state:
            st.session_state.alerts = load_alerts()
            
    except Exception as e:
        session.rollback()
        print(f"Error deleting job alert: {e}")
    finally:
        session.close()

def update_alert_notification(alert_id):
    """
    Update the last notification timestamp for an alert
    
    Args:
        alert_id (str): ID of the alert
    """
    try:
        session = Session()
        
        # Find the alert
        alert = session.query(JobAlert).filter_by(alert_id=alert_id).first()
        
        if alert:
            alert.last_notified = datetime.datetime.now()
            session.commit()
            
    except Exception as e:
        session.rollback()
        print(f"Error updating alert notification timestamp: {e}")
    finally:
        session.close()