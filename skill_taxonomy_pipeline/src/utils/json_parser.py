"""
Robust JSON Parser for LLM responses.

Handles common LLM output quirks:
  - Channel markers: 'final', 'assistantfinal', 'commentary', etc.
  - Markdown code fences: ```json ... ```
  - Extra/doubled brackets from JSON-start forcing: {{"choice": ...}}
  - Trailing text after valid JSON
  - Leading text before JSON
  - Nested JSON with extra wrapping

Used by both GenAIInterface and VLLMGenAIInterface to replace
their individual _parse_json_response methods.

Usage:
    from src.utils.json_parser import robust_parse_json
    result = robust_parse_json(llm_response)
    # Returns dict, list, or {} on failure
"""

import json
import re
import logging
from typing import Union, Dict, List

logger = logging.getLogger(__name__)

# Channel markers produced by GPT-template models
# These appear at the start of the response before actual content
CHANNEL_MARKERS = re.compile(
    r'^[\s]*(final|assistantfinal|commentary|analysis|assistant)\s*',
    re.IGNORECASE
)

# Markdown code fence patterns
MD_FENCE_START = re.compile(r'^[\s]*```(?:json)?[\s]*\n?', re.IGNORECASE)
MD_FENCE_END = re.compile(r'\n?[\s]*```[\s]*$')


def robust_parse_json(text: str) -> Union[Dict, List, dict]:
    """
    Parse JSON from an LLM response, handling common output quirks.

    Tries multiple extraction strategies in order:
    1. Strip channel markers and markdown fences
    2. Direct parse
    3. Find outermost JSON object {...}
    4. Find outermost JSON array [...]
    5. Find innermost JSON object (for double-wrapped cases)
    6. Attempt repair of common malformations

    Args:
        text: Raw LLM response string

    Returns:
        Parsed JSON as dict or list. Returns {} on complete failure.
    """
    if not text:
        return {}

    # ── Step 0: Clean the text ────────────────────────────────
    cleaned = _clean_response(text)

    if not cleaned:
        return {}

    # ── Step 1: Direct parse ──────────────────────────────────
    result = _try_parse(cleaned)
    if result is not None:
        return result

    # ── Step 2: Find outermost JSON object ────────────────────
    result = _extract_outermost_object(cleaned)
    if result is not None:
        return result

    # ── Step 3: Find outermost JSON array ─────────────────────
    result = _extract_outermost_array(cleaned)
    if result is not None:
        return result

    # ── Step 4: Find innermost JSON object (double-wrap fix) ──
    result = _extract_innermost_object(cleaned)
    if result is not None:
        return result

    # ── Step 5: Repair common malformations ───────────────────
    result = _try_repair(cleaned)
    if result is not None:
        return result

    # ── Step 6: Last resort — try the original text too ───────
    if cleaned != text.strip():
        result = _extract_outermost_object(text.strip())
        if result is not None:
            return result

    logger.debug(f"All JSON parsing strategies failed. Text: {text[:200]}...")
    return {}


def _clean_response(text: str) -> str:
    """Strip channel markers, markdown fences, and whitespace."""
    cleaned = text.strip()

    # Remove channel markers (e.g., "final", "assistantfinal")
    cleaned = CHANNEL_MARKERS.sub('', cleaned).strip()

    # Remove markdown code fences
    cleaned = MD_FENCE_START.sub('', cleaned)
    cleaned = MD_FENCE_END.sub('', cleaned)
    cleaned = cleaned.strip()

    return cleaned


def _try_parse(text: str) -> Union[Dict, List, None]:
    """Try direct JSON parse."""
    try:
        result = json.loads(text)
        if isinstance(result, (dict, list)):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _extract_outermost_object(text: str) -> Union[Dict, None]:
    """
    Find the outermost balanced {...} in the text using bracket counting.
    More robust than regex for nested objects.
    """
    start = text.find('{')
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False
    end = -1

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        return None

    candidate = text[start:end + 1]
    return _try_parse(candidate)


def _extract_outermost_array(text: str) -> Union[List, None]:
    """
    Find the outermost balanced [...] in the text using bracket counting.
    """
    start = text.find('[')
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False
    end = -1

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        return None

    candidate = text[start:end + 1]
    return _try_parse(candidate)


def _extract_innermost_object(text: str) -> Union[Dict, None]:
    """
    Find the innermost (smallest) balanced {...} in the text.
    Handles double-wrapping like {{"choice": 3, "confidence": 0.8}}
    """
    # Find all { positions
    starts = [i for i, c in enumerate(text) if c == '{']

    # Try from the last { backwards (innermost first)
    for start in reversed(starts):
        depth = 0
        in_string = False
        escape_next = False

        for i in range(start, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    result = _try_parse(candidate)
                    if result is not None:
                        return result
                    break

    return None


def _try_repair(text: str) -> Union[Dict, List, None]:
    """
    Attempt to repair common JSON malformations:
    - Missing closing bracket/brace
    - Extra trailing brackets
    - Single quotes instead of double quotes
    """
    # Fix 1: JSON-start prefix remnant — model completed {"choice": ...}
    # but the prompt already had {"choice": so we get {"choice":{"choice": ...}
    # Try to find the second occurrence and parse from there
    if text.count('{"') > 1:
        second_start = text.find('{"', text.find('{"') + 1)
        if second_start != -1:
            result = _extract_outermost_object(text[second_start:])
            if result is not None:
                return result

    # Fix 2: Single quotes → double quotes
    if "'" in text and '"' not in text:
        fixed = text.replace("'", '"')
        result = _try_parse(fixed)
        if result is not None:
            return result

    # Fix 3: Truncated JSON — try adding closing brackets
    for suffix in ['}', ']}', '}}', '"]}', '"}}']:
        result = _try_parse(text + suffix)
        if result is not None:
            return result

    # Fix 4: Extra trailing content after valid JSON
    # Find first { and try progressively longer substrings
    start = text.find('{')
    if start == -1:
        start = text.find('[')
    if start != -1:
        for end in range(len(text), start, -1):
            result = _try_parse(text[start:end])
            if result is not None:
                return result
            # Don't try every position — skip by chunks
            if len(text) - end > 10:
                break

    return None