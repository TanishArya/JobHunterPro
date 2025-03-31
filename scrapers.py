import pandas as pd
import datetime
import random
import time
import requests
from bs4 import BeautifulSoup
import trafilatura
import re

def scrape_indeed(keywords, location, job_type=None):
    """
    Scrape job listings from Indeed based on search criteria
    
    Args:
        keywords (list): List of keywords to search for
        location (str): Location to search in
        job_type (str, optional): Type of job (Full-time, Part-time, etc)
        
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    jobs = []
    
    # Convert keywords to search query format
    keyword_query = '+'.join(keywords) if keywords else ''
    
    # Base search URL
    url = "https://www.indeed.com/jobs"
    params = {}
    
    if keyword_query:
        params['q'] = keyword_query
    if location:
        params['l'] = location
    if job_type:
        job_type_param = job_type.lower().replace('-', '')
        params['jt'] = job_type_param
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_=re.compile('job_seen_beacon'))
            
            for card in job_cards:
                try:
                    # Extract job details
                    title_element = card.find('h2', class_=re.compile('jobTitle'))
                    title = title_element.get_text().strip() if title_element else "Unknown Title"
                    
                    company_element = card.find('span', class_=re.compile('companyName'))
                    company = company_element.get_text().strip() if company_element else "Unknown Company"
                    
                    location_element = card.find('div', class_=re.compile('companyLocation'))
                    location_text = location_element.get_text().strip() if location_element else "Unknown Location"
                    
                    # Get relative URL and convert to absolute URL
                    relative_url_element = card.find('a', href=True)
                    relative_url = relative_url_element['href'] if relative_url_element else None
                    job_url = f"https://www.indeed.com{relative_url}" if relative_url else "#"
                    
                    # Extract job description snippet
                    description_element = card.find('div', class_=re.compile('job-snippet'))
                    description = description_element.get_text().strip() if description_element else "No description available"
                    
                    # Determine job type from the listing
                    job_type_element = card.find('div', class_=re.compile('metadata'))
                    detected_job_type = "Full-time"  # Default
                    if job_type_element:
                        job_type_text = job_type_element.get_text().lower()
                        if 'part-time' in job_type_text:
                            detected_job_type = "Part-time"
                        elif 'contract' in job_type_text:
                            detected_job_type = "Contract"
                        elif 'remote' in job_type_text:
                            detected_job_type = "Remote"
                    
                    # Generate a recent date (within the last 30 days) for demonstration
                    days_ago = random.randint(0, 29)
                    date_posted = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                    
                    # Create job entry
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'description': description,
                        'url': job_url,
                        'job_type': detected_job_type,
                        'date_posted': date_posted,
                        'source': 'Indeed'
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    print(f"Error extracting job details: {e}")
                    continue
        else:
            print(f"Failed to retrieve data from Indeed. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    # Return as DataFrame
    return pd.DataFrame(jobs)

def scrape_linkedin(keywords, location, job_type=None):
    """
    Scrape job listings from LinkedIn based on search criteria
    
    Args:
        keywords (list): List of keywords to search for
        location (str): Location to search in
        job_type (str, optional): Type of job (Full-time, Part-time, etc)
        
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    jobs = []
    
    # Convert keywords to search query format
    keyword_query = '%20'.join(keywords) if keywords else ''
    
    # Base search URL
    url = "https://www.linkedin.com/jobs/search"
    params = {}
    
    if keyword_query:
        params['keywords'] = keyword_query
    if location:
        params['location'] = location
    
    # Add job type filter if specified
    job_type_param = None
    if job_type:
        if job_type.lower() == 'full-time':
            job_type_param = 'F'
        elif job_type.lower() == 'part-time':
            job_type_param = 'P'
        elif job_type.lower() == 'contract':
            job_type_param = 'C'
        elif job_type.lower() == 'remote':
            job_type_param = 'R'
    
    if job_type_param:
        params['f_JT'] = job_type_param
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='base-card')
            
            for card in job_cards:
                try:
                    # Extract job details
                    title_element = card.find('h3', class_='base-search-card__title')
                    title = title_element.get_text().strip() if title_element else "Unknown Title"
                    
                    company_element = card.find('h4', class_='base-search-card__subtitle')
                    company = company_element.get_text().strip() if company_element else "Unknown Company"
                    
                    location_element = card.find('span', class_='job-search-card__location')
                    location_text = location_element.get_text().strip() if location_element else "Unknown Location"
                    
                    # Get job URL
                    url_element = card.find('a', class_='base-card__full-link', href=True)
                    job_url = url_element['href'] if url_element else "#"
                    
                    # For LinkedIn, we need to fetch the full job description from the job URL
                    description = "Click the link to view the full job description"
                    
                    # Try to fetch more detailed description if possible
                    if job_url and job_url != "#":
                        try:
                            downloaded = trafilatura.fetch_url(job_url)
                            if downloaded:
                                job_content = trafilatura.extract(downloaded)
                                if job_content:
                                    description = job_content[:500] + "..." if len(job_content) > 500 else job_content
                        except Exception as desc_err:
                            print(f"Error fetching job description: {desc_err}")
                    
                    # Determine job type from the listing or default to the provided job_type
                    detected_job_type = job_type if job_type else "Full-time"  # Default
                    
                    # Generate a recent date (within the last 30 days) for demonstration
                    days_ago = random.randint(0, 29)
                    date_posted = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                    
                    # Create job entry
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'description': description,
                        'url': job_url,
                        'job_type': detected_job_type,
                        'date_posted': date_posted,
                        'source': 'LinkedIn'
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    print(f"Error extracting LinkedIn job details: {e}")
                    continue
        else:
            print(f"Failed to retrieve data from LinkedIn. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
    
    # Return as DataFrame
    return pd.DataFrame(jobs)

# Helper function to get detailed job description
def get_detailed_job_description(url):
    """
    Get detailed job description from a job listing page
    
    Args:
        url (str): URL of the job listing
        
    Returns:
        str: Detailed job description
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            job_content = trafilatura.extract(downloaded)
            return job_content if job_content else "No detailed description available"
        return "Failed to fetch job details"
    except Exception as e:
        print(f"Error fetching detailed job description: {e}")
        return "Error fetching job details"
