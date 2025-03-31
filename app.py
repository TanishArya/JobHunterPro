import streamlit as st
import pandas as pd
import datetime
from scrapers import scrape_indeed, scrape_linkedin
from data_manager import (
    load_jobs, save_jobs, load_saved_jobs, save_job_to_saved,
    remove_job_from_saved, load_applied_jobs, add_job_to_applied,
    load_alerts, save_alert, delete_alert
)
from notification import send_job_alert_email
import schedule
import time
import threading
import uuid

# Page configuration
st.set_page_config(
    page_title="Job Finder",
    page_icon="🔍",
    layout="wide",
)

# Initialize session state variables if they don't exist
if 'jobs_df' not in st.session_state:
    st.session_state.jobs_df = load_jobs()
if 'saved_jobs' not in st.session_state:
    st.session_state.saved_jobs = load_saved_jobs()
if 'applied_jobs' not in st.session_state:
    st.session_state.applied_jobs = load_applied_jobs()
if 'alerts' not in st.session_state:
    st.session_state.alerts = load_alerts()
if 'show_saved' not in st.session_state:
    st.session_state.show_saved = False
if 'show_applied' not in st.session_state:
    st.session_state.show_applied = False
if 'show_alerts' not in st.session_state:
    st.session_state.show_alerts = False
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'email_address' not in st.session_state:
    st.session_state.email_address = ""

# Function to run scheduled tasks
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Define job alert checker
def check_job_alerts():
    alerts = load_alerts()
    current_jobs = load_jobs()
    
    if current_jobs.empty or len(alerts) == 0:
        return
        
    for alert in alerts:
        matching_jobs = []
        for index, job in current_jobs.iterrows():
            keywords_match = all(kw.lower() in job['title'].lower() or kw.lower() in job['description'].lower() 
                               for kw in alert['keywords'])
            location_match = True if not alert['location'] else alert['location'].lower() in job['location'].lower()
            job_type_match = True if not alert['job_type'] else alert['job_type'].lower() in job['job_type'].lower()
            
            if keywords_match and location_match and job_type_match and job['date_posted'] >= alert['created_date']:
                matching_jobs.append(job.to_dict())
        
        if matching_jobs and alert['email']:
            send_job_alert_email(alert['email'], alert['name'], matching_jobs)

# Schedule alert checking to run every hour
schedule.every(1).hours.do(check_job_alerts)

# Start scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
scheduler_thread.start()

# Sidebar for search filters and navigation
with st.sidebar:
    st.title("Job Finder 🔍")
    
    # Navigation
    st.subheader("Navigation")
    if st.button("Search Jobs", use_container_width=True):
        st.session_state.show_saved = False
        st.session_state.show_applied = False
        st.session_state.show_alerts = False
        st.rerun()
    
    if st.button("Saved Jobs", use_container_width=True):
        st.session_state.show_saved = True
        st.session_state.show_applied = False
        st.session_state.show_alerts = False
        st.rerun()
    
    if st.button("Applied Jobs", use_container_width=True):
        st.session_state.show_saved = False
        st.session_state.show_applied = True
        st.session_state.show_alerts = False
        st.rerun()
    
    if st.button("Job Alerts", use_container_width=True):
        st.session_state.show_saved = False
        st.session_state.show_applied = False
        st.session_state.show_alerts = True
        st.rerun()
    
    # Search filters (only show in search mode)
    if not st.session_state.show_saved and not st.session_state.show_applied and not st.session_state.show_alerts:
        st.subheader("Search Filters")
        
        keywords = st.text_input("Keywords (separate with commas)")
        location = st.text_input("Location")
        
        job_type_options = ['Any', 'Full-time', 'Part-time', 'Contract', 'Remote']
        job_type = st.selectbox("Job Type", job_type_options)
        
        date_posted_options = ['Any time', 'Past 24 hours', 'Past week', 'Past month']
        date_posted = st.selectbox("Date Posted", date_posted_options)
        
        source_options = ['All', 'Indeed', 'LinkedIn']
        source = st.selectbox("Source", source_options)
        
        if st.button("Search", type="primary", use_container_width=True):
            # Clear previous search results
            st.session_state.search_performed = True
            
            # Convert keywords to list
            keyword_list = [k.strip() for k in keywords.split(',')] if keywords else []
            
            # Execute the scraping based on selected source
            if source == 'All' or source == 'Indeed':
                indeed_jobs = scrape_indeed(keyword_list, location, job_type if job_type != 'Any' else None)
            else:
                indeed_jobs = pd.DataFrame()
                
            if source == 'All' or source == 'LinkedIn':
                linkedin_jobs = scrape_linkedin(keyword_list, location, job_type if job_type != 'Any' else None)
            else:
                linkedin_jobs = pd.DataFrame()
            
            # Combine results
            combined_jobs = pd.concat([indeed_jobs, linkedin_jobs], ignore_index=True)
            
            # Filter by date if selected
            if date_posted != 'Any time' and not combined_jobs.empty:
                today = datetime.datetime.now()
                if date_posted == 'Past 24 hours':
                    cutoff_date = today - datetime.timedelta(days=1)
                elif date_posted == 'Past week':
                    cutoff_date = today - datetime.timedelta(days=7)
                elif date_posted == 'Past month':
                    cutoff_date = today - datetime.timedelta(days=30)
                
                combined_jobs = combined_jobs[combined_jobs['date_posted'] >= cutoff_date]
            
            # Update the session state with the new jobs
            st.session_state.jobs_df = combined_jobs
            
            # Save to persistent storage
            save_jobs(combined_jobs)
            
            st.rerun()
    
    # Email for alerts
    st.subheader("Notification Settings")
    st.session_state.email_address = st.text_input("Your email address for job alerts", st.session_state.email_address)

