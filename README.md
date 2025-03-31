# Job Finder

A Streamlit-based job aggregation and alert system that scrapes listings from major job boards and sends notifications for matching opportunities.

## Features

- **Job Search**: Scrape job listings from major job boards (Indeed, LinkedIn)
- **Filter System**: Search through collected job listings with various filters
- **Job Saving**: Save interesting job listings for later review
- **Application Tracking**: Keep track of jobs you've applied to
- **Job Alerts**: Set up custom job alerts based on keywords, location, or job type
- **Email Notifications**: Receive email alerts when new matching jobs are found

## Application Structure

- `app.py`: Main Streamlit application with UI components
- `scrapers.py`: Job scraping functionality for different job boards
- `data_manager.py`: Data persistence and management functions
- `notification.py`: Email notification system for alerts
- `utils.py`: Utility functions for formatting and text processing

## Running the Application

To run the application:

```bash
streamlit run app.py
```

## Setting Up Email Notifications

To enable email notifications, set the following environment variables:

- `EMAIL_SENDER`: Sender email address
- `EMAIL_PASSWORD`: Sender email password (or app password)
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)

## Job Sources

Currently, the app scrapes job listings from:
- Indeed
- LinkedIn

Additional sources can be added by implementing new scraper functions in `scrapers.py`.

## Color Scheme

- Primary: #0066CC (professional blue)
- Secondary: #28A745 (success green)
- Background: #F8F9FA (light grey)
- Text: #212529 (dark grey)
- Accent: #FFC107 (alert yellow)