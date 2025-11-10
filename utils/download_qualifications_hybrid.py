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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingGovDownloader:
    """
    Download all qualifications and units from training.gov.au
    Tries XML download first, falls back to web scraping
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
        
        # Cache for unit details
        self.unit_cache = {}
        
        # Track method success rates
        self.xml_success = 0
        self.web_scrape_success = 0
        self.api_fallback = 0
    
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
    
    def _extract_qualification_level(self, title):
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
    
    def _extract_training_package_code(self, qual_code):
        """Extract training package code from qualification code"""
        match = re.match(r'^([A-Z]+)', qual_code)
        if match:
            return match.group(1)
        return 'OTHER'
    
    def get_qualification_with_units(self, code):
        """Get qualification details with all units"""
        logger.info(f"Fetching qualification: {code}")
        
        try:
            request = {'Code': code, 'IncludeLegacyData': False}
            response = self.client.service.GetDetails(request)
            
            if not response:
                return None
            
            title = response.Title if hasattr(response, 'Title') else ''
            level = self._extract_qualification_level(title)
            
            status = 'current'
            if hasattr(response, 'CurrencyStatus'):
                status_value = str(response.CurrencyStatus).lower()
                if 'superseded' in status_value or 'deleted' in status_value:
                    status = 'superseded'
            
            training_package = 'Unknown'
            if hasattr(response, 'ParentCode') and response.ParentCode:
                training_package = response.ParentCode
            else:
                training_package = self._extract_training_package_code(code)
            
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
            
            logger.info(f"Found {len(unit_codes)} units for {code}")
            
            # Get details for each unit
            for unit_code in unit_codes:
                unit_details = self.get_unit_details_formatted(unit_code)
                if unit_details:
                    qualification['units'].append(unit_details)
                time.sleep(0.5)
            
            return qualification
            
        except Exception as e:
            logger.error(f"Error getting qualification {code}: {e}")
            return None
    
    def get_unit_details_formatted(self, code):
        """Get unit details - tries XML download, then web scraping"""
        # Check cache
        if code in self.unit_cache:
            logger.info(f"Using cached data for unit: {code}")
            return self.unit_cache[code]
        
        logger.info(f"Fetching unit: {code}")
        
        # Try Method 1: Download and parse XML file
        unit_data = self._try_xml_download(code)
        if unit_data:
            self.xml_success += 1
            self.unit_cache[code] = unit_data
            return unit_data
        
        # Try Method 2: Web scraping
        unit_data = self._try_web_scraping(code)
        if unit_data:
            self.web_scrape_success += 1
            self.unit_cache[code] = unit_data
            return unit_data
        
        # Method 3: Basic API fallback
        unit_data = self._get_basic_unit_info(code)
        if unit_data:
            self.api_fallback += 1
            self.unit_cache[code] = unit_data
        return unit_data
    
    def _try_xml_download(self, code):
        """Try to download and parse XML file for unit"""
        try:
            # Get file path from API
            request = {'Code': code, 'IncludeLegacyData': False}
            response = self.client.service.GetDetails(request)
            
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
            # The file location might be at training.gov.au/TrainingComponentFiles/
            base_urls = [
                f"https://training.gov.au/TrainingComponentFiles/{xml_path}",
                f"https://training.gov.au/Home/Tga/DownloadFile?Path={xml_path}",
            ]
            
            xml_content = None
            for url in base_urls:
                try:
                    r = requests.get(url, timeout=30)
                    if r.status_code == 200:
                        xml_content = r.content
                        logger.info(f"✓ Downloaded XML for {code}")
                        break
                except:
                    continue
            
            if not xml_content:
                return None
            
            # Parse the XML
            return self._parse_unit_xml(code, xml_content)
            
        except Exception as e:
            logger.debug(f"XML download failed for {code}: {e}")
            return None
    
    def _parse_unit_xml(self, code, xml_content):
        """Parse unit XML content to extract details - supports AuthorIT format"""
        try:
            # Try AuthorIT format first (training.gov.au uses this)
            from authorit_parser import AuthorITParser
            
            try:
                parser = AuthorITParser(xml_content)
                unit_data = parser.parse_unit()
                logger.info(f"✓ Parsed XML using AuthorIT parser for {code}")
                return unit_data
            except Exception as e:
                logger.debug(f"AuthorIT parser failed for {code}: {e}")
                # Fall through to try standard format
            
            # Try standard XML format
            root = ET.fromstring(xml_content)
            
            # Define namespace
            ns = {'': 'http://training.gov.au'}
            
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
            title_elem = root.find('.//Title', ns)
            if title_elem is not None and title_elem.text:
                unit_data['name'] = title_elem.text.strip()
            
            description_parts = []
            
            # Application
            app_elem = root.find('.//Application', ns)
            if app_elem is not None and app_elem.text:
                description_parts.append(f"Application:\n{app_elem.text.strip()}")
            
            # Elements and Performance Criteria
            elements = root.findall('.//Element', ns)
            if elements:
                elem_text = "\n\nElements and Performance Criteria:\n"
                for i, elem in enumerate(elements, 1):
                    elem_title = elem.find('Title', ns)
                    if elem_title is not None and elem_title.text:
                        elem_text += f"\nElement {i}: {elem_title.text.strip()}\n"
                    
                    criteria = elem.findall('.//PerformanceCriterion', ns)
                    for j, pc in enumerate(criteria, 1):
                        pc_text = pc.find('Text', ns)
                        if pc_text is not None and pc_text.text:
                            elem_text += f"  {i}.{j} {pc_text.text.strip()}\n"
                
                description_parts.append(elem_text)
            
            # Foundation Skills
            foundation = root.findall('.//FoundationSkill', ns)
            if foundation:
                found_text = "\n\nFoundation Skills:\n"
                for skill in foundation:
                    name = skill.find('Name', ns)
                    desc = skill.find('Description', ns)
                    if name is not None and name.text:
                        found_text += f"\n{name.text.strip()}:\n"
                    if desc is not None and desc.text:
                        found_text += f"{desc.text.strip()}\n"
                description_parts.append(found_text)
            
            unit_data['description'] = '\n'.join(description_parts)
            
            # Knowledge Evidence
            knowledge_elem = root.find('.//KnowledgeEvidence', ns)
            if knowledge_elem is not None and knowledge_elem.text:
                lines = knowledge_elem.text.split('\n')
                outcomes = []
                for line in lines:
                    line = line.strip().lstrip('•-*').strip()
                    line = re.sub(r'^\d+\.?\s*', '', line)
                    if line:
                        outcomes.append(line)
                unit_data['learning_outcomes'] = outcomes
            
            # Assessment Requirements
            assess_elem = root.find('.//AssessmentRequirements', ns)
            if assess_elem is not None and assess_elem.text:
                unit_data['assessment_requirements'] = assess_elem.text.strip()
            
            # Performance Evidence
            perf_elem = root.find('.//PerformanceEvidence', ns)
            if perf_elem is not None and perf_elem.text:
                perf_text = perf_elem.text.strip()
                if unit_data['assessment_requirements']:
                    unit_data['assessment_requirements'] += f"\n\nPerformance Evidence:\n{perf_text}"
                else:
                    unit_data['assessment_requirements'] = f"Performance Evidence:\n{perf_text}"
            
            # Volume of Learning
            vol_elem = root.find('.//VolumeOfLearning', ns)
            if vol_elem is not None and vol_elem.text:
                try:
                    unit_data['nominal_hours'] = int(vol_elem.text.strip())
                except:
                    pass
            
            # Prerequisites
            prereq_elem = root.find('.//Prerequisite', ns)
            if prereq_elem is not None and prereq_elem.text:
                codes = re.findall(r'[A-Z]{3,10}\d{3,6}[A-Z]?', prereq_elem.text)
                unit_data['prerequisites'] = codes
            
            return unit_data
            
        except Exception as e:
            logger.error(f"Error parsing XML for {code}: {e}")
            return None
    
    def _try_web_scraping(self, code):
        """Try web scraping from training.gov.au"""
        try:
            url = f"https://training.gov.au/Training/Details/{code}"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
                unit_data['name'] = title_text.replace(code, '').strip(' -')
            
            description_parts = []
            
            # Application
            application_section = soup.find('h2', string=re.compile(r'Application', re.I))
            if application_section:
                app_content = []
                for sibling in application_section.find_next_siblings():
                    if sibling.name == 'h2':
                        break
                    text = sibling.get_text(strip=True)
                    if text:
                        app_content.append(text)
                if app_content:
                    description_parts.append(f"Application:\n{' '.join(app_content)}")
            
            # Elements and Performance Criteria
            elements_section = soup.find('h2', string=re.compile(r'Elements and Performance Criteria', re.I))
            if elements_section:
                elements_text = "\n\nElements and Performance Criteria:\n"
                table = elements_section.find_next('table')
                if table:
                    rows = table.find_all('tr')
                    element_num = 0
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            first_cell = cells[0].get_text(strip=True)
                            second_cell = cells[1].get_text(strip=True)
                            
                            if first_cell and (first_cell.lower().startswith('element') or re.match(r'^\d+\.$', first_cell)):
                                element_num += 1
                                elements_text += f"\nElement {element_num}: {second_cell}\n"
                            elif second_cell:
                                elements_text += f"  {first_cell} {second_cell}\n"
                
                description_parts.append(elements_text)
            
            # Foundation Skills
            foundation_section = soup.find('h2', string=re.compile(r'Foundation Skills', re.I))
            if foundation_section:
                foundation_text = "\n\nFoundation Skills:\n"
                for sibling in foundation_section.find_next_siblings():
                    if sibling.name == 'h2':
                        break
                    text = sibling.get_text(strip=True)
                    if text:
                        foundation_text += f"{text}\n"
                description_parts.append(foundation_text)
            
            unit_data['description'] = '\n'.join(description_parts) if description_parts else 'Content not available'
            
            # Knowledge Evidence
            knowledge_section = soup.find('h3', string=re.compile(r'Knowledge Evidence', re.I))
            if not knowledge_section:
                knowledge_section = soup.find('h2', string=re.compile(r'Knowledge Evidence', re.I))
            
            if knowledge_section:
                knowledge_items = []
                ul = knowledge_section.find_next('ul')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            knowledge_items.append(text)
                unit_data['learning_outcomes'] = knowledge_items
            
            # Assessment Requirements
            assessment_section = soup.find('h2', string=re.compile(r'Assessment Requirements', re.I))
            if assessment_section:
                assessment_parts = []
                for sibling in assessment_section.find_next_siblings():
                    if sibling.name == 'h2':
                        break
                    text = sibling.get_text(strip=True)
                    if text:
                        assessment_parts.append(text)
                unit_data['assessment_requirements'] = '\n'.join(assessment_parts)
            
            # Performance Evidence
            performance_section = soup.find('h3', string=re.compile(r'Performance Evidence', re.I))
            if not performance_section:
                performance_section = soup.find('h2', string=re.compile(r'Performance Evidence', re.I))
            
            if performance_section:
                perf_parts = []
                for sibling in performance_section.find_next_siblings():
                    if sibling.name in ['h2', 'h3']:
                        break
                    text = sibling.get_text(strip=True)
                    if text:
                        perf_parts.append(text)
                
                if perf_parts:
                    perf_text = '\n'.join(perf_parts)
                    if unit_data['assessment_requirements']:
                        unit_data['assessment_requirements'] += f"\n\nPerformance Evidence:\n{perf_text}"
                    else:
                        unit_data['assessment_requirements'] = f"Performance Evidence:\n{perf_text}"
            
            # Volume of Learning
            vol_section = soup.find(string=re.compile(r'Volume of Learning', re.I))
            if vol_section:
                parent = vol_section.find_parent()
                if parent:
                    text = parent.get_text()
                    hours_match = re.search(r'(\d+)\s*hour', text, re.I)
                    if hours_match:
                        try:
                            unit_data['nominal_hours'] = int(hours_match.group(1))
                        except:
                            pass
            
            # Prerequisites
            prereq_section = soup.find('h2', string=re.compile(r'Prerequisite', re.I))
            if not prereq_section:
                prereq_section = soup.find('h3', string=re.compile(r'Prerequisite', re.I))
            
            if prereq_section:
                prereq_text = ''
                for sibling in prereq_section.find_next_siblings():
                    if sibling.name in ['h2', 'h3']:
                        break
                    prereq_text += sibling.get_text()
                
                prereq_codes = re.findall(r'[A-Z]{3,10}\d{3,6}[A-Z]?', prereq_text)
                unit_data['prerequisites'] = prereq_codes
            
            logger.info(f"✓ Web scraped {code}")
            return unit_data
            
        except Exception as e:
            logger.debug(f"Web scraping failed for {code}: {e}")
            return None
    
    def _get_basic_unit_info(self, code):
        """Fallback: basic info from API"""
        try:
            request = {'Code': code, 'IncludeLegacyData': False}
            response = self.client.service.GetDetails(request)
            
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
    
    def download_all_qualifications(self, output_dir='qualifications', delay=1):
        """Download all qualifications with units"""
        os.makedirs(output_dir, exist_ok=True)
        
        qualifications = self.search_all_qualifications()
        
        if not qualifications:
            logger.error("No qualifications found")
            return
        
        successful = 0
        failed = []
        training_package_stats = {}
        
        for i, qual in enumerate(qualifications, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing {i}/{len(qualifications)}: {qual['code']}")
            logger.info(f"{'='*80}")
            
            try:
                qual_data = self.get_qualification_with_units(qual['code'])
                
                if qual_data:
                    training_package = qual_data.get('training_package', 'Unknown')
                    
                    if training_package == 'Unknown':
                        training_package = self._extract_training_package_code(qual['code'])
                        qual_data['training_package'] = training_package
                    
                    package_dir = os.path.join(output_dir, training_package)
                    os.makedirs(package_dir, exist_ok=True)
                    
                    filename = os.path.join(package_dir, f"{qual['code']}.json")
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(qual_data, f, indent=2, ensure_ascii=False)
                    
                    if training_package not in training_package_stats:
                        training_package_stats[training_package] = {
                            'total': 0,
                            'current': 0,
                            'superseded': 0
                        }
                    
                    training_package_stats[training_package]['total'] += 1
                    if qual_data['status'] == 'current':
                        training_package_stats[training_package]['current'] += 1
                    else:
                        training_package_stats[training_package]['superseded'] += 1
                    
                    logger.info(f"✓ Saved: {qual['code']}.json")
                    logger.info(f"  Status: {qual_data['status']}, Units: {len(qual_data['units'])}")
                    logger.info(f"  Methods: XML={self.xml_success}, Web={self.web_scrape_success}, API={self.api_fallback}")
                    successful += 1
                else:
                    logger.warning(f"✗ Failed: {qual['code']}")
                    failed.append(qual['code'])
                
            except Exception as e:
                logger.error(f"✗ Error: {qual['code']}: {e}")
                failed.append(qual['code'])
            
            time.sleep(delay)
        
        self._generate_summary_report(
            output_dir, 
            len(qualifications), 
            successful, 
            failed, 
            training_package_stats
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ DOWNLOAD COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Files saved to: {output_dir}/")
        logger.info(f"Method stats: XML={self.xml_success}, Web={self.web_scrape_success}, API={self.api_fallback}")
        logger.info("=" * 80)
    
    def _generate_summary_report(self, output_dir, total, successful, failed, training_package_stats):
        """Generate summary report"""
        summary = {
            'download_date': datetime.now().isoformat(),
            'total_qualifications': total,
            'successful_downloads': successful,
            'failed_downloads': len(failed),
            'failed_codes': failed,
            'method_stats': {
                'xml_downloads': self.xml_success,
                'web_scraping': self.web_scrape_success,
                'api_fallback': self.api_fallback
            },
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
        
        with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        if failed:
            with open(os.path.join(output_dir, '_failed_qualifications.txt'), 'w') as f:
                f.write('\n'.join(failed))
        
        logger.info("\n" + "=" * 80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total: {total}")
        logger.info(f"Success: {successful}")
        logger.info(f"Failed: {len(failed)}")
        
        logger.info("\nTraining Packages:")
        logger.info("-" * 80)
        logger.info(f"{'Package':<15} {'Total':<10} {'Current':<10} {'Superseded':<10}")
        logger.info("-" * 80)
        
        for item in sorted(summary['training_package_summary'], key=lambda x: x['total'], reverse=True):
            logger.info(f"{item['code']:<15} {item['total']:<10} {item['current']:<10} {item['superseded']:<10}")
        
        if failed:
            logger.info(f"\n⚠️  Failed: {', '.join(failed[:10])}")
            if len(failed) > 10:
                logger.info(f"... and {len(failed)-10} more")


def main():
    """Main execution"""
    print("=" * 80)
    print("Training.gov.au - Qualification Downloader (Hybrid)")
    print("Tries XML download first, falls back to web scraping")
    print("=" * 80)
    
    username = input("Enter your API username: ")
    password = input("Enter your API password: ")
    environment = "y"# input("Use sandbox? (y/n): ").lower()
    
    use_sandbox = environment == 'y'
    
    print(f"\nConnecting to {'SANDBOX' if use_sandbox else 'PRODUCTION'}...")
    print("Method priority: 1) XML download, 2) Web scraping, 3) API basic")
    
    try:
        downloader = TrainingGovDownloader(username, password, use_sandbox)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'qualifications_{timestamp}'
        
        print(f"\nOutput: {output_dir}/")
        print("Organized by training package")
        print("\nStarting download...")
        print("⚠️  This will take several hours!")
        print("-" * 80)
        
        downloader.download_all_qualifications(output_dir=output_dir, delay=1)
        
        print(f"\n✓ Complete! Check '{output_dir}' folder")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted - partial data saved")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
