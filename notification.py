import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def send_job_alert_email(recipient_email, alert_name, matching_jobs):
    """
    Send an email notification for job alerts
    
    Args:
        recipient_email (str): Email address to send the notification to
        alert_name (str): Name of the job alert
        matching_jobs (list): List of job dictionaries that match the alert criteria
    
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Get email credentials from environment variables
    sender_email = os.getenv("EMAIL_SENDER", "jobfinder@example.com")
    sender_password = os.getenv("EMAIL_PASSWORD", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    # If no sender password is set, log a message instead of sending email
    if not sender_password:
        print(f"Email would be sent to {recipient_email} for alert '{alert_name}' with {len(matching_jobs)} matching jobs")
        print("Set EMAIL_PASSWORD environment variable to enable actual email sending")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Job Alert: {alert_name} - {len(matching_jobs)} new matching jobs"
        
        # Build email body
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .job-card {{ 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin-bottom: 15px; 
                    border-radius: 5px;
                }}
                .job-title {{ 
                    color: #0066CC; 
                    font-size: 18px; 
                    margin-top: 0;
                    margin-bottom: 5px;
                }}
                .company {{ 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                .apply-button {{
                    display: inline-block;
                    background-color: #28A745;
                    color: white;
                    padding: 8px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <h2>Job Alert: {alert_name}</h2>
            <p>We found {len(matching_jobs)} new jobs matching your alert criteria:</p>
        """
        
        # Add each job to the email
        for job in matching_jobs:
            posted_date = job.get('date_posted')
            if isinstance(posted_date, str):
                try:
                    posted_date = datetime.datetime.fromisoformat(posted_date)
                    date_str = posted_date.strftime('%Y-%m-%d')
                except:
                    date_str = posted_date
            elif isinstance(posted_date, datetime.datetime):
                date_str = posted_date.strftime('%Y-%m-%d')
            else:
                date_str = "Unknown"
                
            email_body += f"""
            <div class="job-card">
                <h3 class="job-title">{job.get('title', 'Unknown Title')}</h3>
                <p class="company">{job.get('company', 'Unknown Company')} - {job.get('location', 'Unknown Location')}</p>
                <p>{job.get('job_type', 'Unknown Type')} | Posted: {date_str}</p>
                <p>{job.get('description', 'No description available')[:200]}...</p>
                <a href="{job.get('url', '#')}" class="apply-button">View Job</a>
            </div>
            """
        
        email_body += """
            <p>Thank you for using Job Finder!</p>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(email_body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Email alert sent successfully to {recipient_email}")
        return True
    
    except Exception as e:
        print(f"Error sending email alert: {e}")
        return False
