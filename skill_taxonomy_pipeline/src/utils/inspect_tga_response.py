"""
TGA API Response Inspector
Run this locally to see the FULL structure of the API response
This will help us find where ANZSCO data is stored
"""

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object
import json
from datetime import datetime

# Credentials
USERNAME = "WebService.Read"
PASSWORD = "Asdf098"
USE_SANDBOX = True

def recursive_dict_print(d, indent=0, max_depth=10):
    """Recursively print dictionary with all fields"""
    if indent > max_depth:
        return
    
    prefix = "  " * indent
    
    if isinstance(d, dict):
        for key, value in d.items():
            if value is None:
                print(f"{prefix}{key}: null")
            elif isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                recursive_dict_print(value, indent + 1, max_depth)
            else:
                val_str = str(value)
                if len(val_str) > 200:
                    val_str = val_str[:200] + "..."
                print(f"{prefix}{key}: {val_str}")
    elif isinstance(d, list):
        if len(d) == 0:
            print(f"{prefix}(empty list)")
        for i, item in enumerate(d[:5]):  # Show first 5 items
            print(f"{prefix}[{i}]:")
            recursive_dict_print(item, indent + 1, max_depth)
        if len(d) > 5:
            print(f"{prefix}... ({len(d) - 5} more items)")
    else:
        print(f"{prefix}{d}")


def find_anzsco_patterns(data, path=""):
    """Search for ANZSCO-related fields anywhere in the response"""
    anzsco_keywords = ['anzsco', 'occupation', 'classification', 'asced', 'mapping', 'industry']
    findings = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if key contains ANZSCO-related terms
            key_lower = key.lower()
            for keyword in anzsco_keywords:
                if keyword in key_lower:
                    findings.append({
                        'path': current_path,
                        'key': key,
                        'value': value,
                        'type': type(value).__name__
                    })
            
            # Recurse
            if isinstance(value, (dict, list)):
                findings.extend(find_anzsco_patterns(value, current_path))
                
    elif isinstance(data, list):
        for i, item in enumerate(data[:10]):  # Check first 10 items
            current_path = f"{path}[{i}]"
            if isinstance(item, (dict, list)):
                findings.extend(find_anzsco_patterns(item, current_path))
    
    return findings


