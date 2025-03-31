# Job Finder - Career Opportunity Aggregator

A Streamlit-based job aggregation and alert system that scrapes listings from major job boards and sends notifications for matching opportunities.

## Features

- **Job Scraping**: Automatically collects job listings from major job boards (Indeed, LinkedIn)
- **Search & Filter**: Find relevant opportunities using keywords, location, job type, and date filters
- **Job Tracking**: Save interesting positions and track your job applications
- **Custom Alerts**: Set up personalized job alerts with email notifications for new matching opportunities
- **PostgreSQL Database**: Persistent storage of jobs, saved positions, and alerts

## Tech Stack

- **Frontend/Backend**: Streamlit
- **Database**: PostgreSQL
- **Web Scraping**: BeautifulSoup4, Trafilatura, Requests
- **Data Processing**: Pandas
- **Background Tasks**: Schedule

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r dependencies.txt
   ```
3. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `EMAIL_SENDER`: Email address to send notifications from
   - `EMAIL_PASSWORD`: Password for the sender email
   - `SMTP_SERVER`: SMTP server address (default: smtp.gmail.com)
   - `SMTP_PORT`: SMTP server port (default: 587)

### Running the Application

```
streamlit run app.py
```

## Project Structure

- **app.py**: Main Streamlit application
- **database.py**: Database models and data access functions
- **scrapers.py**: Web scraping functionality for various job boards
- **notification.py**: Email notification system
- **utils.py**: Utility functions for data processing and formatting

## Usage Guide

1. **Search for Jobs**:
   - Enter keywords, location, and other filters
   - Click "Search" to find matching opportunities

2. **Save Interesting Jobs**:
   - Click "Save" on any job listing to add it to your saved jobs
   - View saved jobs in the "Saved Jobs" section

3. **Track Applications**:
   - Click "Apply" to mark a job as applied
   - View all your applications in the "Applied Jobs" section

4. **Create Job Alerts**:
   - Navigate to "Job Alerts"
   - Fill in alert criteria and your email address
   - Receive notifications for new matching jobs

## License

MIT