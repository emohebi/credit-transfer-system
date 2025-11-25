import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Optional


class AuthorITParser:
    """
    Parser for AuthorIT XML format used by training.gov.au
    """
    
    def __init__(self, xml_content: bytes):
        """
        Initialize parser with XML content
        
        Args:
            xml_content: Raw XML bytes
        """
        # Remove BOM if present
        if xml_content.startswith(b'\xef\xbb\xbf'):
            xml_content = xml_content[3:]
        
        self.root = ET.fromstring(xml_content)
        self.ns = {'': 'http://www.authorit.com/xml/authorit'}
        
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace"""
        if not text:
            return ""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_text_from_element(self, element) -> str:
        """
        Recursively extract text from an element and its children
        """
        texts = []
        
        # Get direct text
        if element.text:
            texts.append(element.text)
        
        # Process children
        for child in element:
            texts.append(self._extract_text_from_element(child))
            if child.tail:
                texts.append(child.tail)
        
        return ''.join(texts)
    
    def _extract_paragraph_text(self, p_element) -> str:
        """Extract text from a paragraph element, handling nested tags"""
        return self._clean_text(self._extract_text_from_element(p_element))
    
    def _find_topic_by_description(self, description: str) -> Optional[ET.Element]:
        """
        Find a Topic element by its description
        """
        for topic in self.root.findall('.//Topic', self.ns):
            obj = topic.find('.//Object', self.ns)
            if obj is not None:
                desc = obj.find('Description', self.ns)
                if desc is not None and description.lower() in desc.text.lower():
                    return topic
        return None
    
    def _extract_list_items(self, text_element, list_id: str = "13") -> List[str]:
        """
        Extract list items (bullet points) from text element
        List items are typically in <p id="13"> or <p id="14"> tags
        """
        items = []
        
        for p in text_element.findall('.//p', self.ns):
            p_id = p.get('id', '')
            if p_id in [list_id, "14"]:  # 13 is main bullet, 14 is sub-bullet
                text = self._extract_paragraph_text(p)
                if text:
                    items.append(text)
        
        return items
    
    def _extract_table_as_text(self, table_element) -> str:
        """
        Extract table content as formatted text
        """
        lines = []
        
        for tr in table_element.findall('.//tr', self.ns):
            row_cells = []
            for td in tr.findall('.//td', self.ns):
                # Extract all paragraphs in the cell
                cell_texts = []
                for p in td.findall('.//p', self.ns):
                    text = self._extract_paragraph_text(p)
                    if text:
                        cell_texts.append(text)
                
                if cell_texts:
                    row_cells.append(' | '.join(cell_texts))
            
            if row_cells:
                lines.append(' | '.join(row_cells))
        
        return '\n'.join(lines)
    
    def get_unit_code_and_title(self) -> tuple[str, str]:
        """
        Extract unit code and title from the XML
        """
        # Look for the main unit Book (not templates)
        for book in self.root.findall('.//Book', self.ns):
            obj = book.find('.//Object', self.ns)
            if obj is not None:
                # Check if it's not a template
                is_template = obj.find('IsTemplate', self.ns)
                if is_template is not None and is_template.text == 'false':
                    # Get code and title from VariableAssignments
                    var_assignments = book.find('.//VariableAssignments', self.ns)
                    if var_assignments is not None:
                        code = None
                        title = None
                        
                        for var in var_assignments.findall('.//VariableAssignment', self.ns):
                            name = var.find('Name', self.ns)
                            value = var.find('Value', self.ns)
                            
                            if name is not None and value is not None:
                                if name.text == 'Code':
                                    code = value.text
                                elif name.text == 'Title':
                                    title = value.text
                        
                        if code and title:
                            return code, title
        
        return "", ""
    
    def extract_application(self) -> str:
        """
        Extract Application section
        """
        topic = self._find_topic_by_description("Application")
        if topic is None:
            return ""
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return ""
        
        paragraphs = []
        for p in text_element.findall('.//p', self.ns):
            text = self._extract_paragraph_text(p)
            if text:
                paragraphs.append(text)
        
        return '\n\n'.join(paragraphs)
    
    def extract_elements_and_performance_criteria(self) -> str:
        """
        Extract Elements and Performance Criteria section
        Usually in a table format
        """
        topic = self._find_topic_by_description("Elements and Performance Criteria")
        if topic is None:
            return ""
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return ""
        
        # Look for table
        table = text_element.find('.//table', self.ns)
        if table is not None:
            return self._extract_table_as_text(table)
        
        # Fallback: extract paragraphs
        paragraphs = []
        for p in text_element.findall('.//p', self.ns):
            text = self._extract_paragraph_text(p)
            if text:
                paragraphs.append(text)
        
        return '\n\n'.join(paragraphs)
    
    def extract_foundation_skills(self) -> str:
        """
        Extract Foundation Skills section
        """
        topic = self._find_topic_by_description("Foundation Skills")
        if topic is None:
            return ""
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return ""
        
        # Check for table first
        table = text_element.find('.//table', self.ns)
        if table is not None:
            return self._extract_table_as_text(table)
        
        # Extract paragraphs
        paragraphs = []
        for p in text_element.findall('.//p', self.ns):
            text = self._extract_paragraph_text(p)
            if text:
                paragraphs.append(text)
        
        return '\n\n'.join(paragraphs)
    
    def extract_knowledge_evidence(self) -> List[str]:
        """
        Extract Knowledge Evidence as a list of items
        """
        topic = self._find_topic_by_description("Knowledge Evidence")
        if topic is None:
            return []
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return []
        
        return self._extract_list_items(text_element)
    
    def extract_performance_evidence(self) -> str:
        """
        Extract Performance Evidence section
        """
        topic = self._find_topic_by_description("Performance Evidence")
        if topic is None:
            return ""
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return ""
        
        # Extract all list items
        items = self._extract_list_items(text_element)
        
        return '\n'.join(items)
    
    def extract_assessment_conditions(self) -> str:
        """
        Extract Assessment Conditions section
        """
        topic = self._find_topic_by_description("Assessment Conditions")
        if topic is None:
            return ""
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return ""
        
        # Extract all items
        items = self._extract_list_items(text_element)
        
        # Also get regular paragraphs
        paragraphs = []
        for p in text_element.findall('.//p', self.ns):
            p_id = p.get('id', '')
            if p_id == "4":  # Regular paragraphs
                text = self._extract_paragraph_text(p)
                if text:
                    paragraphs.append(text)
        
        all_content = paragraphs + items
        return '\n\n'.join(all_content)
    
    def extract_prerequisites(self) -> List[str]:
        """
        Extract prerequisites/pre-requisite units
        """
        topic = self._find_topic_by_description("Pre-requisite")
        if topic is None:
            return []
        
        text_element = topic.find('.//Text', self.ns)
        if text_element is None:
            return []
        
        # Extract all text
        full_text = ""
        for p in text_element.findall('.//p', self.ns):
            text = self._extract_paragraph_text(p)
            if text:
                full_text += " " + text
        
        # Extract unit codes (pattern: 3-10 letters followed by 3-6 digits, optionally followed by letters)
        prereq_codes = re.findall(r'[A-Z]{3,10}\d{3,6}[A-Z]?', full_text)
        
        return prereq_codes
    
    def extract_volume_of_learning(self) -> Optional[int]:
        """
        Extract volume of learning (nominal hours)
        Note: This might not be in a separate topic, might be in assessment conditions
        """
        # Try to find it in any topic
        for topic in self.root.findall('.//Topic', self.ns):
            text_element = topic.find('.//Text', self.ns)
            if text_element is not None:
                full_text = ""
                for p in text_element.findall('.//p', self.ns):
                    text = self._extract_paragraph_text(p)
                    full_text += " " + text
                
                # Look for volume of learning mention
                if 'volume of learning' in full_text.lower():
                    # Try to extract hours
                    hours_match = re.search(r'(\d+)\s*hour', full_text, re.I)
                    if hours_match:
                        try:
                            return int(hours_match.group(1))
                        except:
                            pass
        
        return None
    
    def parse_unit(self) -> Dict:
        """
        Parse the complete unit and return structured data
        """
        code, title = self.get_unit_code_and_title()
        
        # Build description from multiple sections
        description_parts = []
        
        application = self.extract_application()
        if application:
            description_parts.append(f"Application:\n{application}")
        
        elements = self.extract_elements_and_performance_criteria()
        if elements:
            description_parts.append(f"\n\nElements and Performance Criteria:\n{elements}")
        
        foundation = self.extract_foundation_skills()
        if foundation:
            description_parts.append(f"\n\nFoundation Skills:\n{foundation}")
        
        unit_data = {
            'code': code,
            'name': title,
            'description': '\n'.join(description_parts) if description_parts else 'Content not available',
            'learning_outcomes': self.extract_knowledge_evidence(),
            'assessment_requirements': self.extract_performance_evidence(),
            'nominal_hours': self.extract_volume_of_learning(),
            'prerequisites': self.extract_prerequisites()
        }
        
        # Add assessment conditions to assessment requirements
        assessment_conditions = self.extract_assessment_conditions()
        if assessment_conditions:
            if unit_data['assessment_requirements']:
                unit_data['assessment_requirements'] += f"\n\nAssessment Conditions:\n{assessment_conditions}"
            else:
                unit_data['assessment_requirements'] = f"Assessment Conditions:\n{assessment_conditions}"
        
        return unit_data


def parse_authorit_xml_file(filepath: str) -> Dict:
    """
    Parse an AuthorIT XML file and return unit data
    
    Args:
        filepath: Path to the XML file
        
    Returns:
        Dictionary containing unit data
    """
    with open(filepath, 'rb') as f:
        xml_content = f.read()
    
    parser = AuthorITParser(xml_content)
    return parser.parse_unit()


def parse_authorit_xml_bytes(xml_bytes: bytes) -> Dict:
    """
    Parse AuthorIT XML from bytes and return unit data
    
    Args:
        xml_bytes: Raw XML bytes
        
    Returns:
        Dictionary containing unit data
    """
    parser = AuthorITParser(xml_bytes)
    return parser.parse_unit()


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python authorit_parser.py <xml_file>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    
    print(f"Parsing {xml_file}...")
    unit_data = parse_authorit_xml_file(xml_file)
    
    print("\n" + "="*80)
    print(f"Unit Code: {unit_data['code']}")
    print(f"Unit Name: {unit_data['name']}")
    print("="*80)
    
    print("\nDESCRIPTION:")
    print(unit_data['description'][:500] + "..." if len(unit_data['description']) > 500 else unit_data['description'])
    
    print(f"\n\nLEARNING OUTCOMES ({len(unit_data['learning_outcomes'])} items):")
    for i, outcome in enumerate(unit_data['learning_outcomes'][:5], 1):
        print(f"  {i}. {outcome[:100]}{'...' if len(outcome) > 100 else ''}")
    if len(unit_data['learning_outcomes']) > 5:
        print(f"  ... and {len(unit_data['learning_outcomes']) - 5} more")
    
    print("\n\nASSESSMENT REQUIREMENTS:")
    print(unit_data['assessment_requirements'][:500] + "..." if len(unit_data['assessment_requirements']) > 500 else unit_data['assessment_requirements'])
    
    print(f"\n\nNOMINAL HOURS: {unit_data['nominal_hours']}")
    print(f"PREREQUISITES: {unit_data['prerequisites']}")
    
    print("\n" + "="*80)
    print("✓ Parsing complete!")
