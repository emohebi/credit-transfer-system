from bs4 import BeautifulSoup
import json
import re
from pathlib import Path

def extract_course_info(html_file_path):
    """
    Extract course information from HTML file and return as JSON format
    """
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize the result dictionary
    result = {
        "code": None,
        "name": None,
        "description": None,
        "study_level": None,
        "learning_outcomes": [],
        "prerequisites": [],
        "credit_points": None,
        "topics": [],
        "assessment": None
    }
    
    # Extract code and name from title
    title = soup.find('title')
    if title:
        title_text = title.text.strip()
        # Extract code from title - pattern: "Name (Code)"
        match = re.search(r'\((\d+)\)', title_text)
        if match:
            result["code"] = match.group(1)
        # Extract name - everything before the parenthesis
        name_match = re.search(r'^(.+?)\s*\(', title_text)
        if name_match:
            result["name"] = name_match.group(1).strip()
    
    # Look for course information in the main content
    unit_details = soup.find_all('div', class_='unit-details')
    
    for detail in unit_details:
        text_content = detail.get_text(separator='\n', strip=True)
        
        # Extract description - content between Introduction and Learning outcomes
        intro_start_idx = text_content.find('Introduction')
        learning_outcomes_idx = text_content.find('Learning outcomes')
        
        if intro_start_idx != -1 and learning_outcomes_idx != -1 and learning_outcomes_idx > intro_start_idx:
            # Extract content between these two headers
            description_text = text_content[intro_start_idx + len('Introduction'):learning_outcomes_idx].strip()
            
            # Clean up the extracted text
            lines = description_text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Skip empty lines and lines that look like headers
                if line and not line.endswith(':') and len(line) > 10:
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                result["description"] = ' '.join(cleaned_lines)
        
        # Fallback if Introduction header not found but Learning outcomes exists
        elif learning_outcomes_idx != -1:
            # Take substantial content before Learning outcomes
            intro_text = text_content[:learning_outcomes_idx].strip()
            lines = intro_text.split('\n')
            desc_lines = []
            
            # Start collecting after we pass metadata/headers
            start_collecting = False
            for line in lines:
                line = line.strip()
                # Start collecting after we see substantial content
                if not start_collecting and len(line) > 50:
                    start_collecting = True
                
                if start_collecting and line and not line.endswith(':'):
                    desc_lines.append(line)
            
            if desc_lines:
                result["description"] = ' '.join(desc_lines)
        
        # Extract learning outcomes
        if 'Learning outcomes' in text_content:
            outcomes_start = text_content.find('Learning outcomes')
            outcomes_text = text_content[outcomes_start:]
            # Look for numbered outcomes
            outcome_matches = re.findall(r'\d+\.\s*([^;]+?)(?:;|$|\n\d+\.|\nGraduate)', outcomes_text)
            result["learning_outcomes"] = [outcome.strip() for outcome in outcome_matches if outcome.strip()]
        
        # Extract prerequisites
        if 'Prerequisites' in text_content:
            prereq_start = text_content.find('Prerequisites')
            prereq_end = text_content.find('Corequisites', prereq_start) if 'Corequisites' in text_content[prereq_start:] else prereq_start + 100
            prereq_text = text_content[prereq_start:prereq_end]
            if 'None' in prereq_text:
                result["prerequisites"] = []
            else:
                # Extract any course codes mentioned
                prereq_codes = re.findall(r'\b\d{4,5}\b', prereq_text)
                result["prerequisites"] = prereq_codes
    
    # Extract credit points from table
    tables = soup.find_all('table')
    for table in tables:
        # Look for credit points in table cells
        tds = table.find_all('td')
        for i, td in enumerate(tds):
            td_text = td.get_text(strip=True)
            # Credit points are typically single digit numbers in specific context
            if i > 0 and tds[i-1].get_text(strip=True) == '0.125':  # EFTSL value before credit points
                try:
                    result["credit_points"] = int(td_text)
                except:
                    pass
    
    # Extract study level
    for table in tables:
        cells = table.find_all('td')
        for cell in cells:
            cell_text = cell.get_text(strip=True)
            if 'Level 1 - Undergraduate Introductory' in cell_text:
                result["study_level"] = "introductory"
            elif 'Level 2' in cell_text or 'Intermediate' in cell_text:
                result["study_level"] = "intermediate"
            elif 'Level 3' in cell_text or 'Advanced' in cell_text:
                result["study_level"] = "advanced"
    
    # Extract assessment information
    assessment_section = soup.find(text=re.compile(r'Assessment requirements|Submission of assessment'))
    if assessment_section:
        parent = assessment_section.find_parent()
        if parent:
            assessment_text = parent.get_text(separator=' ', strip=True)
            # Extract the assessment description
            if 'To pass the unit' in assessment_text:
                assess_start = assessment_text.find('To pass the unit')
                assess_end = assessment_text.find('Use of AI', assess_start) if 'Use of AI' in assessment_text else len(assessment_text)
                result["assessment"] = assessment_text[assess_start:assess_end].strip()
    
    # Extract topics from module activities or course content
    # Since specific topics aren't clearly listed, we can infer from the description
    if result["description"]:
        desc_lower = result["description"].lower()
        topics = []
        if 'financial' in desc_lower or 'accounting' in desc_lower:
            topics.append("Financial Analysis")
        if 'decision' in desc_lower:
            topics.append("Business Decision Making")
        if 'budget' in desc_lower:
            topics.append("Budgeting")
        if 'cost' in desc_lower:
            topics.append("Cost Analysis")
        if 'spreadsheet' in desc_lower or 'excel' in desc_lower:
            topics.append("Spreadsheet Modeling")
        if 'information systems' in desc_lower or 'data' in desc_lower:
            topics.append("Information Systems")
        result["topics"] = topics
    
    return result


def main():
    # Replace with your actual file path
    html_file_path = "/home/ehsan/Downloads/Business Decision Making (11009) - University of Canberra.html"
    qual = {
        "code": "364JA",
        "name": "Bachelor of Nursing",
        "courses": []
        }
    parent_dir = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/NST/MiniProjOct25/data"
    dir_ = Path(parent_dir) / "raw/364JA Bachelor of Nursing/"
    files = [str(f) for f in dir_.glob("*.html")]
    from tqdm import tqdm
    try:
        for html_file_path in tqdm(files):
            course_info = extract_course_info(html_file_path)
            qual["courses"].append(course_info)
        # Output as formatted JSON
        # json_output = json.dumps(course_info, indent=2, ensure_ascii=False)
        # print(json_output)
        
        # Optionally save to file
        output_path = Path(parent_dir) / f"{qual['code']}_{qual['name'].replace(' ', '_')}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qual, f, indent=2, ensure_ascii=False)
        
        print(f"\nJSON output saved to {output_path}")
        
    except FileNotFoundError:
        print(f"Error: File '{html_file_path}' not found.")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
