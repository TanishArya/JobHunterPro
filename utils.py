import datetime
import re

def format_date(date_obj):
    """
    Format a datetime object as a human-readable string
    
    Args:
        date_obj (datetime.datetime): Date to format
        
    Returns:
        str: Formatted date string
    """
    if not isinstance(date_obj, datetime.datetime):
        return "Unknown"
    
    now = datetime.datetime.now()
    diff = now - date_obj
    
    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    else:
        return date_obj.strftime("%b %d, %Y")

def clean_job_title(title):
    """
    Clean a job title by removing extra information
    
    Args:
        title (str): Job title to clean
        
    Returns:
        str: Cleaned job title
    """
    # Remove patterns like (Remote) or [Full-time] from the title
    cleaned = re.sub(r'\s*[\(\[].*?[\)\]]', '', title)
    return cleaned.strip()

def extract_relevant_keywords(text, keyword_list):
    """
    Extract and highlight keywords from text
    
    Args:
        text (str): Text to search for keywords
        keyword_list (list): List of keywords to highlight
        
    Returns:
        str: Text with highlighted keywords
    """
    if not text or not keyword_list:
        return text
    
    highlighted_text = text
    for keyword in keyword_list:
        if not keyword.strip():
            continue
        
        pattern = re.compile(re.escape(keyword.lower()), re.IGNORECASE)
        highlighted_text = pattern.sub(f"**{keyword}**", highlighted_text)
    
    return highlighted_text

def get_job_posting_age_days(date_posted):
    """
    Calculate the age of a job posting in days
    
    Args:
        date_posted (datetime.datetime): Date the job was posted
        
    Returns:
        int: Age in days
    """
    if not isinstance(date_posted, datetime.datetime):
        return None
    
    now = datetime.datetime.now()
    diff = now - date_posted
    return diff.days

def truncate_text(text, max_length=200):
    """
    Truncate text to a maximum length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Find the nearest space to truncate at
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."
