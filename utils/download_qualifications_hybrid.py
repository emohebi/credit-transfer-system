from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.exceptions import Fault
import json
import time
from datetime import datetime
import logging
import os
import re
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from multiprocessing import Pool, Manager, cpu_count
from functools import partial

# Set up logging
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logging(output_dir):
    """
    Set up logging to write to both console and file
    
    Args:
        output_dir: Directory where log file will be created
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = os.path.join(output_dir, f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (max 50MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=50*1024*1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Capture more detail in file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized. Log file: {log_filename}")
    return log_filename

logger = logging.getLogger(__name__)

def _extract_qualification_level(title):
    """Extract qualification level from title"""
    title_lower = title.lower()
    
    if 'certificate iii' in title_lower:
        return 'Certificate III'
    elif 'certificate ii' in title_lower:
        return 'Certificate II'
    if 'certificate i' in title_lower and 'certificate iv' not in title_lower:
        return 'Certificate I'
    elif 'certificate iv' in title_lower:
        return 'Certificate IV'
    elif 'advanced diploma' in title_lower:
        return 'Advanced Diploma'
    elif 'graduate certificate' in title_lower:
        return 'Graduate Certificate'
    elif 'graduate diploma' in title_lower:
        return 'Graduate Diploma'
    elif 'diploma' in title_lower and 'advanced' not in title_lower:
        return 'Diploma'
    else:
        return 'Unknown'
    
def _extract_training_package_code(qual_code):
    """Extract training package code from qualification code"""
    match = re.match(r'^([A-Z]+)', qual_code)
    if match:
        return match.group(1)
    return 'OTHER'

class TrainingGovDownloader:
    """
    Download all qualifications and units from training.gov.au
    Uses API for structure and web scraping/XML parsing for detailed content
    Supports multiprocessing for faster downloads
    """
    
    def __init__(self, username, password, use_sandbox=True):
        self.username = username
        self.password = password
        self.wsse = UsernameToken(username, password)
        
        # Choose environment
        base_url = "https://ws.sandbox.training.gov.au" if use_sandbox else "https://ws.training.gov.au"
        self.training_service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
        
        # Initialize client
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the SOAP client"""
        try:
            self.client = Client(self.training_service_url, wsse=self.wsse)
            logger.info("Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise
    
    def search_all_qualifications(self):
        """Search for all qualifications"""
        logger.info("Searching for all qualifications...")
        
        all_qualifications = []
        page_number = 0
        page_size = 100
        
        try:
            while True:
                request = {
                    'SearchCode': True,
                    'SearchTitle': True,
                    'PageNumber': page_number,
                    'PageSize': page_size,
                    'TrainingComponentTypes': {
                        'IncludeQualification': True,
                    }
                }
                
                response = self.client.service.Search(request)
                
                if not hasattr(response, 'Results') or not response.Results:
                    break
                
                if hasattr(response.Results, 'TrainingComponentSummary'):
                    summaries = response.Results.TrainingComponentSummary
                    if not isinstance(summaries, list):
                        summaries = [summaries]
                    
                    for summary in summaries:
                        if hasattr(summary, 'ComponentType'):
                            comp_types = summary.ComponentType
                            if not isinstance(comp_types, list):
                                comp_types = [comp_types]
                            
                            if 'Qualification' in comp_types:
                                all_qualifications.append({
                                    'code': summary.Code,
                                    'title': summary.Title if hasattr(summary, 'Title') else ''
                                })
                    
                    logger.info(f"Retrieved page {page_number + 1}, total: {len(all_qualifications)}")
                    
                    if len(summaries) < page_size:
                        break
                else:
                    break
                
                page_number += 1
                time.sleep(0.2)
            
            logger.info(f"Found {len(all_qualifications)} qualifications")
            return all_qualifications
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return all_qualifications
    
    def get_qualification_with_units(self, code, username, password, use_sandbox, unit_cache):
        """
        Get qualification details with all units
        This is a static method that can be used in multiprocessing
        """
        try:
            # Initialize client in this process
            wsse = UsernameToken(username, password)
            base_url = "https://ws.sandbox.training.gov.au" if use_sandbox else "https://ws.training.gov.au"
            training_service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
            client = Client(training_service_url, wsse=wsse)
            
            request = {'Code': code, 'IncludeLegacyData': False}
            response = client.service.GetDetails(request)
            
            if not response:
                return None
            
            title = response.Title if hasattr(response, 'Title') else ''
            level = _extract_qualification_level(title)
            
            status = 'current'
            if hasattr(response, 'CurrencyStatus'):
                status_value = str(response.CurrencyStatus).lower()
                if 'superseded' in status_value or 'deleted' in status_value:
                    status = 'superseded'
            
            training_package = 'Unknown'
            if hasattr(response, 'ParentCode') and response.ParentCode:
                training_package = response.ParentCode
            else:
                training_package = _extract_training_package_code(code)
            
            qualification = {
                'code': code,
                'name': title,
                'level': level,
                'status': status,
                'training_package': training_package,
                'units': []
            }
            
            # Extract unit codes
            unit_codes = []
            if hasattr(response, 'CompletionMapping') and response.CompletionMapping:
                if hasattr(response.CompletionMapping, 'NrtCompletion'):
                    completions = response.CompletionMapping.NrtCompletion
                    if not isinstance(completions, list):
                        completions = [completions]
                    
                    for comp in completions:
                        if hasattr(comp, 'Code'):
                            if comp.Code not in unit_codes:
                                unit_codes.append(comp.Code)
            
            logger.info(f"[{code}] Found {len(unit_codes)} units (Status: {status}, Package: {training_package})")
            
            # Get details for each unit
            for unit_code in unit_codes:
                # Check if unit is already in cache
                if unit_code in unit_cache:
                    logger.info(f"[{code}] Using cached unit: {unit_code}")
                    qualification['units'].append(unit_cache[unit_code])
                else:
                    unit_details = get_unit_details_formatted(unit_code, username, password, use_sandbox)
                    if unit_details:
                        qualification['units'].append(unit_details)
                        # Add to cache
                        unit_cache[unit_code] = unit_details
                
                time.sleep(0.3)  # Rate limiting
            
            return qualification
            
        except Exception as e:
            logger.error(f"Error getting qualification {code}: {e}")
            return None


def get_unit_details_formatted(code, username, password, use_sandbox):
    """
    Get unit details - standalone function for multiprocessing
    Tries: 1) XML download, 2) Web scraping, 3) API basic
    """
    # logger.info(f"[UNIT] Fetching: {code}")
    
    # Try Method 1: Download and parse XML file
    unit_data = try_xml_download(code, username, password, use_sandbox)
    if unit_data:
        logger.info(f"[UNIT] ✓ {code} via XML")
        return unit_data
    
    # Try Method 2: Web scraping
    unit_data = try_web_scraping(code)
    if unit_data:
        logger.info(f"[UNIT] ✓ {code} via Web")
        return unit_data
    
    # Method 3: Basic API fallback
    unit_data = get_basic_unit_info(code, username, password, use_sandbox)
    if unit_data:
        logger.warning(f"[UNIT] ✓ {code} via API (basic)")
    return unit_data


def try_xml_download(code, username, password, use_sandbox):
    """Try to download and parse XML file for unit"""
    try:
        # Initialize client
        wsse = UsernameToken(username, password)
        base_url = "https://ws.sandbox.training.gov.au" if use_sandbox else "https://ws.training.gov.au"
        training_service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
        client = Client(training_service_url, wsse=wsse)
        
        request = {'Code': code, 'IncludeLegacyData': False}
        response = client.service.GetDetails(request)
        
        if not hasattr(response, 'Releases') or not response.Releases:
            return None
        
        # Find Complete XML file
        xml_path = None
        if hasattr(response.Releases, 'Release'):
            releases = response.Releases.Release
            if not isinstance(releases, list):
                releases = [releases]
            
            for release in releases:
                if hasattr(release, 'Files') and release.Files:
                    if hasattr(release.Files, 'ReleaseFile'):
                        files = release.Files.ReleaseFile
                        if not isinstance(files, list):
                            files = [files]
                        
                        for file in files:
                            if hasattr(file, 'RelativePath'):
                                path = file.RelativePath
                                if '_Complete_' in path and path.endswith('.xml'):
                                    xml_path = path
                                    break
                if xml_path:
                    break
        
        if not xml_path:
            return None
        
        # Try to download the XML file
        base_urls = [
            f"https://training.gov.au/TrainingComponentFiles/{xml_path}",
        ]
        
        xml_content = None
        for url in base_urls:
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200:
                    xml_content = r.content
                    break
            except:
                continue
        
        if not xml_content:
            return None
        
        # Parse the XML using AuthorIT parser
        return parse_authorit_xml(code, xml_content)
        
    except Exception as e:
        logger.debug(f"XML download failed for {code}: {e}")
        return None


def parse_authorit_xml(code, xml_content):
    """Parse AuthorIT XML content"""
    try:
        from authorit_parser import AuthorITParser
        
        parser = AuthorITParser(xml_content)
        unit_data = parser.parse_unit()
        return unit_data
        
    except Exception as e:
        logger.debug(f"AuthorIT parse failed for {code}: {e}")
        return None


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Global driver instance (reuse across calls)
_driver = None

def get_driver():
    """Get or create a Selenium driver"""
    global _driver
    if _driver is None:
        options = Options()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=service, options=options)
    return _driver

