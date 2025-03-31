import pandas as pd
import os
import datetime
import json

# Paths for persisting data
JOBS_DATA_PATH = "jobs_data.json"
SAVED_JOBS_PATH = "saved_jobs.json"
APPLIED_JOBS_PATH = "applied_jobs.json"
ALERTS_PATH = "job_alerts.json"

def load_jobs():
    """
    Load the current job listings from storage
    
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    if os.path.exists(JOBS_DATA_PATH):
        try:
            # Read the JSON file
            with open(JOBS_DATA_PATH, 'r') as f:
                jobs_data = json.load(f)
            
            # Convert to DataFrame
            df = pd.DataFrame(jobs_data)
            
            # Convert date strings back to datetime
            if not df.empty and 'date_posted' in df.columns:
                df['date_posted'] = pd.to_datetime(df['date_posted'])
            
            return df
        except Exception as e:
            print(f"Error loading jobs data: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_jobs(jobs_df):
    """
    Save job listings to storage
    
    Args:
        jobs_df (pandas.DataFrame): DataFrame containing job listings
    """
    try:
        # Convert DataFrame to list of dictionaries
        jobs_data = jobs_df.to_dict('records')
        
        # Convert datetime objects to strings
        for job in jobs_data:
            if 'date_posted' in job and isinstance(job['date_posted'], datetime.datetime):
                job['date_posted'] = job['date_posted'].isoformat()
        
        # Write to JSON file
        with open(JOBS_DATA_PATH, 'w') as f:
            json.dump(jobs_data, f)
    except Exception as e:
        print(f"Error saving jobs data: {e}")

def load_saved_jobs():
    """
    Load saved jobs from storage
    
    Returns:
        pandas.DataFrame: DataFrame containing saved jobs
    """
    if os.path.exists(SAVED_JOBS_PATH):
        try:
            # Read the JSON file
            with open(SAVED_JOBS_PATH, 'r') as f:
                saved_jobs_data = json.load(f)
            
            # Convert to DataFrame
            df = pd.DataFrame(saved_jobs_data)
            
            # Convert date strings back to datetime
            if not df.empty:
                if 'date_posted' in df.columns:
                    df['date_posted'] = pd.to_datetime(df['date_posted'])
                if 'saved_date' in df.columns:
                    df['saved_date'] = pd.to_datetime(df['saved_date'])
            
            return df
        except Exception as e:
            print(f"Error loading saved jobs: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_job_to_saved(job):
    """
    Save a job to the saved jobs list
    
    Args:
        job (pandas.Series or dict): Job to save
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    # Add saved date
    job['saved_date'] = datetime.datetime.now().isoformat()
    
    # Convert datetime to string for JSON serialization
    if 'date_posted' in job and isinstance(job['date_posted'], datetime.datetime):
        job['date_posted'] = job['date_posted'].isoformat()
    
    # Load existing saved jobs
    saved_jobs = []
    if os.path.exists(SAVED_JOBS_PATH):
        try:
            with open(SAVED_JOBS_PATH, 'r') as f:
                saved_jobs = json.load(f)
        except:
            saved_jobs = []
    
    # Check if job is already saved (by URL)
    job_urls = [j.get('url') for j in saved_jobs]
    if job.get('url') not in job_urls:
        saved_jobs.append(job)
        
        # Save to file
        with open(SAVED_JOBS_PATH, 'w') as f:
            json.dump(saved_jobs, f)
        
        # Update session state if it exists
        import streamlit as st
        if 'saved_jobs' in st.session_state:
            st.session_state.saved_jobs = load_saved_jobs()