# Main content area
if st.session_state.show_saved:
    # Saved Jobs View
    st.title("Saved Jobs")
    
    if st.session_state.saved_jobs.empty:
        st.info("You haven't saved any jobs yet. Search for jobs and save them to see them here.")
    else:
        for index, job in st.session_state.saved_jobs.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.subheader(job['title'])
                    st.write(f"**{job['company']}** - {job['location']}")
                    st.write(f"**{job['job_type']}** | Posted: {job['date_posted'].strftime('%Y-%m-%d')}")
                    
                    with st.expander("Job Description"):
                        st.write(job['description'])
                    
                    st.write(f"[Apply Here]({job['url']})")
                
                with col2:
                    if st.button("Remove", key=f"remove_{index}"):
                        remove_job_from_saved(job)
                        st.rerun()
                    
                    if st.button("Mark Applied", key=f"apply_{index}"):
                        add_job_to_applied(job)
                        remove_job_from_saved(job)
                        st.rerun()
                
                st.divider()

elif st.session_state.show_applied:
    # Applied Jobs View
    st.title("Applied Jobs")
    
    if st.session_state.applied_jobs.empty:
        st.info("You haven't marked any jobs as applied yet.")
    else:
        for index, job in st.session_state.applied_jobs.iterrows():
            with st.container():
                st.subheader(job['title'])
                st.write(f"**{job['company']}** - {job['location']}")
                st.write(f"**{job['job_type']}** | Applied on: {job['applied_date'].strftime('%Y-%m-%d')}")
                
                with st.expander("Job Description"):
                    st.write(job['description'])
                
                st.write(f"[Job Link]({job['url']})")
                st.divider()

elif st.session_state.show_alerts:
    # Job Alerts View
    st.title("Job Alerts")
    
    # Form to create a new alert
    with st.form("new_alert_form"):
        st.subheader("Create New Alert")
        
        alert_name = st.text_input("Alert Name")
        alert_keywords = st.text_input("Keywords (separate with commas)")
        alert_location = st.text_input("Location (optional)")
        
        job_type_options = ['Any', 'Full-time', 'Part-time', 'Contract', 'Remote']
        alert_job_type = st.selectbox("Job Type", job_type_options)
        
        alert_email = st.text_input("Email for notifications", st.session_state.email_address)
        
        submit_button = st.form_submit_button("Create Alert")
        
        if submit_button:
            if not alert_name or not alert_keywords:
                st.error("Alert name and keywords are required.")
            elif not alert_email:
                st.error("Email address is required for notifications.")
            else:
                # Create new alert
                new_alert = {
                    'id': str(uuid.uuid4()),
                    'name': alert_name,
                    'keywords': [k.strip() for k in alert_keywords.split(',')],
                    'location': alert_location,
                    'job_type': None if alert_job_type == 'Any' else alert_job_type,
                    'email': alert_email,
                    'created_date': datetime.datetime.now()
                }
                
                # Save the alert
                save_alert(new_alert)
                st.success("Alert created successfully!")
                st.rerun()
    
    # Display existing alerts
    st.subheader("Your Alerts")
    
    if len(st.session_state.alerts) == 0:
        st.info("You don't have any job alerts set up yet.")
    else:
        for i, alert in enumerate(st.session_state.alerts):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{alert['name']}**")
                    st.write(f"Keywords: {', '.join(alert['keywords'])}")
                    if alert['location']:
                        st.write(f"Location: {alert['location']}")
                    if alert['job_type']:
                        st.write(f"Job Type: {alert['job_type']}")
                    st.write(f"Email: {alert['email']}")
                    st.write(f"Created: {alert['created_date'].strftime('%Y-%m-%d')}")
                
                with col2:
                    if st.button("Delete", key=f"delete_alert_{i}"):
                        delete_alert(alert['id'])
                        st.rerun()
                
                st.divider()

else:
    # Default search results view
    st.title("Job Listings")
    
    if st.session_state.search_performed and st.session_state.jobs_df.empty:
        st.info("No jobs found matching your search criteria. Try adjusting your filters.")
    elif not st.session_state.search_performed:
        st.info("Use the search filters on the left to find job opportunities.")
    else:
        # Display job results
        st.write(f"Found {len(st.session_state.jobs_df)} jobs matching your criteria")
        
        for index, job in st.session_state.jobs_df.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.subheader(job['title'])
                    st.write(f"**{job['company']}** - {job['location']}")
                    st.write(f"**{job['job_type']}** | Posted: {job['date_posted'].strftime('%Y-%m-%d')}")
                    st.write(f"Source: {job['source']}")
                    
                    with st.expander("Job Description"):
                        st.write(job['description'])
                    
                    st.write(f"[Apply Here]({job['url']})")
                
                with col2:
                    if st.button("Save", key=f"save_{index}"):
                        save_job_to_saved(job)
                        st.success("Job saved!")
                        
                    if st.button("Apply", key=f"apply_search_{index}"):
                        add_job_to_applied(job)
                        st.success("Job marked as applied!")
                
                st.divider()