def try_web_scraping(code):
    """Try web scraping using Selenium to handle JavaScript rendering"""
    try:
        url = f"https://training.gov.au/Training/Details/{code}"
        logger.info(f"[WEB] Attempting to scrape with Selenium: {url}")
        
        driver = get_driver()
        driver.get(url)
        # Wait for content to load (wait for h1 or main content)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except:
            logger.warning(f"[WEB] Timeout waiting for content: {code}")
            return None
        
        # Give it a moment to fully render
        time.sleep(2)
        
        # Now parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        unit_data = {
            'code': code,
            'name': '',
            'description': '',
            'learning_outcomes': [],
            'assessment_requirements': '',
            'nominal_hours': None,
            'prerequisites': []
        }
        
        # Get title
        title_elem = soup.find('h1')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            unit_data['name'] = title_text.replace(code, '').strip(' -–—')
            logger.info(f"[WEB] Found title: {unit_data['name'][:50]}...")
        else:
            logger.warning(f"[WEB] No title found for {code}")
            return None
        
        description_parts = []
        
        # Helper function to find section
        def find_section(text_pattern):
            """Find a section by heading text"""
            for tag in ['h2', 'h3', 'h4']:
                elem = soup.find(tag, string=re.compile(text_pattern, re.I))
                if elem:
                    return elem
            return None
        
        # Application section
        application_section = find_section(r'Application')
        if application_section:
            logger.info(f"[WEB] Found Application section")
            app_content = []
            for sibling in application_section.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                text = sibling.get_text(strip=True)
                if text:
                    app_content.append(text)
            if app_content:
                description_parts.append(f"Application:\n{' '.join(app_content)}")
        
        # Elements and Performance Criteria
        elements_section = find_section(r'Elements.*Performance.*Criteria')
        if elements_section:
            logger.info(f"[WEB] Found Elements section")
            elements_text = "\n\nElements and Performance Criteria:\n"
            
            table = elements_section.find_next('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        first = cells[0].get_text(strip=True)
                        second = cells[1].get_text(strip=True)
                        if first and second:
                            elements_text += f"{first}: {second}\n"
                description_parts.append(elements_text)
        
        # Foundation Skills
        foundation_section = find_section(r'Foundation.*Skills')
        if foundation_section:
            logger.info(f"[WEB] Found Foundation Skills")
            content = []
            for sibling in foundation_section.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                text = sibling.get_text(strip=True)
                if text:
                    content.append(text)
            if content:
                description_parts.append(f"\n\nFoundation Skills:\n{' '.join(content)}")
        
        unit_data['description'] = '\n'.join(description_parts) if description_parts else 'Content not available'
        
        # Knowledge Evidence
        knowledge_section = find_section(r'Knowledge.*Evidence')
        if knowledge_section:
            ul = knowledge_section.find_next('ul')
            if ul:
                items = []
                for li in ul.find_all('li', recursive=False):
                    text = li.get_text(strip=True)
                    if text:
                        items.append(text)
                unit_data['learning_outcomes'] = items
                logger.info(f"[WEB] Found {len(items)} knowledge items")
        
        # Performance Evidence
        perf_section = find_section(r'Performance.*Evidence')
        if perf_section:
            parts = []
            for sibling in perf_section.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                if sibling.name == 'ul':
                    for li in sibling.find_all('li', recursive=False):
                        text = li.get_text(strip=True)
                        if text:
                            parts.append(f"• {text}")
                else:
                    text = sibling.get_text(strip=True)
                    if text:
                        parts.append(text)
            if parts:
                unit_data['assessment_requirements'] = '\n'.join(parts)
        
        # Assessment Conditions
        assessment_section = find_section(r'Assessment.*Conditions')
        if assessment_section:
            parts = []
            for sibling in assessment_section.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                if sibling.name == 'ul':
                    for li in sibling.find_all('li', recursive=False):
                        text = li.get_text(strip=True)
                        if text:
                            parts.append(f"• {text}")
                else:
                    text = sibling.get_text(strip=True)
                    if text:
                        parts.append(text)
            if parts:
                cond_text = '\n'.join(parts)
                if unit_data['assessment_requirements']:
                    unit_data['assessment_requirements'] += f"\n\nAssessment Conditions:\n{cond_text}"
                else:
                    unit_data['assessment_requirements'] = f"Assessment Conditions:\n{cond_text}"
        
        # Volume of Learning
        vol_text = soup.find(string=re.compile(r'Volume.*Learning', re.I))
        if vol_text:
            parent = vol_text.find_parent()
            if parent:
                text = parent.get_text()
                for sibling in parent.find_next_siblings():
                    if sibling.name in ['h2', 'h3']:
                        break
                    text += ' ' + sibling.get_text()
                
                hours_match = re.search(r'(\d+)\s*hours?', text, re.I)
                if hours_match:
                    unit_data['nominal_hours'] = int(hours_match.group(1))
        
        # Prerequisites
        prereq_section = find_section(r'Pre-?requisite')
        if prereq_section:
            text = ''
            for sibling in prereq_section.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                text += ' ' + sibling.get_text()
            
            codes = re.findall(r'\b[A-Z]{3,10}\d{3,6}[A-Z]?\b', text)
            if codes:
                unit_data['prerequisites'] = list(set(codes))
        
        logger.info(f"[WEB] ✓ Successfully scraped {code}")
        return unit_data
        
    except Exception as e:
        logger.warning(f"[WEB] Selenium scraping failed for {code}: {e}")
        return None

def cleanup_driver():
    """Call this at the end to close the browser"""
    global _driver
    if _driver:
        _driver.quit()
        _driver = None


def get_basic_unit_info(code, username, password, use_sandbox):
    """Fallback: basic info from API"""
    try:
        wsse = UsernameToken(username, password)
        base_url = "https://ws.sandbox.training.gov.au" if use_sandbox else "https://ws.training.gov.au"
        training_service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
        client = Client(training_service_url, wsse=wsse)
        
        request = {'Code': code, 'IncludeLegacyData': False}
        response = client.service.GetDetails(request)
        
        unit_data = {
            'code': code,
            'name': response.Title if hasattr(response, 'Title') else '',
            'description': 'Detailed content not available',
            'learning_outcomes': [],
            'assessment_requirements': '',
            'nominal_hours': None,
            'prerequisites': []
        }
        
        return unit_data
        
    except Exception as e:
        logger.error(f"Error getting basic info for {code}: {e}")
        return None


def process_qualification_wrapper(qual_info, username, password, use_sandbox, output_dir, unit_cache):
    """
    Wrapper function to process a single qualification
    Used for multiprocessing
    """
    qual_code = qual_info['code']
    qual_title = qual_info['title']
    
    logger.info(f"Processing: {qual_code} - {qual_title}")
    
    try:
        downloader = TrainingGovDownloader(username, password, use_sandbox)
        qual_data = downloader.get_qualification_with_units(
            qual_code, username, password, use_sandbox, unit_cache
        )
        
        if qual_data:
            training_package = qual_data.get('training_package', 'Unknown')
            
            if training_package == 'Unknown':
                match = re.match(r'^([A-Z]+)', qual_code)
                if match:
                    training_package = match.group(1)
                else:
                    training_package = 'OTHER'
                qual_data['training_package'] = training_package
            
            # Create training package directory
            package_dir = os.path.join(output_dir, training_package)
            os.makedirs(package_dir, exist_ok=True)
            
            # Save to file
            filename = os.path.join(package_dir, f"{qual_code}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(qual_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved: {qual_code} ({qual_data['status']}, {len(qual_data['units'])} units)")
            
            return {
                'code': qual_code,
                'success': True,
                'status': qual_data['status'],
                'training_package': training_package,
                'unit_count': len(qual_data['units'])
            }
        else:
            logger.warning(f"✗ Failed: {qual_code}")
            return {
                'code': qual_code,
                'success': False
            }
            
    except Exception as e:
        logger.error(f"✗ Error processing {qual_code}: {e}")
        return {
            'code': qual_code,
            'success': False,
            'error': str(e)
        }


def download_all_qualifications_parallel(username, password, use_sandbox, output_dir='qualifications', num_processes=None):
    """
    Download all qualifications using parallel processing
    
    Args:
        username: API username
        password: API password
        use_sandbox: Use sandbox environment
        output_dir: Output directory
        num_processes: Number of parallel processes (default: CPU count - 1)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    log_file = setup_logging(output_dir)
    
    # Initialize downloader to get qualifications list
    downloader = TrainingGovDownloader(username, password, use_sandbox)
    qualifications = downloader.search_all_qualifications()
    
    if not qualifications:
        logger.error("No qualifications found")
        return
    
    # Set number of processes
    if num_processes is None:
        num_processes = max(1, cpu_count() - 1)
    
    logger.info(f"Starting download with {num_processes} parallel processes")
    logger.info(f"Total qualifications to process: {len(qualifications)}")
    
    # Create a manager for shared unit cache
    manager = Manager()
    unit_cache = manager.dict()
    
    # Create partial function with fixed arguments
    process_func = partial(
        process_qualification_wrapper,
        username=username,
        password=password,
        use_sandbox=use_sandbox,
        output_dir=output_dir,
        unit_cache=unit_cache
    )
    
    # Process qualifications in parallel
    start_time = time.time()
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_func, qualifications)
    
    elapsed_time = time.time() - start_time
    
    # Process results
    successful = sum(1 for r in results if r['success'])
    failed = [r['code'] for r in results if not r['success']]
    
    # Calculate statistics
    training_package_stats = {}
    for result in results:
        if result['success']:
            pkg = result['training_package']
            if pkg not in training_package_stats:
                training_package_stats[pkg] = {
                    'total': 0,
                    'current': 0,
                    'superseded': 0
                }
            
            training_package_stats[pkg]['total'] += 1
            if result['status'] == 'current':
                training_package_stats[pkg]['current'] += 1
            else:
                training_package_stats[pkg]['superseded'] += 1
    
    # Generate summary report
    generate_summary_report(
        output_dir,
        len(qualifications),
        successful,
        failed,
        training_package_stats,
        elapsed_time,
        num_processes
    )
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ DOWNLOAD COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total time: {elapsed_time/60:.1f} minutes")
    logger.info(f"Average: {elapsed_time/len(qualifications):.1f} seconds per qualification")
    logger.info(f"Successful: {successful}/{len(qualifications)}")
    logger.info(f"Failed: {len(failed)}")
    logger.info(f"Cached units: {len(unit_cache)}")
    logger.info(f"Files saved to: {output_dir}/")
    logger.info("=" * 80)


def generate_summary_report(output_dir, total, successful, failed, training_package_stats, elapsed_time, num_processes):
    """Generate summary report"""
    summary = {
        'download_date': datetime.now().isoformat(),
        'total_qualifications': total,
        'successful_downloads': successful,
        'failed_downloads': len(failed),
        'failed_codes': failed,
        'elapsed_time_minutes': round(elapsed_time / 60, 2),
        'num_processes': num_processes,
        'training_packages': training_package_stats,
        'training_package_summary': []
    }
    
    for package, stats in sorted(training_package_stats.items()):
        summary['training_package_summary'].append({
            'code': package,
            'total': stats['total'],
            'current': stats['current'],
            'superseded': stats['superseded']
        })
    
    # Save summary
    with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Save failed list if any
    if failed:
        with open(os.path.join(output_dir, '_failed_qualifications.txt'), 'w') as f:
            f.write('\n'.join(failed))
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total qualifications: {total}")
    logger.info(f"Successfully downloaded: {successful}")
    logger.info(f"Failed: {len(failed)}")
    logger.info(f"Time elapsed: {elapsed_time/60:.1f} minutes")
    logger.info(f"Parallel processes: {num_processes}")
    
    logger.info("\nTraining Packages:")
    logger.info("-" * 80)
    logger.info(f"{'Package':<15} {'Total':<10} {'Current':<10} {'Superseded':<10}")
    logger.info("-" * 80)
    
    for item in sorted(summary['training_package_summary'], key=lambda x: x['total'], reverse=True):
        logger.info(f"{item['code']:<15} {item['total']:<10} {item['current']:<10} {item['superseded']:<10}")


def main():
    """Main execution"""
    print("=" * 80)
    print("Training.gov.au - Qualification Downloader (Multiprocessing)")
    print("Downloads qualifications organized by training package")
    print("=" * 80)
    
    # Get credentials
    username = input("Enter your API username: ")
    password = input("Enter your API password: ")
    environment = input("Use sandbox? (y/n): ").lower()
    
    num_processes_input = input(f"Number of parallel processes (default: {max(1, cpu_count()-1)}): ")
    if num_processes_input.strip():
        num_processes = int(num_processes_input)
    else:
        num_processes = None
    
    use_sandbox = environment == 'y'
    
    print(f"\nConnecting to {'SANDBOX' if use_sandbox else 'PRODUCTION'}...")
    print(f"Using {num_processes if num_processes else max(1, cpu_count()-1)} parallel processes")
    print("Method priority: 1) XML download, 2) Web scraping, 3) API basic")
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'qualifications_{timestamp}'
        
        print(f"\nOutput: {output_dir}/")
        print("Organized by training package")
        print("\nStarting download...")
        print("This will be much faster with multiprocessing!")
        print("-" * 80)
        try:
            get_driver()
            download_all_qualifications_parallel(
                username, 
                password, 
                use_sandbox, 
                output_dir=output_dir,
                num_processes=num_processes
            )
        finally:
            cleanup_driver()   
        print(f"\n✓ Complete! Check '{output_dir}' folder")
        print(f"Log file saved in '{output_dir}' folder")
    except KeyboardInterrupt:
        print("\n\nInterrupted - partial data saved")
        print(f"Check log file in '{output_dir}' folder for details")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n✗ Error: {e}")
        print(f"Check log file in '{output_dir}' folder for details")


if __name__ == "__main__":
    main()