def remove_job_from_saved(job):
    """
    Remove a job from the saved jobs list
    
    Args:
        job (pandas.Series or dict): Job to remove
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    # Load existing saved jobs
    saved_jobs = []
    if os.path.exists(SAVED_JOBS_PATH):
        try:
            with open(SAVED_JOBS_PATH, 'r') as f:
                saved_jobs = json.load(f)
        except:
            saved_jobs = []
    
    # Remove job by URL
    saved_jobs = [j for j in saved_jobs if j.get('url') != job.get('url')]
    
    # Save to file
    with open(SAVED_JOBS_PATH, 'w') as f:
        json.dump(saved_jobs, f)
    
    # Update session state if it exists
    import streamlit as st
    if 'saved_jobs' in st.session_state:
        st.session_state.saved_jobs = load_saved_jobs()

def load_applied_jobs():
    """
    Load applied jobs from storage
    
    Returns:
        pandas.DataFrame: DataFrame containing applied jobs
    """
    if os.path.exists(APPLIED_JOBS_PATH):
        try:
            # Read the JSON file
            with open(APPLIED_JOBS_PATH, 'r') as f:
                applied_jobs_data = json.load(f)
            
            # Convert to DataFrame
            df = pd.DataFrame(applied_jobs_data)
            
            # Convert date strings back to datetime
            if not df.empty:
                if 'date_posted' in df.columns:
                    df['date_posted'] = pd.to_datetime(df['date_posted'])
                if 'applied_date' in df.columns:
                    df['applied_date'] = pd.to_datetime(df['applied_date'])
            
            return df
        except Exception as e:
            print(f"Error loading applied jobs: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def add_job_to_applied(job):
    """
    Add a job to the applied jobs list
    
    Args:
        job (pandas.Series or dict): Job to add to applied list
    """
    # Convert job to dictionary if it's a Series
    if isinstance(job, pd.Series):
        job = job.to_dict()
    
    # Add applied date
    job['applied_date'] = datetime.datetime.now().isoformat()
    
    # Convert datetime to string for JSON serialization
    if 'date_posted' in job and isinstance(job['date_posted'], datetime.datetime):
        job['date_posted'] = job['date_posted'].isoformat()
    
    # Load existing applied jobs
    applied_jobs = []
    if os.path.exists(APPLIED_JOBS_PATH):
        try:
            with open(APPLIED_JOBS_PATH, 'r') as f:
                applied_jobs = json.load(f)
        except:
            applied_jobs = []
    
    # Check if job is already in applied list (by URL)
    job_urls = [j.get('url') for j in applied_jobs]
    if job.get('url') not in job_urls:
        applied_jobs.append(job)
        
        # Save to file
        with open(APPLIED_JOBS_PATH, 'w') as f:
            json.dump(applied_jobs, f)
        
        # Update session state if it exists
        import streamlit as st
        if 'applied_jobs' in st.session_state:
            st.session_state.applied_jobs = load_applied_jobs()

def load_alerts():
    """
    Load job alerts from storage
    
    Returns:
        list: List of job alert dictionaries
    """
    if os.path.exists(ALERTS_PATH):
        try:
            # Read the JSON file
            with open(ALERTS_PATH, 'r') as f:
                alerts_data = json.load(f)
            
            # Convert date strings back to datetime
            for alert in alerts_data:
                if 'created_date' in alert:
                    alert['created_date'] = datetime.datetime.fromisoformat(alert['created_date'])
            
            return alerts_data
        except Exception as e:
            print(f"Error loading job alerts: {e}")
            return []
    else:
        return []

def save_alert(alert):
    """
    Save a job alert
    
    Args:
        alert (dict): Job alert to save
    """
    # Load existing alerts
    alerts = load_alerts()
    
    # Convert datetime to string for JSON serialization
    alert_to_save = alert.copy()
    if 'created_date' in alert_to_save and isinstance(alert_to_save['created_date'], datetime.datetime):
        alert_to_save['created_date'] = alert_to_save['created_date'].isoformat()
    
    # Add alert
    alerts.append(alert_to_save)
    
    # Save to file
    with open(ALERTS_PATH, 'w') as f:
        json.dump(alerts, f)
    
    # Update session state if it exists
    import streamlit as st
    if 'alerts' in st.session_state:
        st.session_state.alerts = load_alerts()

def delete_alert(alert_id):
    """
    Delete a job alert by ID
    
    Args:
        alert_id (str): ID of the alert to delete
    """
    # Load existing alerts
    alerts = load_alerts()
    
    # Remove alert by ID
    alerts = [a for a in alerts if a.get('id') != alert_id]
    
    # Convert datetime to string for JSON serialization
    for alert in alerts:
        if 'created_date' in alert and isinstance(alert['created_date'], datetime.datetime):
            alert['created_date'] = alert['created_date'].isoformat()
    
    # Save to file
    with open(ALERTS_PATH, 'w') as f:
        json.dump(alerts, f)
    
    # Update session state if it exists
    import streamlit as st
    if 'alerts' in st.session_state:
        st.session_state.alerts = load_alerts()
