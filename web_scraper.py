import trafilatura
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Args:
        url (str): URL of the website to extract text from

    Returns:
        str: Extracted text content
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text if text else "Unable to extract content from this website."
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return f"Error: {str(e)}"


def get_job_details(url: str) -> dict:
    """
    Extract detailed job information from a job posting URL.
    
    Args:
        url (str): URL of the job posting
        
    Returns:
        dict: Dictionary containing job details including description, requirements, etc.
    """
    try:
        # Get the main content of the job posting
        job_content = get_website_text_content(url)
        
        # Process the content to extract structured information
        details = {
            'full_description': job_content,
            'requirements': extract_requirements(job_content),
            'benefits': extract_benefits(job_content)
        }
        
        return details
    except Exception as e:
        print(f"Error fetching job details from {url}: {e}")
        return {'error': str(e)}


def extract_requirements(text: str) -> list:
    """
    Extract job requirements from the job description text.
    
    Args:
        text (str): Job description text
        
    Returns:
        list: List of requirement strings
    """
    # This is a simple implementation - in real application would use NLP or regex
    requirements = []
    
    # Look for common requirement indicators
    text_lower = text.lower()
    sections = text.split('\n')
    
    in_requirements_section = False
    for section in sections:
        if any(req in section.lower() for req in ['requirements', 'qualifications', 'what you need']):
            in_requirements_section = True
            continue
        elif in_requirements_section and any(term in section.lower() for term in ['benefits', 'perks', 'we offer']):
            in_requirements_section = False
        
        if in_requirements_section and section.strip() and len(section.strip()) > 10:
            requirements.append(section.strip())
    
    # If we couldn't find a specific requirements section, look for bullet points with requirement-like content
    if not requirements:
        for section in sections:
            if section.strip().startswith('•') or section.strip().startswith('-'):
                if any(term in section.lower() for term in ['year', 'experience', 'degree', 'skill', 'proficient']):
                    requirements.append(section.strip())
    
    return requirements


def extract_benefits(text: str) -> list:
    """
    Extract job benefits from the job description text.
    
    Args:
        text (str): Job description text
        
    Returns:
        list: List of benefit strings
    """
    # This is a simple implementation - in real application would use NLP or regex
    benefits = []
    
    # Look for common benefit indicators
    text_lower = text.lower()
    sections = text.split('\n')
    
    in_benefits_section = False
    for section in sections:
        if any(ben in section.lower() for ben in ['benefits', 'perks', 'we offer', 'what we offer']):
            in_benefits_section = True
            continue
        elif in_benefits_section and any(term in section.lower() for term in ['how to apply', 'about us', 'company']):
            in_benefits_section = False
        
        if in_benefits_section and section.strip() and len(section.strip()) > 10:
            benefits.append(section.strip())
    
    # If we couldn't find a specific benefits section, look for bullet points with benefit-like content
    if not benefits:
        for section in sections:
            if section.strip().startswith('•') or section.strip().startswith('-'):
                if any(term in section.lower() for term in ['health', 'insurance', 'vacation', 'pto', 'salary', 'bonus', 'remote']):
                    benefits.append(section.strip())
    
    return benefits