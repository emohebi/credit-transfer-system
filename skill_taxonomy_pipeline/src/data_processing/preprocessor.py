"""
Data Preprocessor for Skill Assertion Pipeline.

Key difference from taxonomy pipeline:
  - We do NOT remove duplicates here.
  - Every row is a potential SkillAssertion.
  - We only clean, validate, and normalize.
"""
import logging
import re
import json
import pandas as pd
import numpy as np
from typing import Dict

logger = logging.getLogger(__name__)


class AssertionDataPreprocessor:
    """Clean and normalize extracted skill data. Preserves all rows."""

    def __init__(self, config: Dict):
        self.confidence_threshold = config["data"]["confidence_threshold"]
        self.min_skill_length = config["data"]["min_skill_length"]
        self.max_skill_length = config["data"]["max_skill_length"]

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Preprocessing {len(df)} rows (each row → potential SkillAssertion)")
        df = df.copy()

        df = self._ensure_columns(df)
        df = self._filter_confidence(df)
        df = self._clean_names(df)
        df = self._clean_evidence(df)
        df = self._normalize_context(df)
        df = self._normalize_level(df)
        df = self._parse_keywords(df)
        df = self._create_embedding_text(df)
        df = df.reset_index(drop=True)

        logger.info(f"After preprocessing: {len(df)} rows retained")
        logger.info(f"  Unique skill names: {df['name'].nunique()}")
        logger.info(f"  Unique unit codes: {df['code'].nunique()}")
        logger.info(f"  Context distribution: {df['context'].value_counts().to_dict()}")
        logger.info(f"  Level range: {df['level'].min()}-{df['level'].max()}")
        return df

    # ── Column setup ──────────────────────────────────────────────

    def _ensure_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if "name" not in df.columns and "skill_name" in df.columns:
            df.rename(columns={"skill_name": "name"}, inplace=True)
        if "code" not in df.columns and "unit_code" in df.columns:
            df.rename(columns={"unit_code": "code"}, inplace=True)

        required = ["name", "code", "level", "context", "confidence"]
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df["name"] = df["name"].astype(str).str.strip()
        df["code"] = df["code"].astype(str).str.strip()

        # Drop rows with empty names
        df = df[df["name"].notna() & (df["name"] != "") & (df["name"] != "nan")]

        # Optional columns
        if "description" not in df.columns:
            df["description"] = ""
        if "evidence" not in df.columns:
            df["evidence"] = ""
        if "category" not in df.columns:
            df["category"] = "general"
        if "keywords" not in df.columns:
            df["keywords"] = ""

        df["description"] = df["description"].fillna("").astype(str)
        df["evidence"] = df["evidence"].fillna("").astype(str)
        df["category"] = df["category"].fillna("general").astype(str).str.lower().str.replace(" ", "_")
        return df

    # ── Filtering ─────────────────────────────────────────────────

    def _filter_confidence(self, df: pd.DataFrame) -> pd.DataFrame:
        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)
        before = len(df)
        df = df[df["confidence"] >= self.confidence_threshold]
        dropped = before - len(df)
        if dropped:
            logger.info(f"  Filtered {dropped} rows below confidence {self.confidence_threshold}")
        return df

    # ── Cleaning ──────────────────────────────────────────────────

    def _clean_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df["name"] = df["name"].str.replace(r"\s+", " ", regex=True)
        df["name"] = df["name"].str.replace(r"[^\w\s\-\+\#\&\/\.]", " ", regex=True)

        before = len(df)
        df = df[
            (df["name"].str.len() >= self.min_skill_length)
            & (df["name"].str.len() <= self.max_skill_length)
        ]
        dropped = before - len(df)
        if dropped:
            logger.info(f"  Filtered {dropped} rows by name length")

        # Title case for consistency
        df["name"] = df["name"].str.title()
        return df

    def _clean_evidence(self, df: pd.DataFrame) -> pd.DataFrame:
        df["evidence"] = df["evidence"].str.replace(r"[^a-zA-Z0-9\s,.]", "", regex=True).str.strip()
        return df

    # ── Normalization ─────────────────────────────────────────────

    def _normalize_context(self, df: pd.DataFrame) -> pd.DataFrame:
        def _norm(val):
            s = str(val).lower().strip()
            if "prac" in s or "hand" in s:
                return "PRACTICAL"
            elif "theo" in s or "concept" in s:
                return "THEORETICAL"
            elif "hybrid" in s or "blend" in s:
                return "HYBRID"
            return "HYBRID"  # default

        df["context"] = df["context"].apply(_norm)
        return df

    def _normalize_level(self, df: pd.DataFrame) -> pd.DataFrame:
        # Handle SkillLevel enum names from the original pipeline
        level_name_map = {
            "FOLLOW": 1, "ASSIST": 2, "APPLY": 3, "ENABLE": 4,
            "ENSURE_ADVISE": 5, "INITIATE_INFLUENCE": 6, "SET_STRATEGY": 7,
        }

        def _norm(val):
            if pd.isna(val):
                return 3
            s = str(val).strip().upper()
            if s in level_name_map:
                return level_name_map[s]
            try:
                return max(1, min(7, int(float(s))))
            except (ValueError, TypeError):
                return 3

        df["level"] = df["level"].apply(_norm)
        return df

    # ── Keywords ──────────────────────────────────────────────────

    def _parse_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        def _parse(val):
            if isinstance(val, list):
                return val
            if pd.isna(val) or val == "":
                return []
            s = str(val).strip()
            if s.startswith("["):
                try:
                    return json.loads(s.replace("'", '"'))
                except (json.JSONDecodeError, ValueError):
                    pass
            return [k.strip() for k in re.split(r"[,;|\n]", s) if k.strip()]

        df["keywords_list"] = df["keywords"].apply(_parse)
        return df

    # ── Embedding text ────────────────────────────────────────────

    def _create_embedding_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Text used for embedding-based deduplication. Name + description only."""
        df["embedding_text"] = (df["name"].fillna(""))# + ". " + df["description"].fillna("")).str.strip()
        df = df[df["embedding_text"] != ""]
        return df
