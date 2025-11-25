"""
Enhanced custom JSON encoder for model objects with deep serialization
"""

import json
from typing import Any, Dict, List
from datetime import datetime, date
from enum import Enum
from dataclasses import dataclass, is_dataclass, asdict
from pathlib import Path


class ModelJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles dataclasses, enums, and other types"""
    
    def default(self, obj: Any) -> Any:
        # Handle dataclasses
        if is_dataclass(obj):
            # Recursively handle nested dataclasses
            return self._serialize_dataclass(obj)
        
        # Handle Enums
        if isinstance(obj, Enum):
            return obj.value
        
        # Handle datetime objects
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle Path objects
        if isinstance(obj, Path):
            return str(obj)
        
        # Handle sets
        if isinstance(obj, set):
            return list(obj)
        
        # Handle numpy types
        try:
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        
        # Let the base class handle other types
        return super().default(obj)
    
    def _serialize_dataclass(self, obj) -> Dict:
        """Serialize a dataclass object"""
        result = {"_type": obj.__class__.__name__}
        
        for field_name, field_value in asdict(obj).items():
            # Handle special field types
            if isinstance(field_value, Enum):
                result[field_name] = field_value.value
            elif isinstance(field_value, (datetime, date)):
                result[field_name] = field_value.isoformat()
            elif isinstance(field_value, Path):
                result[field_name] = str(field_value)
            else:
                result[field_name] = field_value
        
        return result
    
    def encode(self, o: Any) -> str:
        """Override encode to handle nested structures"""
        # First, recursively process the object to handle nested dataclasses
        processed = self._deep_process(o)
        # Then use the standard encoding
        return super().encode(processed)
    
    def _deep_process(self, obj: Any) -> Any:
        """Recursively process objects to prepare for JSON encoding"""
        
        # Handle dataclasses
        if is_dataclass(obj):
            return self._serialize_dataclass(obj)
        
        # Handle dictionaries - recursively process values
        elif isinstance(obj, dict):
            return {key: self._deep_process(value) for key, value in obj.items()}
        
        # Handle lists and tuples - recursively process elements
        elif isinstance(obj, (list, tuple)):
            processed = [self._deep_process(item) for item in obj]
            return processed if isinstance(obj, list) else tuple(processed)
        
        # Handle sets
        elif isinstance(obj, set):
            return [self._deep_process(item) for item in obj]
        
        # Handle Enums
        elif isinstance(obj, Enum):
            return obj.value
        
        # Handle datetime objects
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle Path objects
        elif isinstance(obj, Path):
            return str(obj)
        
        # Handle numpy types
        try:
            import numpy as np
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        
        # Return as-is for native JSON types
        return obj


class ModelJSONDecoder(json.JSONDecoder):
    """Custom JSON decoder that reconstructs dataclass objects"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj: dict) -> Any:
        """Hook to convert dictionaries back to dataclass instances"""
        
        # Check if this is a serialized dataclass
        if "_type" in obj:
            class_name = obj.pop("_type")
            
            # Import the appropriate class based on the type
            if class_name == "Skill":
                from models.base_models import Skill
                from models.enums import SkillLevel, SkillCategory, SkillContext
                
                # Convert enum strings/values back to enums
                if "level" in obj:
                    if isinstance(obj["level"], (str, int)):
                        try:
                            obj["level"] = SkillLevel(obj["level"])
                        except (ValueError, KeyError):
                            # Handle if value doesn't match enum
                            obj["level"] = SkillLevel.COMPETENT
                
                if "category" in obj:
                    if isinstance(obj["category"], str):
                        try:
                            obj["category"] = SkillCategory(obj["category"])
                        except (ValueError, KeyError):
                            obj["category"] = SkillCategory.TECHNICAL
                
                if "context" in obj:
                    if isinstance(obj["context"], str):
                        try:
                            obj["context"] = SkillContext(obj["context"])
                        except (ValueError, KeyError):
                            obj["context"] = SkillContext.HYBRID
                
                return Skill(**obj)
            
            elif class_name == "UnitOfCompetency":
                from models.base_models import UnitOfCompetency, Skill
                
                # Recursively handle extracted_skills
                if "extracted_skills" in obj:
                    skills = []
                    for skill_data in obj["extracted_skills"]:
                        if isinstance(skill_data, dict) and "_type" in skill_data:
                            skills.append(self.object_hook(skill_data))
                        elif isinstance(skill_data, Skill):
                            skills.append(skill_data)
                        else:
                            # Try to create Skill from dict
                            skills.append(self.object_hook({**skill_data, "_type": "Skill"}))
                    obj["extracted_skills"] = skills
                
                return UnitOfCompetency(**obj)
            
            elif class_name == "UniCourse":
                from models.base_models import UniCourse, Skill
                
                # Recursively handle extracted_skills
                if "extracted_skills" in obj:
                    skills = []
                    for skill_data in obj["extracted_skills"]:
                        if isinstance(skill_data, dict) and "_type" in skill_data:
                            skills.append(self.object_hook(skill_data))
                        elif isinstance(skill_data, Skill):
                            skills.append(skill_data)
                        else:
                            # Try to create Skill from dict
                            skills.append(self.object_hook({**skill_data, "_type": "Skill"}))
                    obj["extracted_skills"] = skills
                
                return UniCourse(**obj)
            
            elif class_name == "VETQualification":
                from models.base_models import VETQualification, UnitOfCompetency
                
                # Recursively handle units
                if "units" in obj:
                    units = []
                    for unit_data in obj["units"]:
                        if isinstance(unit_data, dict):
                            units.append(self.object_hook({**unit_data, "_type": "UnitOfCompetency"}))
                        else:
                            units.append(unit_data)
                    obj["units"] = units
                
                return VETQualification(**obj)
            
            elif class_name == "UniQualification":
                from models.base_models import UniQualification, UniCourse
                
                # Recursively handle courses
                if "courses" in obj:
                    courses = []
                    for course_data in obj["courses"]:
                        if isinstance(course_data, dict):
                            courses.append(self.object_hook({**course_data, "_type": "UniCourse"}))
                        else:
                            courses.append(course_data)
                    obj["courses"] = courses
                
                return UniQualification(**obj)
            
            elif class_name == "CreditTransferRecommendation":
                from models.base_models import CreditTransferRecommendation
                from models.enums import RecommendationType
                
                # Handle recommendation type enum
                if "recommendation" in obj and isinstance(obj["recommendation"], str):
                    obj["recommendation"] = RecommendationType(obj["recommendation"])
                
                # Handle nested objects
                if "vet_units" in obj:
                    units = []
                    for unit_data in obj["vet_units"]:
                        if isinstance(unit_data, dict):
                            units.append(self.object_hook({**unit_data, "_type": "UnitOfCompetency"}))
                        else:
                            units.append(unit_data)
                    obj["vet_units"] = units
                
                if "uni_course" in obj and isinstance(obj["uni_course"], dict):
                    obj["uni_course"] = self.object_hook({**obj["uni_course"], "_type": "UniCourse"})
                
                if "gaps" in obj:
                    gaps = []
                    for gap_data in obj["gaps"]:
                        if isinstance(gap_data, dict):
                            gaps.append(self.object_hook({**gap_data, "_type": "Skill"}))
                        else:
                            gaps.append(gap_data)
                    obj["gaps"] = gaps
                
                return CreditTransferRecommendation(**obj)
        
        return obj


# Convenience functions
def dumps(obj: Any, **kwargs) -> str:
    """Serialize object to JSON string with deep processing"""
    kwargs.setdefault('indent', 2)
    return json.dumps(obj, cls=ModelJSONEncoder, **kwargs)


def dump(obj: Any, fp, **kwargs) -> None:
    """Serialize object to JSON file with deep processing"""
    kwargs.setdefault('indent', 2)
    json.dump(obj, fp, cls=ModelJSONEncoder, **kwargs)


def loads(s: str, **kwargs) -> Any:
    """Deserialize JSON string to object"""
    return json.loads(s, cls=ModelJSONDecoder, **kwargs)


def load(fp, **kwargs) -> Any:
    """Deserialize JSON file to object"""
    return json.load(fp, cls=ModelJSONDecoder, **kwargs)


# For convenience, also provide functions that work with standard json module
def make_json_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format.
    This can be used with standard json.dumps()
    """
    encoder = ModelJSONEncoder()
    return encoder._deep_process(obj)