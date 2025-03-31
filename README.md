# Job Finder

A Streamlit-based job aggregation and alert system that scrapes listings from major job boards and sends notifications for matching opportunities.

## Features

- **Job Search**: Search for jobs across multiple platforms (Indeed, LinkedIn) using keywords, location, and job type filters
- **Job Tracking**: Save interesting jobs and mark them as applied
- **Job Alerts**: Create custom alerts that notify you when new matching jobs are found
- **Email Notifications**: Receive email notifications for new job matches
- **PostgreSQL Database**: Persistent storage for all job listings, saved jobs, and alerts

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database

### Environment Variables

The following environment variables are used for database configuration:
- `DATABASE_URL`: Connection string for PostgreSQL
- `PGHOST`: Database host
- `PGPORT`: Database port
- `PGUSER`: Database username
- `PGPASSWORD`: Database password
- `PGDATABASE`: Database name

For email notifications:
- `EMAIL_SENDER`: Email address to send notifications from
- `EMAIL_PASSWORD`: Password for the sender email account
- `SMTP_SERVER`: SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)

### Dependencies

All required dependencies are listed in the `dependencies.txt` file.

## Usage

1. Start the application:
   ```
   streamlit run app.py --server.port 5000
   ```

2. The web interface provides several sections:
   - **Search Jobs**: Find job listings using various filters
   - **Saved Jobs**: View and manage jobs you've saved
   - **Applied Jobs**: Track jobs you've applied for
   - **Job Alerts**: Set up and manage custom job alerts

3. For job alerts to work properly, set your email address in the "Notification Settings" section.

## Files Structure

- `app.py`: Main Streamlit application
- `database.py`: Database models and operations
- `scrapers.py`: Web scraping functionality for job sites
- `notification.py`: Email notification system
- `utils.py`: Utility functions
- `.streamlit/config.toml`: Streamlit configuration

## Notes

- Web scraping is subject to the terms of service of each job board
- For email notifications to work, you need to configure the email environment variables