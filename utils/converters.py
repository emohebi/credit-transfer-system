import re
import json

class JSONExtraction:
    
    @classmethod
    def extract_json_from_text(self, text):
        """
        Extract JSON array from text, preferably after 'assistantfinal' term if present.
        
        Args:
            text: Input text containing JSON
        
        Returns:
            Parsed JSON object or None if not found
        """
        
        # First try to find JSON after 'assistantfinal'
        after_assistant_pattern = r'assistantfinal.*?(\s*\{.*\}\s*)'
        match = re.search(after_assistant_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # If 'assistantfinal' not found or no JSON after it, 
            # find any JSON array in the text
            general_pattern = r'(\s*\{.*\}\s*)'
            match = re.search(general_pattern, text, re.DOTALL)
            
            if match:
                json_str = match.group(1)
            else:
                return None
        
        # Try to parse the extracted string as JSON
        try:
            return json_str
        except json.JSONDecodeError:
            # If simple pattern fails, try more robust extraction
            return None

    def extract_json_robust(self, text):
        """
        More robust JSON extraction using bracket counting.
        """
        # Find all potential JSON array start positions
        potential_starts = []
        
        # Check after 'assistantfinal' first
        assistant_pos = text.find('assistantfinal')
        if assistant_pos != -1:
            # Start searching after 'assistantfinal'
            search_text = text[assistant_pos:]
            offset = assistant_pos
        else:
            search_text = text
            offset = 0
        
        # Find the first '[' that likely starts a JSON array
        start_pos = search_text.find('[')
        if start_pos == -1:
            return None
        
        # Count brackets to find matching closing bracket
        bracket_count = 0
        in_string = False
        escape_next = False
        end_pos = -1
        
        for i in range(start_pos, len(search_text)):
            char = search_text[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i
                        break
        
        if end_pos != -1:
            json_str = search_text[start_pos:end_pos + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        
        return None

    # Alternative simpler regex-based approach
    def extract_json_simple(self, text):
        """
        Simpler regex approach that works for non-nested JSON arrays.
        """
        # Pattern explanation:
        # (?:assistantfinal.*?)? - optionally match 'assistantfinal' and any chars (non-greedy)
        # (\[         - match opening bracket
        # \s*         - optional whitespace
        # \{          - opening brace for first object
        # [^[\]]*     - any chars except brackets (simplified for non-nested)
        # \}          - closing brace
        # (?:\s*,\s*\{[^[\]]*\})*  - zero or more additional objects
        # \s*         - optional whitespace
        # \])         - closing bracket
        
        pattern = r'(?:assistantfinal.*?)?(\[\s*\{[^[\]]*\}(?:\s*,\s*\{[^[\]]*\})*\s*\])'
        
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None