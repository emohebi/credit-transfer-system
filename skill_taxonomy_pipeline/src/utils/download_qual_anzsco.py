"""
ANZSCO Extraction Module for TGA Qualifications - Final Version

This module extracts ANZSCO codes from the TGA API by parsing the
Classifications.Classification field where:
- SchemeCode "01" = ANZSCO (occupation code)
- SchemeCode "04" = ASCED (field of education)
- SchemeCode "05" = Possibly ANZSIC (industry)
- SchemeCode "06" = Other classification

The ANZSCO code is in the ValueCode field when SchemeCode = "01"

Author: skill_taxonomy_pipeline
"""

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object
import json
import time
import re
import os
import logging
import requests
from datetime import datetime
from multiprocessing import Pool, Manager, cpu_count
from functools import partial
from logging.handlers import RotatingFileHandler

# Classification Scheme Codes
SCHEME_ANZSCO = "01"  # Australian and New Zealand Standard Classification of Occupations
SCHEME_ASCED = "04"   # Australian Standard Classification of Education
SCHEME_ANZSIC = "05"  # Australian and New Zealand Standard Industrial Classification (likely)
SCHEME_OTHER = "06"   # Other classification

# Set up logging
def setup_logging(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    log_filename = os.path.join(output_dir, f'anzsco_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=50*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized: {log_filename}")
    return log_filename

logger = logging.getLogger(__name__)

# ANZSCO Reference Data
ANZSCO_MAJOR_GROUPS = {
    '1': 'Managers',
    '2': 'Professionals',
    '3': 'Technicians and Trades Workers',
    '4': 'Community and Personal Service Workers',
    '5': 'Clerical and Administrative Workers',
    '6': 'Sales Workers',
    '7': 'Machinery Operators and Drivers',
    '8': 'Labourers'
}

ANZSCO_SKILL_LEVELS = {
    '1': 1,  # Managers - typically Skill Level 1
    '2': 1,  # Professionals - typically Skill Level 1
    '3': 3,  # Technicians and Trades - typically Skill Level 2-3
    '4': 2,  # Community/Personal Service - typically Skill Level 2-4
    '5': 2,  # Clerical/Admin - typically Skill Level 2-4
    '6': 4,  # Sales Workers - typically Skill Level 4-5
    '7': 4,  # Machinery Operators - typically Skill Level 4
    '8': 5,  # Labourers - typically Skill Level 5
}


class ANZSCOLookup:
    """Manages ANZSCO code to title lookups from NCVER reference file"""
    
    NCVER_URL = "https://www.ncver.edu.au/__data/assets/file/0025/9664/ANZSCO-2022-revised-April-2023.txt"
    CACHE_FILE = "anzsco_reference_cache.json"
    
    def __init__(self, cache_dir=None):
        self.anzsco_data = {}
        self._loaded = False
        self.cache_dir = cache_dir or os.path.dirname(os.path.abspath(__file__))
    
    def _get_cache_path(self):
        """Get the path to the cache file"""
        return os.path.join(self.cache_dir, self.CACHE_FILE)
    
    def _load_from_cache(self):
        """Try to load data from local cache"""
        cache_path = self._get_cache_path()
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    # Check if cache is less than 30 days old
                    cache_date = datetime.fromisoformat(cached.get('date', '2000-01-01'))
                    if (datetime.now() - cache_date).days < 30:
                        self.anzsco_data = cached.get('data', {})
                        self._loaded = True
                        logger.info(f"Loaded {len(self.anzsco_data)} ANZSCO codes from cache")
                        return True
            except Exception as e:
                logger.debug(f"Could not load cache: {e}")
        return False
    
    def _save_to_cache(self):
        """Save data to local cache"""
        try:
            cache_path = self._get_cache_path()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'date': datetime.now().isoformat(),
                    'source': self.NCVER_URL,
                    'data': self.anzsco_data
                }, f, indent=2)
            logger.info(f"Saved ANZSCO cache to {cache_path}")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def load_from_ncver(self, force_download=False):
        """
        Load ANZSCO codes from NCVER reference file.
        
        File format (tab-delimited):
        - Column 1: ANZSCO Code (6 digits)
        - Column 2: Description/Title
        - Column 3: Effective to date (blank if current, date if retired)
        
        Example:
        512111\tOffice Manager\t
        121200\tCrop Farmers\t2022-04-21  (retired)
        """
        # Try cache first unless forced
        if not force_download and self._load_from_cache():
            return True
        
        try:
            logger.info(f"Downloading ANZSCO reference data from NCVER...")
            logger.info(f"URL: {self.NCVER_URL}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/plain, text/html, */*',
            }
            
            response = requests.get(self.NCVER_URL, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the tab-delimited file
            lines = response.text.strip().split('\n')
            
            # Skip header line if present
            start_idx = 0
            if lines and not lines[0][0].isdigit():
                start_idx = 1
            
            for line in lines[start_idx:]:
                # Split by tab
                parts = line.split('\t')
                if len(parts) >= 2:
                    code = parts[0].strip()
                    title = parts[1].strip()
                    effective_to = parts[2].strip() if len(parts) > 2 else ''
                    
                    # Validate code format (should be 6 digits)
                    if re.match(r'^\d{6}$', code):
                        # Only include current codes (no effective_to date)
                        # Codes with an effective_to date have been retired
                        if not effective_to:
                            self.anzsco_data[code] = title
                        else:
                            # Also store retired codes with a marker
                            self.anzsco_data[code] = f"{title} (retired {effective_to})"
            
            self._loaded = True
            logger.info(f"Loaded {len(self.anzsco_data)} ANZSCO codes from NCVER")
            
            # Save to cache
            self._save_to_cache()
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not download NCVER data: {e}")
            # Try to load from cache even if expired
            if self._load_from_cache():
                logger.info("Using cached data (may be outdated)")
                return True
            return False
        except Exception as e:
            logger.warning(f"Error parsing NCVER data: {e}")
            return False
    
    def load_from_file(self, filepath):
        """Load ANZSCO data from a local file"""
        try:
            logger.info(f"Loading ANZSCO data from file: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Skip header line if present
            start_idx = 0
            if lines and not lines[0].strip()[0].isdigit():
                start_idx = 1
            
            for line in lines[start_idx:]:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    code = parts[0].strip()
                    title = parts[1].strip()
                    effective_to = parts[2].strip() if len(parts) > 2 else ''
                    
                    if re.match(r'^\d{6}$', code):
                        if not effective_to:
                            self.anzsco_data[code] = title
                        else:
                            self.anzsco_data[code] = f"{title} (retired {effective_to})"
            
            self._loaded = True
            logger.info(f"Loaded {len(self.anzsco_data)} ANZSCO codes from file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            return False
    
    def get_title(self, code):
        """Get title for an ANZSCO code"""
        if not self._loaded:
            self.load_from_ncver()
        
        code = str(code).strip()
        return self.anzsco_data.get(code)
    
    def get_hierarchy(self, code):
        """Get full hierarchy for an ANZSCO code"""
        if not self._loaded:
            self.load_from_ncver()
        
        code = str(code).strip()
        hierarchy = {}
        
        if len(code) >= 6:
            # Major group (1xxxxx -> 100000)
            major = code[0] + '00000'
            if major in self.anzsco_data:
                hierarchy['major_group'] = {'code': major, 'title': self.anzsco_data[major]}
            
            # Sub-major group (12xxxx -> 120000)
            sub_major = code[:2] + '0000'
            if sub_major in self.anzsco_data:
                hierarchy['sub_major_group'] = {'code': sub_major, 'title': self.anzsco_data[sub_major]}
            
            # Minor group (123xxx -> 123000)
            minor = code[:3] + '000'
            if minor in self.anzsco_data:
                hierarchy['minor_group'] = {'code': minor, 'title': self.anzsco_data[minor]}
            
            # Unit group (1234xx -> 123400)
            unit = code[:4] + '00'
            if unit in self.anzsco_data:
                hierarchy['unit_group'] = {'code': unit, 'title': self.anzsco_data[unit]}
            
            # Occupation (123456)
            if code in self.anzsco_data:
                hierarchy['occupation'] = {'code': code, 'title': self.anzsco_data[code]}
        
        return hierarchy
    
    def search_by_title(self, keyword, limit=20):
        """Search ANZSCO codes by title keyword"""
        if not self._loaded:
            self.load_from_ncver()
        
        keyword = keyword.lower()
        results = []
        
        for code, title in self.anzsco_data.items():
            if keyword in title.lower():
                results.append({'code': code, 'title': title})
                if len(results) >= limit:
                    break
        
        return results


# Global lookup instance
_anzsco_lookup = None

def get_anzsco_lookup(cache_dir=None):
    """Get or create the global ANZSCO lookup instance"""
    global _anzsco_lookup
    if _anzsco_lookup is None:
        _anzsco_lookup = ANZSCOLookup(cache_dir=cache_dir)
        _anzsco_lookup.load_from_ncver()
    return _anzsco_lookup


def set_anzsco_lookup(lookup):
    """Set a custom ANZSCO lookup instance"""
    global _anzsco_lookup
    _anzsco_lookup = lookup


def extract_classification_from_response(response_dict):
    """
    Extract ANZSCO and other classifications from API response.
    
    The Classifications field contains a list of Classification objects:
    - SchemeCode "01" = ANZSCO
    - SchemeCode "04" = ASCED
    - ValueCode contains the actual code
    
    Returns:
        dict with anzsco_code, anzsco_title, full hierarchy, etc.
    """
    result = {
        'anzsco_code': None,
        'anzsco_title': None,
        'anzsco_major_group': None,
        'anzsco_major_group_code': None,
        'anzsco_sub_major_group': None,
        'anzsco_minor_group': None,
        'anzsco_unit_group': None
        # 'anzsco_skill_level': None
        # 'asced_code': None,
        # 'asced_title': None
        # 'other_classifications': []
    }
    
    if not response_dict:
        return result
    
    # Get Classifications field
    classifications = response_dict.get('Classifications')
    if not classifications:
        return result
    
    # Get the Classification list
    classification_list = classifications.get('Classification', [])
    if not isinstance(classification_list, list):
        classification_list = [classification_list]
    
    for classification in classification_list:
        if not isinstance(classification, dict):
            continue
        
        scheme_code = classification.get('SchemeCode')
        value_code = classification.get('ValueCode')
        
        if not scheme_code or not value_code:
            continue
        
        if scheme_code == SCHEME_ANZSCO:
            # ANZSCO (Occupation)
            anzsco_code = str(value_code)
            result['anzsco_code'] = anzsco_code
            
            # Get title and hierarchy from lookup
            lookup = get_anzsco_lookup()
            result['anzsco_title'] = lookup.get_title(anzsco_code)
            
            # Get full hierarchy
            hierarchy = lookup.get_hierarchy(anzsco_code)
            
            if hierarchy.get('major_group'):
                result['anzsco_major_group'] = hierarchy['major_group']['title']
                result['anzsco_major_group_code'] = hierarchy['major_group']['code']
            else:
                # Fallback to static mapping if hierarchy not found
                if len(anzsco_code) >= 1:
                    major_digit = anzsco_code[0]
                    result['anzsco_major_group'] = ANZSCO_MAJOR_GROUPS.get(major_digit)
                    result['anzsco_major_group_code'] = major_digit + '00000'
            
            if hierarchy.get('sub_major_group'):
                result['anzsco_sub_major_group'] = hierarchy['sub_major_group']['title']
            
            if hierarchy.get('minor_group'):
                result['anzsco_minor_group'] = hierarchy['minor_group']['title']
            
            if hierarchy.get('unit_group'):
                result['anzsco_unit_group'] = hierarchy['unit_group']['title']
            
            # Get skill level from major group
            # if len(anzsco_code) >= 1:
            #     major_digit = anzsco_code[0]
            #     result['anzsco_skill_level'] = ANZSCO_SKILL_LEVELS.get(major_digit)
        
        # elif scheme_code == SCHEME_ASCED:
        #     # ASCED (Field of Education)
        #     result['asced_code'] = str(value_code)
            # Could add ASCED title lookup here
        
        # else:
            # Other classifications
            # result['other_classifications'].append({
            #     'scheme_code': scheme_code,
            #     'value_code': str(value_code),
            #     'start_date': classification.get('StartDate'),
            #     'end_date': classification.get('EndDate')
            # })
    
    return result


class TGAANZSCOExtractor:
    """
    Extract ANZSCO codes from TGA API using the Classifications field
    """
    
    def __init__(self, username, password, use_sandbox=True):
        self.username = username
        self.password = password
        self.wsse = UsernameToken(username, password)
        
        base_url = "https://ws.sandbox.training.gov.au" if use_sandbox else "https://ws.training.gov.au"
        self.service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
        
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the SOAP client"""
        try:
            self.client = Client(self.service_url, wsse=self.wsse)
            logger.info("TGA API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise
    
    def get_qualification_details(self, code):
        """Get full details for a qualification including classifications"""
        try:
            request = {'Code': code, 'IncludeLegacyData': False}
            response = self.client.service.GetDetails(request)
            
            if response:
                return serialize_object(response)
            return None
            
        except Exception as e:
            logger.error(f"Error getting details for {code}: {e}")
            return None
    
    def get_qualification_anzsco(self, code):
        """
        Get ANZSCO classification for a single qualification.
        
        Returns:
            dict with qualification info and ANZSCO data
        """
        response_dict = self.get_qualification_details(code)
        
        if not response_dict:
            return {
                'qualification_code': code,
                'error': 'No response from API'
            }
        
        # Extract classification data
        classification_data = extract_classification_from_response(response_dict)
        
        # Build result
        result = {
            'qualification_code': code,
            'qualification_title': response_dict.get('Title', ''),
            'training_package': response_dict.get('ParentCode', ''),
            'status': 'current',
            **classification_data
        }
        
        # Check status
        if hasattr(response_dict, 'CurrencyStatus'):
            status_value = str(response_dict.get('CurrencyStatus', '')).lower()
            if 'superseded' in status_value or 'deleted' in status_value:
                result['status'] = 'superseded'
        
        return result
    
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
                    
                    logger.info(f"Page {page_number + 1}: {len(all_qualifications)} qualifications found")
                    
                    if len(summaries) < page_size:
                        break
                else:
                    break
                
                page_number += 1
                time.sleep(0.2)
            
            logger.info(f"Total qualifications found: {len(all_qualifications)}")
            return all_qualifications
            
        except Exception as e:
            logger.error(f"Error searching qualifications: {e}")
            return all_qualifications


def process_single_qualification(qual_info, username, password, use_sandbox):
    """
    Process a single qualification - used for multiprocessing.
    Creates a new client connection for each process.
    """
    try:
        extractor = TGAANZSCOExtractor(username, password, use_sandbox)
        result = extractor.get_qualification_anzsco(qual_info['code'])
        
        if result.get('anzsco_code'):
            logger.info(f"✓ {qual_info['code']}: ANZSCO={result['anzsco_code']} ({result.get('anzsco_title', 'Unknown')})")
        else:
            logger.debug(f"○ {qual_info['code']}: No ANZSCO found")
        
        return result
        
    except Exception as e:
        logger.error(f"✗ {qual_info['code']}: Error - {e}")
        return {
            'qualification_code': qual_info['code'],
            'qualification_title': qual_info.get('title', ''),
            'error': str(e)
        }


def download_all_anzsco(username, password, use_sandbox=True, output_dir='anzsco_output', 
                        num_processes=None, anzsco_file=None):
    """
    Download ANZSCO classifications for all qualifications.
    
    Args:
        username: TGA API username
        password: TGA API password
        use_sandbox: Use sandbox environment (default True)
        output_dir: Output directory for results
        num_processes: Number of parallel processes (default: CPU count - 1)
        anzsco_file: Path to local ANZSCO reference file (optional)
                     Download from: https://www.ncver.edu.au/__data/assets/file/0025/9664/ANZSCO-2022-revised-April-2023.txt
    """
    os.makedirs(output_dir, exist_ok=True)
    setup_logging(output_dir)
    
    logger.info("="*80)
    logger.info("TGA ANZSCO EXTRACTION")
    logger.info("="*80)
    logger.info(f"Environment: {'SANDBOX' if use_sandbox else 'PRODUCTION'}")
    
    # Pre-load ANZSCO reference data
    global _anzsco_lookup
    _anzsco_lookup = ANZSCOLookup(cache_dir=output_dir)
    
    if anzsco_file and os.path.exists(anzsco_file):
        # Load from provided local file
        logger.info(f"Loading ANZSCO reference data from local file: {anzsco_file}")
        if not _anzsco_lookup.load_from_file(anzsco_file):
            logger.warning("Could not load ANZSCO reference file - titles will be missing")
    else:
        # Try to download from NCVER
        logger.info("Loading ANZSCO reference data from NCVER...")
        if not _anzsco_lookup.load_from_ncver():
            logger.warning("Could not load ANZSCO reference data - titles will be missing")
            logger.warning("You can download the file manually from:")
            logger.warning("  https://www.ncver.edu.au/__data/assets/file/0025/9664/ANZSCO-2022-revised-April-2023.txt")
            logger.warning("Then pass the path using anzsco_file parameter")
    
    # Get list of qualifications
    extractor = TGAANZSCOExtractor(username, password, use_sandbox)
    qualifications = extractor.search_all_qualifications()
    
    if not qualifications:
        logger.error("No qualifications found!")
        return None
    
    # Set up multiprocessing
    if num_processes is None:
        num_processes = max(1, cpu_count() - 1)
    
    logger.info(f"Processing {len(qualifications)} qualifications with {num_processes} processes...")
    
    # Process qualifications
    start_time = time.time()
    
    process_func = partial(
        process_single_qualification,
        username=username,
        password=password,
        use_sandbox=use_sandbox
    )
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_func, qualifications)
    
    elapsed_time = time.time() - start_time
    
    # Compile statistics
    stats = {
        'total_qualifications': len(qualifications),
        'with_anzsco': 0,
        'without_anzsco': 0,
        'errors': 0,
        'by_major_group': {},
        'by_skill_level': {},
        'processing_time_seconds': round(elapsed_time, 2)
    }
    
    valid_results = []
    
    for result in results:
        if result.get('error'):
            stats['errors'] += 1
        elif result.get('anzsco_code'):
            stats['with_anzsco'] += 1
            
            # Count by major group
            major_group = result.get('anzsco_major_group', 'Unknown')
            stats['by_major_group'][major_group] = stats['by_major_group'].get(major_group, 0) + 1
            
            # Count by skill level
            skill_level = result.get('anzsco_skill_level')
            if skill_level:
                level_key = f"Level {skill_level}"
                stats['by_skill_level'][level_key] = stats['by_skill_level'].get(level_key, 0) + 1
        else:
            stats['without_anzsco'] += 1
        
        valid_results.append(result)
    
    # Save results
    output = {
        'extraction_date': datetime.now().isoformat(),
        'environment': 'sandbox' if use_sandbox else 'production',
        'statistics': stats,
        'mappings': valid_results
    }
    
    output_file = os.path.join(output_dir, 'qualification_anzsco_mappings.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_results, f, indent=2, ensure_ascii=False)
    
    # Also save a simple CSV for easy viewing
    csv_file = os.path.join(output_dir, 'qualification_anzsco_mappings.csv')
    with open(csv_file, 'w', encoding='utf-8') as f:
        # Write header
        headers = [
            "qualification_code",
            "qualification_title", 
            "anzsco_code",
            "anzsco_title",
            "anzsco_major_group",
            "anzsco_sub_major_group",
            "anzsco_minor_group",
            "anzsco_unit_group",
            "anzsco_skill_level",
            "asced_code",
            "training_package",
            "status"
        ]
        f.write(",".join(headers) + "\n")
        
        for r in valid_results:
            line = ','.join([
                f'"{r.get("qualification_code", "")}"',
                f'"{(r.get("qualification_title") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{r.get("anzsco_code") or ""}"',
                f'"{(r.get("anzsco_title") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{(r.get("anzsco_major_group") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{(r.get("anzsco_sub_major_group") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{(r.get("anzsco_minor_group") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{(r.get("anzsco_unit_group") or "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{r.get("anzsco_skill_level") or ""}"',
                f'"{r.get("asced_code") or ""}"',
                f'"{r.get("training_package") or ""}"',
                f'"{r.get("status") or ""}"'
            ])
            f.write(line + "\n")
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("EXTRACTION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total qualifications: {stats['total_qualifications']}")
    logger.info(f"With ANZSCO code: {stats['with_anzsco']}")
    logger.info(f"Without ANZSCO code: {stats['without_anzsco']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Processing time: {elapsed_time/60:.1f} minutes")
    
    if stats['by_major_group']:
        logger.info("\nBy ANZSCO Major Group:")
        for group, count in sorted(stats['by_major_group'].items(), key=lambda x: -x[1]):
            logger.info(f"  {group}: {count}")
    
    if stats['by_skill_level']:
        logger.info("\nBy Skill Level:")
        for level, count in sorted(stats['by_skill_level'].items()):
            logger.info(f"  {level}: {count}")
    
    logger.info(f"\nResults saved to:")
    logger.info(f"  JSON: {output_file}")
    logger.info(f"  CSV:  {csv_file}")
    
    return valid_results


def test_single_qualification(username, password, qual_code, use_sandbox=True, anzsco_file=None):
    """
    Test extraction for a single qualification.
    Useful for debugging and verification.
    
    Args:
        username: TGA API username
        password: TGA API password
        qual_code: Qualification code to test (e.g., 'BSB50120')
        use_sandbox: Use sandbox environment (default True)
        anzsco_file: Path to local ANZSCO reference file (optional)
    """
    print(f"\n{'='*60}")
    print(f"Testing ANZSCO extraction for: {qual_code}")
    print('='*60)
    
    # Load ANZSCO reference data if file provided
    global _anzsco_lookup
    if anzsco_file and os.path.exists(anzsco_file):
        print(f"\nLoading ANZSCO reference data from: {anzsco_file}")
        _anzsco_lookup = ANZSCOLookup()
        if _anzsco_lookup.load_from_file(anzsco_file):
            print(f"✓ Loaded {len(_anzsco_lookup.anzsco_data)} ANZSCO codes")
        else:
            print("✗ Failed to load ANZSCO reference file")
    elif anzsco_file:
        print(f"✗ File not found: {anzsco_file}")
    
    extractor = TGAANZSCOExtractor(username, password, use_sandbox)
    
    # Get raw response
    print("\n1. Getting raw API response...")
    response = extractor.get_qualification_details(qual_code)
    
    if response:
        # Show Classifications field
        print("\n2. Classifications field content:")
        classifications = response.get('Classifications', {})
        print(json.dumps(classifications, indent=2, default=str))
        
        # Extract ANZSCO
        print("\n3. Extracted ANZSCO data:")
        result = extractor.get_qualification_anzsco(qual_code)
        print(json.dumps(result, indent=2, default=str))
        
        return result
    else:
        print("No response from API")
        return None


def main():
    """Main entry point"""
    print("="*80)
    print("TGA ANZSCO EXTRACTION - Final Version")
    print("="*80)
    print("\nThis tool extracts ANZSCO codes from the Classifications field")
    print("in the TGA API response (SchemeCode='01' = ANZSCO).\n")
    
    # Get credentials
    username = "WebService.Read"
    password = "Asdf098"
    env = 'y'
    use_sandbox = env == 'y'
    
    print(f"\nEnvironment: {'SANDBOX' if use_sandbox else 'PRODUCTION'}")
    
    # Ask for ANZSCO reference file FIRST
    print("\n" + "-"*60)
    print("ANZSCO Reference File (for occupation titles)")
    print("-"*60)
    # print("Download from: https://www.ncver.edu.au/__data/assets/file/0025/9664/ANZSCO-2022-revised-April-2023.txt")
    anzsco_file = "skill_taxonomy_pipeline/src/utils/anzsco.txt"
    
    if anzsco_file and not os.path.exists(anzsco_file):
        print(f"Warning: File not found: {anzsco_file}")
        anzsco_file = None
    
    # Test with a single qualification first
    print("\n" + "-"*60)
    print("TEST SINGLE QUALIFICATION")
    print("-"*60)
    test_code = input("Test qualification code [BSB50120]: ").strip() or "BSB50120"
    result = test_single_qualification(username, password, test_code, use_sandbox, anzsco_file)
    
    if result and result.get('anzsco_code'):
        print(f"\n✓ Successfully extracted ANZSCO: {result['anzsco_code']}")
        if result.get('anzsco_title'):
            print(f"  Title: {result['anzsco_title']}")
        else:
            print("  Title: (not found - check ANZSCO reference file)")
        if result.get('anzsco_major_group'):
            print(f"  Major Group: {result['anzsco_major_group']}")
        if result.get('anzsco_unit_group'):
            print(f"  Unit Group: {result['anzsco_unit_group']}")
    else:
        print(f"\n○ No ANZSCO found for {test_code}")
    
    # Ask if user wants to proceed
    proceed = input("\nProceed with full extraction? (y/n): ").strip().lower()
    
    if proceed == 'y':
        num_procs = input(f"Number of processes [{max(1, cpu_count()-1)}]: ").strip()
        num_processes = int(num_procs) if num_procs else None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'anzsco_output_{timestamp}'
        
        download_all_anzsco(
            username, password, use_sandbox,
            output_dir=output_dir,
            num_processes=num_processes,
            anzsco_file=anzsco_file
        )
        
        print(f"\n✓ Complete! Results in '{output_dir}' folder")


if __name__ == "__main__":
    main()