"""
Quality monitoring and feedback system
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import numpy as np


class QualityMonitor:
    """Monitor and improve analysis quality"""
    
    def __init__(self, log_dir: str = "output/quality_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.current_session = {
            "start_time": time.time(),
            "extraction_times": [],
            "matching_times": [],
            "skills_per_unit": [],
            "confidence_scores": [],
            "match_scores": [],
            "ai_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def log_extraction(self, unit_code: str, skill_count: int, duration: float, confidence_avg: float):
        """Log extraction metrics"""
        self.current_session["extraction_times"].append(duration)
        self.current_session["skills_per_unit"].append(skill_count)
        self.current_session["confidence_scores"].append(confidence_avg)
    
    def log_matching(self, score: float, duration: float):
        """Log matching metrics"""
        self.current_session["matching_times"].append(duration)
        self.current_session["match_scores"].append(score)
    
    def log_ai_call(self):
        """Log AI API call"""
        self.current_session["ai_calls"] += 1
    
    def log_cache_hit(self):
        """Log cache hit"""
        self.current_session["cache_hits"] += 1
    
    def log_cache_miss(self):
        """Log cache miss"""
        self.current_session["cache_misses"] += 1
    
    def get_performance_summary(self) -> Dict:
        """Get current performance summary"""
        
        total_time = time.time() - self.current_session["start_time"]
        
        return {
            "total_duration": total_time,
            "avg_extraction_time": np.mean(self.current_session["extraction_times"]) if self.current_session["extraction_times"] else 0,
            "avg_matching_time": np.mean(self.current_session["matching_times"]) if self.current_session["matching_times"] else 0,
            "avg_skills_per_unit": np.mean(self.current_session["skills_per_unit"]) if self.current_session["skills_per_unit"] else 0,
            "avg_confidence": np.mean(self.current_session["confidence_scores"]) if self.current_session["confidence_scores"] else 0,
            "avg_match_score": np.mean(self.current_session["match_scores"]) if self.current_session["match_scores"] else 0,
            "total_ai_calls": self.current_session["ai_calls"],
            "cache_hit_rate": self.current_session["cache_hits"] / max(1, self.current_session["cache_hits"] + self.current_session["cache_misses"])
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on metrics"""
        
        suggestions = []
        summary = self.get_performance_summary()
        
        # Performance suggestions
        if summary["avg_extraction_time"] > 5:
            suggestions.append("Enable batch processing to reduce extraction time")
        
        if summary["cache_hit_rate"] < 0.3:
            suggestions.append("Increase cache TTL or ensure cache is enabled")
        
        if summary["total_ai_calls"] > 100:
            suggestions.append("Consider using 'fast' profile to reduce AI calls")
        
        # Quality suggestions
        if summary["avg_confidence"] < 0.6:
            suggestions.append("Review extraction prompts or switch to 'thorough' profile")
        
        if summary["avg_match_score"] < 0.5:
            suggestions.append("Check if correct courses are being matched")
        
        if summary["avg_skills_per_unit"] < 5:
            suggestions.append("Extraction may be too restrictive - adjust thresholds")
        elif summary["avg_skills_per_unit"] > 50:
            suggestions.append("Too many skills extracted - increase minimum confidence")
        
        return suggestions
    
    def save_session(self):
        """Save current session to file"""
        
        session_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.get_performance_summary(),
            "suggestions": self.suggest_improvements(),
            "raw_data": self.current_session
        }
        
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(session_file)
    
    def reset_session(self):
        """Reset session metrics"""
        self.current_session = {
            "start_time": time.time(),
            "extraction_times": [],
            "matching_times": [],
            "skills_per_unit": [],
            "confidence_scores": [],
            "match_scores": [],
            "ai_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }