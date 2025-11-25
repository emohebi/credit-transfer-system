"""
Data Preprocessing module for skill taxonomy pipeline
Handles data cleaning, normalization, and preparation
"""
import logging
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SkillDataPreprocessor:
    """Preprocesses skill data for taxonomy building"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.confidence_threshold = config['data']['confidence_threshold']
        self.min_skill_length = config['data']['min_skill_length']
        self.max_skill_length = config['data']['max_skill_length']
        
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess skill data
        
        Args:
            df: Raw skill data DataFrame
            
        Returns:
            Preprocessed DataFrame ready for embedding and clustering
        """
        logger.info(f"Preprocessing {len(df)} skills")
        
        # Make a copy to avoid modifying original
        df_processed = df.copy()
        
        # 1. Clean and validate basic fields and create skill_id if missing
        df_processed = self._clean_basic_fields(df_processed)
        
        # 2. Filter by confidence if available
        df_processed = self._filter_by_confidence(df_processed)
        
        # 3. Clean skill names
        df_processed = self._clean_skill_names(df_processed)
        
        # 4. Process descriptions
        df_processed = self._process_descriptions(df_processed)
        
        # 5. Process keywords
        df_processed = self._process_keywords(df_processed)
        
        # 6. Create combined text field for embedding
        df_processed = self._create_combined_text(df_processed)
        
        # 7. Add missing fields with defaults
        df_processed = self._add_default_fields(df_processed)
        
        # 8. Normalize levels and contexts
        df_processed = self._normalize_levels_and_contexts(df_processed)
        
        # 9. Remove duplicates based on skill_id
        df_processed = self._remove_exact_duplicates(df_processed)
        
        # 10. Validate final data
        df_processed = self._validate_final_data(df_processed)
        
        logger.info(f"Preprocessing complete: {len(df_processed)} skills retained")
        
        return df_processed
    
    def _clean_basic_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate basic required fields"""
        
        # Ensure skill_id exists
        if 'skill_id' not in df.columns:
            df['skill_id'] = [f'SK{i:06d}' for i in range(len(df))]
            logger.info("Generated skill IDs")
        
        # Ensure name field exists
        if 'name' not in df.columns:
            if 'skill_name' in df.columns:
                df['name'] = df['skill_name']
            else:
                raise ValueError("No 'name' column found in data")
        
        # Remove rows with empty names
        df = df[df['name'].notna() & (df['name'] != '')]
        
        # Convert to string and strip whitespace
        df['skill_id'] = df['skill_id'].astype(str).str.strip()
        df['name'] = df['name'].astype(str).str.strip()
        
        return df
    
    def _filter_by_confidence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter skills by confidence threshold"""
        if 'confidence' in df.columns:
            initial_count = len(df)
            df = df[df['confidence'] >= self.confidence_threshold]
            filtered_count = initial_count - len(df)
            
            if filtered_count > 0:
                logger.info(f"Filtered {filtered_count} skills with confidence < {self.confidence_threshold}")
        else:
            # Add default confidence if not present
            df['confidence'] = 0.8
            
        return df
    
    def _clean_skill_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize skill names"""
        
        # Remove extra whitespace
        df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)
        
        # Remove special characters but keep essential punctuation
        df['name'] = df['name'].str.replace(r'[^\w\s\-\+\#\&\/\.]', ' ', regex=True)
        
        # Filter by length
        initial_count = len(df)
        df = df[
            (df['name'].str.len() >= self.min_skill_length) & 
            (df['name'].str.len() <= self.max_skill_length)
        ]
        
        filtered_count = initial_count - len(df)
        if filtered_count > 0:
            logger.info(f"Filtered {filtered_count} skills based on name length")
        
        # Capitalize properly
        df['name'] = df['name'].str.title()
        
        return df
    
    def _process_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process skill descriptions"""
        
        if 'description' not in df.columns:
            # Generate from name if no description
            df['description'] = df['name'] + ' skill'
            logger.info("No description column found, using skill names")
        
        # Clean descriptions
        df['description'] = df['description'].fillna('')
        df['description'] = df['description'].astype(str).str.strip()
        
        # Remove excessive whitespace
        df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True)
        
        # Add description length
        df['description_length'] = df['description'].str.len()
        
        return df
    
    def _process_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process keywords field"""
        
        if 'keywords' not in df.columns:
            # Generate basic keywords from name
            df['keywords'] = df['name'].str.lower().str.split()
            logger.info("Generated keywords from skill names")
        
        # Convert keywords to list format
        def parse_keywords(keywords):
            if pd.isna(keywords):
                return []
            elif isinstance(keywords, list):
                return keywords
            elif isinstance(keywords, str):
                keywords = keywords.replace("'", '"').strip()
                # Split by common delimiters
                return json.loads(keywords) if (keywords.startswith('[') and keywords.endswith(']')) else [k.strip() for k in re.split(r',|;|\||\n', keywords) if k.strip()]
                # keywords = keywords.replace(';', ',').replace('|', ',')
                # return [k.strip() for k in keywords.split(',') if k.strip()]
            else:
                return []
        
        df['keywords'] = df['keywords'].apply(parse_keywords)
        
        # Create keywords string for text processing
        df['keywords_str'] = df['keywords'].apply(lambda x: ' '.join(x) if x else '')
        
        return df
    
    def _create_combined_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create combined text field for embedding"""
        
        # Combine name, description, and keywords
        df['combined_text'] = (
            df['name'].fillna('') + '. ' +
            df['description'].fillna('')# + ' ' +
            # df['keywords_str'].fillna('')
        ).str.strip()
        
        # Remove empty combined text
        df = df[df['combined_text'] != '']
        
        return df
    
    def _add_default_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add missing fields with default values"""
        
        # Add category if missing
        if 'category' not in df.columns:
            df['category'] = 'general'
            logger.info("No category column found, using 'general'")
        
        # Normalize category values
        df['category'] = df['category'].fillna('general')
        df['category'] = df['category'].str.lower().str.replace(' ', '_')
        
        # Map to standard categories if possible
        category_mapping = {
            'tech': 'technical',
            'technology': 'technical',
            'it': 'technical',
            'engineering': 'technical',
            'soft': 'interpersonal',
            'communication': 'interpersonal',
            'leadership': 'interpersonal',
            'management': 'interpersonal',
            'analytical': 'cognitive',
            'thinking': 'cognitive',
            'problem_solving': 'cognitive',
            'domain': 'domain_knowledge',
            'business': 'domain_knowledge'
        }
        
        df['category'] = df['category'].replace(category_mapping)
        
        # Add level if missing (handled in main.py validation too)
        if 'level' not in df.columns:
            df['level'] = 3  # Default to APPLY level
            logger.info("No level column found, defaulting to level 3")
        
        # Add context if missing
        if 'context' not in df.columns:
            df['context'] = 'hybrid'
            logger.info("No context column found, defaulting to 'hybrid'")
        
        return df
    
    def _normalize_levels_and_contexts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize level and context values"""
        
        # Normalize levels to 1-7 range
        if 'level' in df.columns:
            def normalize_level(level):
                if pd.isna(level):
                    return 3
                
                # If it's already a number
                try:
                    level_num = int(level)
                    return max(1, min(7, level_num))
                except:
                    pass
                
                # Try to parse from string
                level_str = str(level).lower()
                
                # Map common level descriptions
                level_map = {
                    'beginner': 1,
                    'novice': 1,
                    'basic': 2,
                    'elementary': 2,
                    'intermediate': 3,
                    'competent': 3,
                    'advanced': 4,
                    'proficient': 4,
                    'expert': 5,
                    'master': 6,
                    'strategic': 7
                }
                
                for key, value in level_map.items():
                    if key in level_str:
                        return value
                
                return 3  # Default
            
            df['level'] = df['level'].apply(normalize_level)
        
        # Normalize contexts
        if 'context' in df.columns:
            valid_contexts = ['practical', 'theoretical', 'hybrid']
            
            def normalize_context(context):
                if pd.isna(context):
                    return 'hybrid'
                
                context_str = str(context).lower()
                
                if 'prac' in context_str or 'hand' in context_str:
                    return 'practical'
                elif 'theo' in context_str or 'concept' in context_str:
                    return 'theoretical'
                elif context_str in valid_contexts:
                    return context_str
                else:
                    return 'hybrid'
            
            df['context'] = df['context'].apply(normalize_context)
        
        return df
    
    def _remove_exact_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicates based on skill_id"""
        
        initial_count = len(df)
        
        # Remove duplicates, keeping first occurrence
        df = df.drop_duplicates(subset=['skill_id'], keep='first')
        
        # Also check for duplicate names at same level
        df = df.drop_duplicates(subset=['name', 'level'], keep='first')
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} exact duplicates")
        
        return df
    
    def _validate_final_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final validation of preprocessed data"""
        
        # Check for required columns
        required_columns = ['skill_id', 'name', 'combined_text', 'level', 'context']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns after preprocessing: {missing_columns}")
        
        # Check for empty values in critical fields
        if df['name'].isna().any():
            df = df[df['name'].notna()]
            logger.warning("Removed rows with missing names")
        
        if df['combined_text'].str.strip().eq('').any():
            df = df[df['combined_text'].str.strip() != '']
            logger.warning("Removed rows with empty combined text")
        
        # Ensure proper data types
        df['level'] = df['level'].astype(int)
        df['confidence'] = df['confidence'].astype(float)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Log final statistics
        logger.info(f"Preprocessing complete:")
        logger.info(f"  Total skills: {len(df)}")
        logger.info(f"  Categories: {df['category'].nunique()}")
        logger.info(f"  Level range: {df['level'].min()}-{df['level'].max()}")
        logger.info(f"  Context distribution: {df['context'].value_counts().to_dict()}")
        
        return df
    
    def export_preprocessed_data(self, df: pd.DataFrame, filepath: str):
        """Export preprocessed data for inspection"""
        df.to_csv(filepath, index=False)
        logger.info(f"Exported preprocessed data to {filepath}")
