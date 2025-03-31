# Job Finder Application Dependencies

## Python Packages
The following Python packages are required for this application:

- beautifulsoup4 (>=4.11.1): For parsing HTML and XML documents
- pandas (>=1.4.2): For data manipulation and analysis
- requests (>=2.27.1): For making HTTP requests
- schedule (>=1.1.0): For scheduling recurring tasks
- streamlit (>=1.16.0): For creating the web application interface
- trafilatura (>=1.4.0): For extracting text content from websites
- python-dotenv (>=0.20.0): For loading environment variables from .env files
- lxml (>=4.8.0): XML and HTML processing library

## Installation
These dependencies can be installed using pip:

```bash
pip install beautifulsoup4 pandas requests schedule streamlit trafilatura python-dotenv lxml
```

Or with the provided setup script:

```bash
./setup.sh
```

## Development Environment
For development, it's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```