def main():
    print("="*80)
    print("TGA API RESPONSE INSPECTOR")
    print("="*80)
    
    wsse = UsernameToken(USERNAME, PASSWORD)
    base_url = "https://ws.sandbox.training.gov.au" if USE_SANDBOX else "https://ws.training.gov.au"
    training_service_url = f"{base_url}/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
    
    print(f"\nConnecting to: {training_service_url}")
    client = Client(training_service_url, wsse=wsse)
    
    # List all available service operations
    print("\n" + "-"*80)
    print("AVAILABLE API OPERATIONS:")
    print("-"*80)
    
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            for operation in port.binding._operations.values():
                print(f"  - {operation.name}")
    
    # Test with multiple qualification codes
    test_codes = ['ICT50220', 'BSB50120', 'CHC30121', 'SIT40521', 'CPC30220']
    
    all_findings = []
    
    for code in test_codes:
        print(f"\n{'='*80}")
        print(f"INSPECTING: {code}")
        print("="*80)
        
        try:
            # Try with different request parameters
            request = {
                'Code': code, 
                'IncludeLegacyData': True,  # Try including legacy data
            }
            response = client.service.GetDetails(request)
            
            if response:
                response_dict = serialize_object(response)
                
                # Save full response
                filename = f'full_response_{code}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(response_dict, f, indent=2, default=str)
                print(f"\nFull response saved to: {filename}")
                
                # Print all top-level fields
                print(f"\nTOP-LEVEL FIELDS for {code}:")
                print("-"*60)
                for key in response_dict.keys():
                    value = response_dict[key]
                    if value is None:
                        print(f"  {key}: null")
                    elif isinstance(value, dict):
                        print(f"  {key}: <dict with {len(value)} keys>")
                    elif isinstance(value, list):
                        print(f"  {key}: <list with {len(value)} items>")
                    else:
                        val_str = str(value)[:80]
                        print(f"  {key}: {val_str}")
                
                # Search for ANZSCO-related fields
                print(f"\nSEARCHING FOR ANZSCO/CLASSIFICATION FIELDS:")
                print("-"*60)
                findings = find_anzsco_patterns(response_dict)
                
                if findings:
                    for f in findings:
                        print(f"\n  Found: {f['path']}")
                        print(f"    Key: {f['key']}")
                        print(f"    Type: {f['type']}")
                        if f['value'] is not None:
                            val_str = str(f['value'])[:200]
                            print(f"    Value: {val_str}")
                    all_findings.extend(findings)
                else:
                    print("  No ANZSCO-related fields found in standard locations")
                
                # Check specific fields that might contain ANZSCO
                fields_to_check = [
                    'Classifications', 'Classification', 
                    'Mappings', 'Mapping',
                    'OccupationOutcomes', 'Occupations',
                    'IndustryAreas', 'Industries',
                    'Releases', 'MappingInformation',
                    'UsageRecommendation', 'ReplacedBy'
                ]
                
                print(f"\nCHECKING SPECIFIC FIELDS:")
                print("-"*60)
                for field in fields_to_check:
                    if field in response_dict:
                        value = response_dict[field]
                        print(f"\n  {field}:")
                        if value is not None:
                            recursive_dict_print(value, indent=2, max_depth=4)
                        else:
                            print("    null")
                
                # Only do detailed inspection for first qualification
                if code == test_codes[0]:
                    print(f"\n\nFULL RESPONSE STRUCTURE for {code}:")
                    print("-"*60)
                    recursive_dict_print(response_dict, max_depth=6)
                    
        except Exception as e:
            print(f"Error getting {code}: {e}")
            import traceback
            traceback.print_exc()
    
    # Try the Classification Service
    print("\n\n" + "="*80)
    print("TRYING CLASSIFICATION SERVICE")
    print("="*80)
    
    try:
        class_service_url = f"{base_url}/Deewr.Tga.WebServices/ClassificationService.svc?wsdl"
        print(f"\nConnecting to: {class_service_url}")
        class_client = Client(class_service_url, wsse=wsse)
        
        print("\nClassification Service Operations:")
        for service in class_client.wsdl.services.values():
            for port in service.ports.values():
                for operation in port.binding._operations.values():
                    print(f"  - {operation.name}")
        
        # Try to call classification methods
        for code in test_codes[:2]:
            print(f"\nTrying to get classification for {code}...")
            
            # Try different method signatures
            methods_to_try = [
                ('GetAllClassifications', {}),
                ('GetClassifications', {'TrainingComponentCode': code}),
                ('GetClassifications', {'Code': code}),
                ('Search', {'Query': code}),
            ]
            
            for method_name, params in methods_to_try:
                if hasattr(class_client.service, method_name):
                    try:
                        print(f"  Calling {method_name}({params})...")
                        method = getattr(class_client.service, method_name)
                        result = method(**params) if params else method()
                        if result:
                            result_dict = serialize_object(result)
                            print(f"  SUCCESS! Result:")
                            recursive_dict_print(result_dict, indent=2, max_depth=4)
                            
                            # Save result
                            with open(f'classification_{code}_{method_name}.json', 'w') as f:
                                json.dump(result_dict, f, indent=2, default=str)
                    except Exception as e:
                        print(f"  {method_name} failed: {e}")
                        
    except Exception as e:
        print(f"Classification Service error: {e}")
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY OF FINDINGS")
    print("="*80)
    
    if all_findings:
        print("\nFields containing ANZSCO/occupation/classification keywords:")
        unique_paths = set(f['path'].split('[')[0] for f in all_findings)
        for path in sorted(unique_paths):
            print(f"  - {path}")
    else:
        print("\nNo ANZSCO-related fields found in the API response.")
        print("\nThis suggests ANZSCO data may be:")
        print("  1. In a separate Classification Service endpoint")
        print("  2. Only available on the TGA website (not via API)")
        print("  3. Published separately by NCVER as reference files")
    
    print("\n\nGenerated files:")
    print("  - full_response_*.json - Complete API responses")
    print("  - classification_*.json - Classification service results (if any)")
    print("\nPlease share the full_response_ICT50220.json file content so we can")
    print("identify exactly what fields are available.")


if __name__ == "__main__":
    main()
