"""
THA Facet Assignment Validator

Generates an HTML validation report after THA assignment.
Shows issues immediately with reasoning so you can fix taxonomy gaps
or misassignments before proceeding.

Report sections:
  1. Coverage Summary — skills per THA, empty/overloaded THAs flagged
  2. Flagged Issues — skills with problems, sorted by severity:
     - LOW CONFIDENCE: best match similarity < threshold
     - TIGHT MARGIN: gap between #1 and #2 candidate < margin
     - OUTLIER: skill is far from group centroid
     - UNASSIGNED: no THA assigned at all
  3. Per-THA Sample — 5 random skills per THA for spot-checking
  4. Confusion Pairs — THA pairs most frequently confused

Each flagged skill shows:
  - Skill name + definition
  - Assigned THA + similarity score
  - Top-3 alternative THAs + scores
  - LLM reasoning (optional): why the assignment might be wrong

Usage:
    from src.validation.tha_validator import THAValidator
    validator = THAValidator(config, embedding_interface, genai_interface)
    validator.validate_and_report(skill_registry, df_unique, skill_embeddings, output_path)
"""

import logging
import json
import random
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from config.facets import ALL_FACETS, get_facet_text_for_embedding

logger = logging.getLogger(__name__)


class THAValidator:
    """Validates THA facet assignments and generates an HTML report."""

    def __init__(self, config: Dict, embedding_interface=None, genai_interface=None):
        self.config = config
        self.embedding_interface = embedding_interface
        self.genai_interface = genai_interface

        # Thresholds for flagging
        self.low_confidence_threshold = 0.40
        self.tight_margin_threshold = 0.05  # gap between #1 and #2
        self.outlier_std_multiplier = 2.0   # flag if > mean + 2*std distance from centroid
        self.samples_per_tha = 5
        self.max_llm_validations = 100      # limit LLM calls for cost

        # Precomputed
        self._tha_embeddings = None
        self._tha_keys = None
        self._tha_embeddings_by_trf = {}
        self._tha_keys_by_trf = {}

    def validate_and_report(
        self,
        skill_registry: Dict[str, Dict],
        df_unique: pd.DataFrame,
        skill_embeddings: np.ndarray,
        output_path: Path,
    ) -> Dict[str, Any]:
        """
        Run validation and write HTML report.

        Returns summary statistics dict.
        """
        logger.info("=" * 60)
        logger.info("THA ASSIGNMENT VALIDATION")
        logger.info("=" * 60)

        output_path = Path(output_path)
        self._precompute_tha_embeddings()

        # Build skill_id → embedding index mapping
        sid_to_idx = {}
        for i, row in df_unique.iterrows():
            sid_to_idx[row["skill_id"]] = i

        # ── 1. Compute top-N candidates for every skill ──────
        logger.info("Computing top-5 THA candidates per skill...")
        skill_analyses = self._analyse_all_skills(skill_registry, df_unique, skill_embeddings, sid_to_idx)

        # ── 2. Coverage analysis ─────────────────────────────
        coverage = self._compute_coverage(skill_registry)

        # ── 3. Flag issues ───────────────────────────────────
        issues = self._flag_issues(skill_analyses, skill_registry, skill_embeddings, sid_to_idx)
        logger.info(f"Flagged {len(issues)} issues")

        # ── 4. LLM reasoning for top issues ──────────────────
        if self.genai_interface and issues:
            top_issues = issues[:self.max_llm_validations]
            logger.info(f"Generating LLM reasoning for {len(top_issues)} flagged skills...")
            self._add_llm_reasoning(top_issues)

        # ── 5. Per-THA samples ───────────────────────────────
        samples = self._sample_per_tha(skill_registry)

        # ── 6. Confusion pairs ───────────────────────────────
        confusion = self._compute_confusion_pairs(skill_analyses)

        # ── 7. Generate report ───────────────────────────────
        stats = {
            "total_skills": len(skill_registry),
            "assigned": sum(1 for s in skill_registry.values() if s.get("facets", {}).get("THA")),
            "unassigned": sum(1 for s in skill_registry.values() if not s.get("facets", {}).get("THA")),
            "total_issues": len(issues),
            "issue_breakdown": defaultdict(int),
            "active_thas": len([c for c in coverage if coverage[c]["count"] > 0]),
            "empty_thas": len([c for c in coverage if coverage[c]["count"] == 0]),
        }
        for issue in issues:
            stats["issue_breakdown"][issue["issue_type"]] += 1
        stats["issue_breakdown"] = dict(stats["issue_breakdown"])

        report_path = output_path / "tha_validation_report.html"
        self._write_html_report(report_path, coverage, issues, samples, confusion, stats)
        logger.info(f"Validation report: {report_path}")

        # Also write issues as JSON for programmatic use
        issues_json_path = output_path / "tha_validation_issues.json"
        with open(issues_json_path, "w") as f:
            json.dump({"statistics": stats, "issues": issues[:500]}, f, indent=2, default=str)

        logger.info(f"Total issues: {stats['total_issues']}")
        for itype, count in stats["issue_breakdown"].items():
            logger.info(f"  {itype}: {count}")

        return stats

    # ═══════════════════════════════════════════════════════════════
    #  ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    def _analyse_all_skills(self, skill_registry, df_unique, skill_embeddings, sid_to_idx):
        """Compute top-5 THA candidates for every skill."""
        results = {}  # skill_id → {assigned, confidence, top_candidates: [{code, name, sim}]}

        tha_values = ALL_FACETS.get("THA", {}).get("values", {})

        for sid, info in skill_registry.items():
            if sid not in sid_to_idx:
                continue

            idx = sid_to_idx[sid]
            skill_emb = skill_embeddings[idx].reshape(1, -1)
            facets = info.get("facets", {})
            trf_code = facets.get("TRF", {}).get("code", "")
            tha_data = facets.get("THA", {})
            assigned_code = tha_data.get("code", "")
            assigned_conf = tha_data.get("confidence", 0.0)

            # Parse multi-value THA
            if isinstance(assigned_code, str) and assigned_code.startswith("["):
                try:
                    assigned_codes = json.loads(assigned_code)
                    assigned_code = assigned_codes[0] if assigned_codes else ""
                except:
                    pass

            # Get candidates from the skill's TRF group
            if trf_code and trf_code in self._tha_embeddings_by_trf:
                tha_embs = self._tha_embeddings_by_trf[trf_code]
                tha_keys = self._tha_keys_by_trf[trf_code]

                sims = self.embedding_interface.similarity(skill_emb, tha_embs)[0]
                top_k = min(5, len(tha_keys))
                top_idx = np.argsort(sims)[-top_k:][::-1]

                candidates = []
                for k, j in enumerate(top_idx):
                    code = tha_keys[j]
                    candidates.append({
                        "code": code,
                        "name": tha_values.get(code, {}).get("name", code),
                        "similarity": float(sims[j]),
                        "rank": k + 1,
                    })
            else:
                candidates = []

            results[sid] = {
                "skill_name": info.get("preferred_label", sid),
                "definition": info.get("definition", ""),
                "trf_code": trf_code,
                "assigned_code": assigned_code,
                "assigned_name": tha_values.get(assigned_code, {}).get("name", assigned_code),
                "assigned_confidence": assigned_conf,
                "top_candidates": candidates,
            }

        return results

    def _flag_issues(self, skill_analyses, skill_registry, skill_embeddings, sid_to_idx):
        """Identify skills with potential misassignments."""
        issues = []

        for sid, analysis in skill_analyses.items():
            candidates = analysis["top_candidates"]
            assigned = analysis["assigned_code"]
            conf = analysis["assigned_confidence"]

            issue = {
                "skill_id": sid,
                "skill_name": analysis["skill_name"],
                "definition": analysis["definition"][:200],
                "trf_code": analysis["trf_code"],
                "assigned_tha": assigned,
                "assigned_tha_name": analysis["assigned_name"],
                "confidence": conf,
                "top_candidates": candidates[:5],
                "issue_type": None,
                "severity": 0,
                "reason": "",
                "llm_reasoning": "",
            }

            # UNASSIGNED
            if not assigned:
                issue["issue_type"] = "UNASSIGNED"
                issue["severity"] = 100
                issue["reason"] = "No THA assigned — skill may not match any defined ability"
                issues.append(issue)
                continue

            # LOW CONFIDENCE
            if conf < self.low_confidence_threshold:
                issue["issue_type"] = "LOW_CONFIDENCE"
                issue["severity"] = 80
                issue["reason"] = f"Best match similarity {conf:.3f} is below threshold {self.low_confidence_threshold}"
                issues.append(issue)
                continue

            # TIGHT MARGIN
            if len(candidates) >= 2:
                gap = candidates[0]["similarity"] - candidates[1]["similarity"]
                if gap < self.tight_margin_threshold and conf < 0.6:
                    runner_up = candidates[1]
                    issue["issue_type"] = "TIGHT_MARGIN"
                    issue["severity"] = 60
                    issue["reason"] = (
                        f"Gap between #{1} ({candidates[0]['name']}: {candidates[0]['similarity']:.3f}) "
                        f"and #{2} ({runner_up['name']}: {runner_up['similarity']:.3f}) "
                        f"is only {gap:.3f}"
                    )
                    issues.append(issue)

        # Sort by severity descending, then by confidence ascending
        issues.sort(key=lambda x: (-x["severity"], x["confidence"]))
        return issues

    # ═══════════════════════════════════════════════════════════════
    #  LLM REASONING
    # ═══════════════════════════════════════════════════════════════

    def _add_llm_reasoning(self, issues: List[Dict]):
        """Add LLM-generated reasoning to flagged issues."""
        if not self.genai_interface:
            return

        tha_values = ALL_FACETS.get("THA", {}).get("values", {})

        system_prompt = (
            "You are validating skill-to-ability assignments in a VET taxonomy.\n"
            "For each skill, assess whether the assigned Transferable Human Ability (THA) is correct.\n"
            "Consider: Does the skill genuinely belong to this ability category? "
            "Would a different candidate be a better fit?\n\n"
            "RULES:\n"
            "- Output ONLY a JSON object: {\"correct\": true/false, \"reasoning\": \"...reason...\", \"better_fit\": \"code or null\"}\n"
            "- Be specific: name what makes the match good or bad\n"
            "- If wrong, specify which candidate code is better\n"
            "- Do NOT wrap in markdown"
        )

        batch_size = 20
        for batch_start in range(0, len(issues), batch_size):
            batch = issues[batch_start:batch_start + batch_size]
            prompts = []

            for issue in batch:
                cands = "\n".join(
                    f"  {c['rank']}. {c['code']} — {c['name']} (sim: {c['similarity']:.3f})"
                    for c in issue["top_candidates"][:5]
                )
                assigned_desc = tha_values.get(issue["assigned_tha"], {}).get("description", "")

                prompt = (
                    f"SKILL: {issue['skill_name']}\n"
                    f"DEFINITION: {issue['definition']}\n"
                    f"ASSIGNED: {issue['assigned_tha']} — {issue['assigned_tha_name']}\n"
                    f"  Description: {assigned_desc}\n"
                    f"CONFIDENCE: {issue['confidence']:.3f}\n"
                    f"ISSUE: {issue['issue_type']} — {issue['reason']}\n\n"
                    f"TOP CANDIDATES:\n{cands}\n\n"
                    f"{{\"correct\":"
                )
                prompts.append(prompt)

            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=prompts, system_prompt=system_prompt
                )
                for issue, response in zip(batch, responses):
                    try:
                        parsed = self.genai_interface._parse_json_response(response)
                        if isinstance(parsed, dict):
                            correct = parsed.get("correct", True)
                            reasoning = parsed.get("reasoning", "")
                            better = parsed.get("better_fit")
                            verdict = "✓ CORRECT" if correct else f"✗ WRONG → {better}" if better else "✗ WRONG"
                            issue["llm_reasoning"] = f"{verdict}: {reasoning}"
                        else:
                            issue["llm_reasoning"] = str(response)[:200]
                    except:
                        issue["llm_reasoning"] = str(response)[:200]
            except Exception as e:
                logger.warning(f"LLM validation batch failed: {e}")

    # ═══════════════════════════════════════════════════════════════
    #  COVERAGE & SAMPLES
    # ═══════════════════════════════════════════════════════════════

    def _compute_coverage(self, skill_registry):
        """Count skills per THA."""
        tha_values = ALL_FACETS.get("THA", {}).get("values", {})
        coverage = {}
        for code, val in tha_values.items():
            coverage[code] = {
                "code": code,
                "name": val.get("name", code),
                "parent_trf": val.get("parent_trf", ""),
                "count": 0,
                "skills": [],
            }

        for sid, info in skill_registry.items():
            tha_data = info.get("facets", {}).get("THA", {})
            code = tha_data.get("code", "")
            if isinstance(code, str) and code.startswith("["):
                try:
                    codes = json.loads(code)
                except:
                    codes = [code]
            else:
                codes = [code] if code else []
            for c in codes:
                if c in coverage:
                    coverage[c]["count"] += 1
                    if len(coverage[c]["skills"]) < 50:
                        coverage[c]["skills"].append(info.get("preferred_label", sid))

        return coverage

    def _sample_per_tha(self, skill_registry):
        """Random sample of skills per THA for spot-checking."""
        tha_groups = defaultdict(list)
        for sid, info in skill_registry.items():
            tha_data = info.get("facets", {}).get("THA", {})
            code = tha_data.get("code", "")
            if isinstance(code, str) and code.startswith("["):
                try:
                    codes = json.loads(code)
                    code = codes[0] if codes else ""
                except:
                    pass
            if code:
                tha_groups[code].append({
                    "skill_id": sid,
                    "name": info.get("preferred_label", sid),
                    "confidence": tha_data.get("confidence", 0),
                })

        samples = {}
        for code, skills in tha_groups.items():
            n = min(self.samples_per_tha, len(skills))
            samples[code] = random.sample(skills, n)
        return samples

    def _compute_confusion_pairs(self, skill_analyses):
        """Find THA pairs that are most frequently confused (tight margin)."""
        pair_counts = defaultdict(int)

        for sid, analysis in skill_analyses.items():
            cands = analysis["top_candidates"]
            if len(cands) >= 2:
                gap = cands[0]["similarity"] - cands[1]["similarity"]
                if gap < 0.08:  # fairly tight
                    pair = tuple(sorted([cands[0]["code"], cands[1]["code"]]))
                    pair_counts[pair] += 1

        # Top 20 confused pairs
        sorted_pairs = sorted(pair_counts.items(), key=lambda x: -x[1])[:20]
        tha_values = ALL_FACETS.get("THA", {}).get("values", {})
        result = []
        for (a, b), count in sorted_pairs:
            result.append({
                "tha_a": a, "name_a": tha_values.get(a, {}).get("name", a),
                "tha_b": b, "name_b": tha_values.get(b, {}).get("name", b),
                "confused_count": count,
            })
        return result

    # ═══════════════════════════════════════════════════════════════
    #  PRECOMPUTE
    # ═══════════════════════════════════════════════════════════════

    def _precompute_tha_embeddings(self):
        """Compute THA value embeddings, grouped by TRF."""
        if self._tha_embeddings is not None:
            return

        tha_values = ALL_FACETS.get("THA", {}).get("values", {})
        texts, keys = [], []
        for code in sorted(tha_values.keys()):
            texts.append(get_facet_text_for_embedding("THA", code))
            keys.append(code)

        self._tha_embeddings = self.embedding_interface.encode(texts, batch_size=32, show_progress=False)
        self._tha_keys = keys

        # Group by TRF
        for i, key in enumerate(keys):
            parent = tha_values[key].get("parent_trf", "")
            if parent:
                self._tha_embeddings_by_trf.setdefault(parent, []).append(i)
                self._tha_keys_by_trf.setdefault(parent, []).append(key)

        # Convert index lists to numpy arrays
        for trf in list(self._tha_embeddings_by_trf.keys()):
            indices = self._tha_embeddings_by_trf[trf]
            self._tha_embeddings_by_trf[trf] = self._tha_embeddings[indices]

    # ═══════════════════════════════════════════════════════════════
    #  HTML REPORT
    # ═══════════════════════════════════════════════════════════════

    def _write_html_report(self, path, coverage, issues, samples, confusion, stats):
        """Generate a single-page HTML validation report."""
        tha_values = ALL_FACETS.get("THA", {}).get("values", {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>THA Validation Report</title>
<style>
:root {{ --bg:#f5f7fa; --surf:#fff; --border:#e2e6ed; --text:#1a1f36; --text2:#5a6072; --text3:#8892a4;
  --green:#16a34a; --yellow:#ca8a04; --red:#dc2626; --accent:#0f6b5e; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }}
.container {{ max-width:1200px; margin:0 auto; padding:20px; }}
h1 {{ font-size:1.4rem; margin-bottom:4px; }}
h2 {{ font-size:1.1rem; margin:28px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--border); }}
h3 {{ font-size:.95rem; margin:16px 0 8px; color:var(--accent); }}
.subtitle {{ color:var(--text3); font-size:.85rem; margin-bottom:20px; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:24px; }}
.stat-card {{ background:var(--surf); border:1px solid var(--border); border-radius:8px; padding:14px; text-align:center; }}
.stat-val {{ font-size:1.5rem; font-weight:700; color:var(--accent); }}
.stat-label {{ font-size:.75rem; color:var(--text3); text-transform:uppercase; letter-spacing:.5px; }}
table {{ width:100%; border-collapse:collapse; font-size:.82rem; background:var(--surf); border:1px solid var(--border); border-radius:8px; overflow:hidden; margin-bottom:16px; }}
th {{ text-align:left; padding:8px 10px; background:var(--bg); color:var(--text3); font-size:.72rem; text-transform:uppercase; letter-spacing:.4px; border-bottom:2px solid var(--border); }}
td {{ padding:8px 10px; border-bottom:1px solid var(--border); vertical-align:top; }}
tr:hover td {{ background:#f8f9fb; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:.72rem; font-weight:600; }}
.badge-red {{ background:#fef2f2; color:var(--red); }}
.badge-yellow {{ background:#fefce8; color:var(--yellow); }}
.badge-green {{ background:#f0fdf4; color:var(--green); }}
.badge-gray {{ background:var(--bg); color:var(--text3); }}
.mono {{ font-family:'JetBrains Mono',monospace; font-size:.75rem; }}
.reason {{ font-size:.78rem; color:var(--text2); line-height:1.4; margin-top:4px; }}
.llm-box {{ font-size:.78rem; padding:6px 10px; margin-top:4px; border-radius:6px; line-height:1.4; }}
.llm-correct {{ background:#f0fdf4; color:#166534; }}
.llm-wrong {{ background:#fef2f2; color:#991b1b; }}
.llm-neutral {{ background:var(--bg); color:var(--text2); }}
.cand-list {{ font-size:.76rem; color:var(--text2); }}
.cand-list .top {{ font-weight:600; color:var(--text); }}
.bar {{ height:6px; border-radius:3px; background:#e5e7eb; overflow:hidden; margin-top:2px; }}
.bar-fill {{ height:100%; border-radius:3px; background:var(--accent); }}
.empty {{ color:var(--red); font-weight:600; }}
.section {{ margin-bottom:32px; }}
details {{ margin-bottom:8px; }}
summary {{ cursor:pointer; font-weight:600; font-size:.88rem; padding:6px 0; }}
</style>
</head>
<body>
<div class="container">
<h1>THA Facet Validation Report</h1>
<p class="subtitle">Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · {stats['total_skills']} skills · {stats['active_thas']} active THAs</p>

<!-- STATS -->
<div class="stats-grid">
  <div class="stat-card"><div class="stat-val">{stats['assigned']}</div><div class="stat-label">Assigned</div></div>
  <div class="stat-card"><div class="stat-val">{stats['unassigned']}</div><div class="stat-label">Unassigned</div></div>
  <div class="stat-card"><div class="stat-val">{stats['total_issues']}</div><div class="stat-label">Issues Flagged</div></div>
  <div class="stat-card"><div class="stat-val">{stats['active_thas']}</div><div class="stat-label">Active THAs</div></div>
  <div class="stat-card"><div class="stat-val">{stats['empty_thas']}</div><div class="stat-label">Empty THAs</div></div>
</div>
"""
        # Issue breakdown
        if stats["issue_breakdown"]:
            html += '<div class="stats-grid">'
            for itype, count in stats["issue_breakdown"].items():
                badge = "badge-red" if itype in ("UNASSIGNED", "LOW_CONFIDENCE") else "badge-yellow"
                html += f'<div class="stat-card"><div class="stat-val">{count}</div><div class="stat-label"><span class="badge {badge}">{itype}</span></div></div>'
            html += '</div>'

        # ── SECTION 1: COVERAGE ──────────────────────────────
        html += '<h2>1. Coverage by THA</h2>'
        for trf_code in ["TRF.UNI", "TRF.BRD", "TRF.SEC", "TRF.OCC"]:
            trf_name = ALL_FACETS.get("TRF", {}).get("values", {}).get(trf_code, {}).get("name", trf_code)
            trf_items = [(c, d) for c, d in coverage.items() if d["parent_trf"] == trf_code]
            trf_items.sort(key=lambda x: -x[1]["count"])

            if not trf_items:
                continue

            max_count = max(d["count"] for _, d in trf_items) or 1
            html += f'<h3>{trf_name} ({trf_code})</h3>'
            html += '<table><thead><tr><th>THA Code</th><th>Ability</th><th style="text-align:right">Skills</th><th style="width:200px">Distribution</th></tr></thead><tbody>'
            for code, data in trf_items:
                pct = data["count"] / max_count * 100
                empty_cls = ' class="empty"' if data["count"] == 0 else ""
                html += f'<tr><td class="mono">{code}</td><td{empty_cls}>{_esc(data["name"])}</td>'
                html += f'<td style="text-align:right">{data["count"]}</td>'
                html += f'<td><div class="bar"><div class="bar-fill" style="width:{pct:.0f}%"></div></div></td></tr>'
            html += '</tbody></table>'

        # ── SECTION 2: FLAGGED ISSUES ────────────────────────
        html += f'<h2>2. Flagged Issues ({len(issues)})</h2>'
        if not issues:
            html += '<p style="color:var(--green);font-weight:600">No issues found — all assignments look clean.</p>'
        else:
            html += '<table><thead><tr><th style="width:60px">Type</th><th>Skill</th><th>Assigned THA</th><th style="width:50px">Conf</th><th>Top Candidates</th><th>Reasoning</th></tr></thead><tbody>'
            for issue in issues[:200]:  # cap at 200 rows
                badge_cls = {
                    "UNASSIGNED": "badge-red", "LOW_CONFIDENCE": "badge-red",
                    "TIGHT_MARGIN": "badge-yellow",
                }.get(issue["issue_type"], "badge-gray")

                # Candidates column
                cand_html = ""
                for c in issue["top_candidates"][:4]:
                    is_top = c["rank"] == 1
                    cls = "top" if is_top else ""
                    marker = "→" if c["code"] == issue["assigned_tha"] else f"#{c['rank']}"
                    cand_html += f'<div class="cand-list"><span class="{cls}">{marker} {_esc(c["name"])}</span> <span class="mono">({c["similarity"]:.3f})</span></div>'

                # LLM reasoning
                llm = issue.get("llm_reasoning", "")
                if llm:
                    if "✗ WRONG" in llm:
                        llm_cls = "llm-wrong"
                    elif "✓ CORRECT" in llm:
                        llm_cls = "llm-correct"
                    else:
                        llm_cls = "llm-neutral"
                    llm_html = f'<div class="llm-box {llm_cls}">{_esc(llm)}</div>'
                else:
                    llm_html = f'<div class="reason">{_esc(issue["reason"])}</div>'

                html += f'<tr>'
                html += f'<td><span class="badge {badge_cls}">{issue["issue_type"]}</span></td>'
                html += f'<td><strong>{_esc(issue["skill_name"])}</strong><br><span style="font-size:.74rem;color:var(--text3)">{_esc(issue["definition"])}</span></td>'
                html += f'<td class="mono" style="font-size:.74rem">{_esc(issue["assigned_tha_name"])}</td>'
                html += f'<td style="text-align:center">{issue["confidence"]:.2f}</td>'
                html += f'<td>{cand_html}</td>'
                html += f'<td>{llm_html}</td>'
                html += f'</tr>'
            html += '</tbody></table>'

            if len(issues) > 200:
                html += f'<p style="color:var(--text3);font-size:.82rem">Showing 200 of {len(issues)} issues. Full list in tha_validation_issues.json.</p>'

        # ── SECTION 3: CONFUSION PAIRS ───────────────────────
        html += f'<h2>3. Most Confused THA Pairs ({len(confusion)})</h2>'
        if confusion:
            html += '<p style="font-size:.82rem;color:var(--text2);margin-bottom:8px">THA pairs where skills frequently have tight margins between #1 and #2 candidates.</p>'
            html += '<table><thead><tr><th>THA A</th><th>THA B</th><th style="text-align:right">Confused Skills</th></tr></thead><tbody>'
            for pair in confusion[:15]:
                html += f'<tr><td>{_esc(pair["name_a"])} <span class="mono">({pair["tha_a"]})</span></td>'
                html += f'<td>{_esc(pair["name_b"])} <span class="mono">({pair["tha_b"]})</span></td>'
                html += f'<td style="text-align:right"><strong>{pair["confused_count"]}</strong></td></tr>'
            html += '</tbody></table>'
        else:
            html += '<p style="color:var(--green)">No frequently confused pairs found.</p>'

        # ── SECTION 4: RANDOM SAMPLES ────────────────────────
        html += f'<h2>4. Random Samples by THA ({self.samples_per_tha} per group)</h2>'
        html += '<p style="font-size:.82rem;color:var(--text2);margin-bottom:12px">Spot-check: do these skills belong in their assigned THA?</p>'

        for trf_code in ["TRF.UNI", "TRF.BRD", "TRF.SEC", "TRF.OCC"]:
            trf_name = ALL_FACETS.get("TRF", {}).get("values", {}).get(trf_code, {}).get("name", trf_code)
            trf_thas = [c for c in sorted(samples.keys()) if tha_values.get(c, {}).get("parent_trf") == trf_code]

            if not trf_thas:
                continue

            html += f'<details><summary>{trf_name} ({len(trf_thas)} THAs)</summary>'
            for tha_code in trf_thas:
                tha_name = tha_values.get(tha_code, {}).get("name", tha_code)
                skills = samples[tha_code]
                html += f'<h3 style="margin-left:12px">{tha_name} <span class="mono">({tha_code})</span></h3>'
                html += '<table style="margin-left:12px;width:calc(100% - 12px)"><tbody>'
                for s in skills:
                    conf = s["confidence"]
                    badge = "badge-green" if conf >= 0.5 else "badge-yellow" if conf >= 0.35 else "badge-red"
                    html += f'<tr><td>{_esc(s["name"])}</td><td style="width:60px"><span class="badge {badge}">{conf:.2f}</span></td></tr>'
                html += '</tbody></table>'
            html += '</details>'

        html += '</div></body></html>'

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


def _esc(s):
    """HTML escape."""
    if not s:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
