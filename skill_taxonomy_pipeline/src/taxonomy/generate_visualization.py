"""
Generate Interactive HTML Taxonomy Visualization (Optimized for Large Datasets)

This script creates a performant HTML visualization that can handle 50K+ skills
by using lazy loading, virtual rendering, and deferred detail display.

Now includes Ability Archetypes tab with progression ladders.

Theme: Jobs and Skills Australia (Australian Government)

Usage:
    python generate_visualization.py taxonomy.json output.html

Output:
    - taxonomy_visualization.html
    - taxonomy_data.js
"""

import json
import sys
from pathlib import Path
import pandas as pd

EXTERNAL_DATA_THRESHOLD = 5000


CSS_CONTENT = """
:root {
    --jsa-navy: #1e3a5f;
    --jsa-navy-dark: #0d2137;
    --jsa-navy-light: #2c5282;
    --jsa-teal: #00838f;
    --jsa-teal-light: #4fb3bf;
    --jsa-green: #2e7d32;
    --jsa-green-light: #4caf50;
    --jsa-gold: #c9a227;
    --jsa-orange: #e65100;
    --jsa-purple: #6a1b9a;
    --jsa-red: #c62828;
    --jsa-white: #ffffff;
    --jsa-grey-100: #f5f7fa;
    --jsa-grey-200: #e8ecf1;
    --jsa-grey-300: #d1d9e6;
    --jsa-grey-400: #9aa5b5;
    --jsa-grey-500: #6b7785;
    --jsa-grey-600: #4a5568;
    --jsa-grey-700: #2d3748;
    --jsa-grey-800: #1a202c;
    --shadow-sm: 0 1px 2px rgba(30, 58, 95, 0.05);
    --shadow-md: 0 4px 6px rgba(30, 58, 95, 0.07), 0 2px 4px rgba(30, 58, 95, 0.06);
    --shadow-lg: 0 10px 15px rgba(30, 58, 95, 0.1), 0 4px 6px rgba(30, 58, 95, 0.05);
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--jsa-grey-100);
    color: var(--jsa-grey-800);
    line-height: 1.6;
}

.header { background: linear-gradient(135deg, var(--jsa-navy) 0%, var(--jsa-navy-dark) 100%); color: var(--jsa-white); position: relative; }
.header-top { background: rgba(0,0,0,0.15); padding: 8px 0; font-size: 0.85rem; }
.header-top-content { max-width: 1400px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; gap: 12px; }
.gov-badge { display: flex; align-items: center; gap: 8px; color: var(--jsa-grey-200); }
.header-main { max-width: 1400px; margin: 0 auto; padding: 32px 24px; }
.header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
.header p { font-size: 1rem; opacity: 0.9; }
.header-logo { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.header-logo-icon { width: 48px; height: 48px; background: var(--jsa-teal); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; }
.header-logo-icon i { font-size: 1.5rem; color: white; }

.main-container { max-width: 1400px; margin: 0 auto; padding: 0 24px 48px; }

.stats-dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-top: -40px; padding: 0 24px; max-width: 1400px; margin-left: auto; margin-right: auto; position: relative; z-index: 10; }
.stat-card { background: var(--jsa-white); padding: 16px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); text-align: center; border: 1px solid var(--jsa-grey-200); }
.stat-card i { font-size: 1.5rem; color: var(--jsa-teal); margin-bottom: 4px; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: var(--jsa-navy); }
.stat-label { font-size: 0.75rem; color: var(--jsa-grey-500); text-transform: uppercase; letter-spacing: 0.5px; }

.view-tabs-container { background: var(--jsa-white); margin-top: 24px; border-radius: var(--radius-lg) var(--radius-lg) 0 0; box-shadow: var(--shadow-sm); border: 1px solid var(--jsa-grey-200); border-bottom: none; }
.view-tabs { display: flex; padding: 0 16px; gap: 4px; }
.view-tab { padding: 14px 20px; cursor: pointer; border: none; background: transparent; font-size: 0.9rem; font-weight: 500; color: var(--jsa-grey-500); border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 8px; }
.view-tab:hover { color: var(--jsa-navy); background: var(--jsa-grey-100); }
.view-tab.active { color: var(--jsa-teal); border-bottom-color: var(--jsa-teal); }

.content-area { background: var(--jsa-white); border-radius: 0 0 var(--radius-lg) var(--radius-lg); box-shadow: var(--shadow-md); border: 1px solid var(--jsa-grey-200); border-top: none; min-height: 500px; display: flex; }
.view-section { display: none; flex: 1; }
.view-section.active { display: flex; }

/* Tree Panel */
.tree-panel { flex: 1; display: flex; flex-direction: column; border-right: 1px solid var(--jsa-grey-200); min-width: 0; }
.tree-controls { padding: 16px; border-bottom: 1px solid var(--jsa-grey-200); display: flex; gap: 12px; flex-wrap: wrap; align-items: center; background: var(--jsa-grey-100); }
.tree-search { flex: 1; min-width: 200px; padding: 10px 14px; border: 2px solid var(--jsa-grey-200); border-radius: var(--radius-md); font-size: 0.9rem; }
.tree-search:focus { outline: none; border-color: var(--jsa-teal); }
.tree-container { flex: 1; overflow-y: auto; padding: 16px; background: var(--jsa-grey-100); }

.tree-node { margin: 2px 0; }
.node-row { display: flex; align-items: center; padding: 8px 12px; border-radius: var(--radius-sm); cursor: pointer; background: var(--jsa-white); border-left: 3px solid transparent; margin-bottom: 2px; }
.node-row:hover { background: var(--jsa-grey-100); border-left-color: var(--jsa-teal); }
.node-row.selected { background: rgba(0,131,143,0.1); border-left-color: var(--jsa-teal); }
.node-row.expanded { background: rgba(0,131,143,0.05); }
.node-toggle { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; margin-right: 6px; color: var(--jsa-grey-400); font-size: 0.7rem; transition: transform 0.15s; }
.node-row.expanded .node-toggle { transform: rotate(90deg); }
.node-icon { margin-right: 8px; font-size: 1rem; }
.node-domain .node-icon { color: var(--jsa-navy); }
.node-family .node-icon { color: var(--jsa-teal); }
.node-cluster .node-icon { color: var(--jsa-orange); }
.node-group .node-icon { color: var(--jsa-purple); }
.node-skill .node-icon { color: var(--jsa-green); }
.node-label { flex: 1; font-weight: 500; font-size: 0.9rem; color: var(--jsa-grey-700); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.node-domain .node-label { font-weight: 600; color: var(--jsa-navy); }
.node-badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; background: var(--jsa-grey-200); color: var(--jsa-grey-600); margin-left: 8px; }
.node-children { margin-left: 20px; padding-left: 12px; border-left: 1px solid var(--jsa-grey-200); display: none; }
.node-children.expanded { display: block; }

/* Detail Panel */
.detail-panel { width: 450px; min-width: 350px; max-width: 500px; background: var(--jsa-white); display: flex; flex-direction: column; border-left: 1px solid var(--jsa-grey-200); }
.detail-header { padding: 16px; border-bottom: 1px solid var(--jsa-grey-200); background: var(--jsa-grey-100); }
.detail-header h3 { font-size: 1rem; color: var(--jsa-grey-500); margin: 0; }
.detail-content { flex: 1; overflow-y: auto; padding: 20px; }
.detail-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--jsa-grey-400); text-align: center; padding: 40px; }
.detail-placeholder i { font-size: 3rem; margin-bottom: 16px; opacity: 0.5; }

.skill-card { animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.skill-card-header { margin-bottom: 16px; }
.skill-card-name { font-size: 1.25rem; font-weight: 600; color: var(--jsa-navy); display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.skill-card-name i { color: var(--jsa-green); }
.skill-card-id { display: inline-block; font-size: 0.75rem; color: var(--jsa-grey-500); background: var(--jsa-grey-100); padding: 4px 10px; border-radius: var(--radius-sm); font-family: 'Monaco', 'Consolas', monospace; }
.skill-card-description { font-size: 0.9rem; color: var(--jsa-grey-600); line-height: 1.6; margin: 16px 0; padding: 12px; background: var(--jsa-grey-100); border-radius: var(--radius-md); }
.skill-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--jsa-grey-200); }
.skill-section-title { font-size: 0.75rem; font-weight: 600; color: var(--jsa-grey-500); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }

.meta-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.meta-item { background: var(--jsa-grey-100); padding: 10px; border-radius: var(--radius-sm); }
.meta-label { font-size: 0.7rem; color: var(--jsa-grey-500); text-transform: uppercase; margin-bottom: 2px; }
.meta-value { font-size: 0.85rem; color: var(--jsa-grey-700); font-weight: 500; }
.confidence-bar { width: 100%; height: 4px; background: var(--jsa-grey-200); border-radius: 2px; margin-top: 4px; }
.confidence-fill { height: 100%; border-radius: 2px; }
.confidence-high { background: var(--jsa-green); }
.confidence-medium { background: var(--jsa-gold); }
.confidence-low { background: var(--jsa-orange); }

.dimension-list { display: flex; flex-wrap: wrap; gap: 6px; }
.dim-badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
.dim-category { background: #fff8e1; color: #f57f17; }
.dim-complexity { background: #e3f2fd; color: #1565c0; }
.dim-transfer { background: #f3e5f5; color: #7b1fa2; }
.dim-digital { background: #e0f2f1; color: #00695c; }
.dim-future { background: #fff3e0; color: #e65100; }
.dim-nature { background: #fce4ec; color: #c2185b; }

.tag-list { display: flex; flex-wrap: wrap; gap: 4px; }
.tag { display: inline-block; padding: 3px 8px; border-radius: var(--radius-sm); font-size: 0.75rem; }
.tag-alt { background: var(--jsa-grey-100); color: var(--jsa-grey-600); }
.tag-code { background: #e8eaf6; color: #3949ab; font-family: monospace; }
.tag-keyword { background: #e0f7fa; color: #00838f; }
.tag-more { background: var(--jsa-grey-200); color: var(--jsa-grey-500); font-style: italic; }

.related-skill { display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px; background: rgba(106,27,154,0.08); border-radius: var(--radius-md); font-size: 0.8rem; color: var(--jsa-purple); margin: 3px; cursor: pointer; }
.related-skill:hover { background: rgba(106,27,154,0.15); }
.similarity-score { font-size: 0.7rem; color: var(--jsa-grey-500); }

/* Table View */
.table-view-content { flex: 1; padding: 20px; flex-direction: column; display: flex; }
.table-controls { margin-bottom: 16px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.export-buttons { display: flex; gap: 10px; }
.btn-custom { padding: 8px 16px; border-radius: var(--radius-md); border: none; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 0.85rem; }
.btn-primary-custom { background: var(--jsa-teal); color: var(--jsa-white); }
.btn-primary-custom:hover { background: var(--jsa-navy); }
.btn-outline-custom { background: var(--jsa-white); color: var(--jsa-navy); border: 2px solid var(--jsa-grey-300); }
.btn-outline-custom:hover { border-color: var(--jsa-teal); color: var(--jsa-teal); }
.filter-group { display: flex; gap: 8px; flex-wrap: wrap; flex: 1; }
.filter-group select, .filter-group input { padding: 8px 12px; border: 2px solid var(--jsa-grey-200); border-radius: var(--radius-md); font-size: 0.85rem; background: var(--jsa-white); min-width: 150px; }
.table-wrapper { flex: 1; overflow: auto; border: 1px solid var(--jsa-grey-200); border-radius: var(--radius-md); }
.skills-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.skills-table thead { position: sticky; top: 0; z-index: 10; }
.skills-table th { background: var(--jsa-navy); color: white; padding: 12px 10px; text-align: left; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
.skills-table td { padding: 10px; border-bottom: 1px solid var(--jsa-grey-200); max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.skills-table tbody tr:hover { background: rgba(0,131,143,0.03); }
.skills-table tbody tr { cursor: pointer; }
.table-pagination { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; margin-top: 12px; border-top: 1px solid var(--jsa-grey-200); }
.pagination-info { font-size: 0.85rem; color: var(--jsa-grey-600); }
.pagination-buttons { display: flex; gap: 4px; }
.page-btn { padding: 6px 12px; border: 1px solid var(--jsa-grey-300); background: white; border-radius: var(--radius-sm); cursor: pointer; font-size: 0.85rem; }
.page-btn:hover { background: var(--jsa-grey-100); }
.page-btn.active { background: var(--jsa-teal); color: white; border-color: var(--jsa-teal); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ═══════════════════════════════════════════════════════════════
   ARCHETYPE EXPLORER STYLES
   ═══════════════════════════════════════════════════════════════ */

.archetype-view-content { flex: 1; padding: 20px; display: flex; flex-direction: column; }

.arch-layout { display: grid; grid-template-columns: 320px 1fr 420px; gap: 20px; min-height: 500px; align-items: start; }

.arch-sidebar { border-right: 1px solid var(--jsa-grey-200); padding-right: 20px; }
.arch-sidebar-search { margin-bottom: 16px; }
.arch-sidebar-search input { width: 100%; padding: 10px 12px; border: 2px solid var(--jsa-grey-200); border-radius: var(--radius-md); font-size: 0.9rem; }
.arch-sidebar-search input:focus { outline: none; border-color: var(--jsa-teal); }

.arch-card { background: var(--jsa-grey-100); border-radius: var(--radius-md); padding: 12px; margin-bottom: 10px; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; }
.arch-card:hover { background: var(--jsa-grey-200); }
.arch-card.active { border-color: var(--jsa-teal); background: rgba(0,131,143,0.08); }
.arch-card-label { font-weight: 600; color: var(--jsa-navy); font-size: 0.85rem; margin-bottom: 6px; }
.arch-card-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }
.arch-card-stats { font-size: 0.75rem; color: var(--jsa-grey-500); display: flex; gap: 12px; }

.arch-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
.arch-badge-nat { background: #fff3e0; color: #e65100; }
.arch-badge-trf { background: #f3e5f5; color: #7b1fa2; }
.arch-badge-cog { background: #e3f2fd; color: #1565c0; }

.sc-card { background: var(--jsa-white); border: 1px solid var(--jsa-grey-200); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s; }
.sc-card:hover { border-color: var(--jsa-teal); box-shadow: var(--shadow-md); }
.sc-card.selected { border-color: var(--jsa-teal); background: rgba(0,131,143,0.03); }
.sc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.sc-label { font-weight: 600; font-size: 0.9rem; color: var(--jsa-navy); flex: 1; }
.sc-badges { display: flex; gap: 6px; flex-shrink: 0; }

.prog-badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.prog-badge.full { background: #e8f5e9; color: #2e7d32; }
.prog-badge.partial { background: #fff8e1; color: #f57f17; }
.prog-badge.flat { background: var(--jsa-grey-100); color: var(--jsa-grey-500); }
.prog-badge.sparse { background: #fce4ec; color: #c2185b; }

.ladder-mini { display: flex; align-items: center; gap: 2px; margin: 10px 0; padding: 8px 0; }
.ladder-dot { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 700; color: white; background: var(--jsa-grey-300); z-index: 2; }
.ladder-dot.on { background: var(--jsa-teal); }
.ladder-dot.gap { background: transparent; border: 2px dashed var(--jsa-grey-300); color: var(--jsa-grey-400); }
.ladder-dot-count { font-size: 0.65rem; color: var(--jsa-grey-500); margin-top: 2px; text-align: center; }
.ladder-conn { height: 2px; flex: 0.5; background: var(--jsa-grey-300); }
.ladder-conn.on { background: var(--jsa-teal); }
.ladder-conn.gap { background: transparent; border-top: 2px dashed var(--jsa-grey-300); }

.arch-detail { border-left: 1px solid var(--jsa-grey-200); padding-left: 20px; align-self: start; }
.arch-detail-head h3 { font-size: 0.9rem; color: var(--jsa-grey-500); margin: 0 0 16px; display: flex; align-items: center; gap: 8px; padding-bottom: 12px; border-bottom: 1px solid var(--jsa-grey-200); }

.ladder-full { margin: 16px 0; }
.ladder-rung { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-left: 3px solid var(--jsa-grey-200); margin-left: 12px; padding-left: 16px; position: relative; }
.ladder-rung::before { content: ''; position: absolute; left: -8px; top: 16px; width: 14px; height: 14px; border-radius: 50%; background: var(--jsa-teal); border: 2px solid var(--jsa-white); }
.ladder-rung.gap-rung { border-left-style: dashed; padding: 6px 0 6px 16px; color: var(--jsa-grey-400); font-style: italic; font-size: 0.8rem; }
.ladder-rung.gap-rung::before { background: var(--jsa-grey-300); width: 10px; height: 10px; left: -6px; top: 10px; }
.rung-lvl { background: var(--jsa-teal); color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
.rung-body { flex: 1; }
.rung-name { font-size: 0.75rem; color: var(--jsa-grey-500); margin-bottom: 4px; }
.rung-skills { display: flex; flex-direction: column; gap: 3px; }
.rung-skill { font-size: 0.8rem; color: var(--jsa-grey-700); padding: 3px 0; }
.rung-asced-tags { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.rung-asced-tag { font-size: 0.65rem; padding: 1px 5px; border-radius: 3px; background: #fff8e1; color: #ff8f00; }

.asced-spread-list { display: flex; flex-direction: column; gap: 4px; }
.asced-spread-item { display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; padding: 4px 0; }
.asced-spread-name { color: var(--jsa-grey-600); }
.asced-spread-count { font-weight: 600; color: var(--jsa-navy); }
.asced-code-badge { display: inline-block; background: #e3f2fd; color: #1565c0; font-family: monospace; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; margin-right: 4px; }

/* Loading */
.loading-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1000; }
.loading-spinner { width: 50px; height: 50px; border: 4px solid var(--jsa-grey-200); border-top-color: var(--jsa-teal); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { margin-top: 16px; color: var(--jsa-grey-600); font-size: 0.9rem; }

@media (max-width: 1200px) {
    .arch-layout { grid-template-columns: 280px 1fr; }
    .arch-detail { display: none; }
}
@media (max-width: 1024px) {
    .detail-panel { display: none; }
    .tree-panel { border-right: none; }
}
@media (max-width: 768px) {
    .header h1 { font-size: 1.5rem; }
    .stats-dashboard { grid-template-columns: repeat(2, 1fr); margin-top: -24px; }
    .arch-layout { grid-template-columns: 1fr; }
}
"""


BODY_CONTENT = """
<div id="loadingOverlay" class="loading-overlay">
    <div class="loading-spinner"></div>
    <div class="loading-text">Loading taxonomy data...</div>
    <div style="margin-top: 24px; font-size: 0.8rem; color: #9aa5b5; max-width: 400px; text-align: center;">
        If loading takes too long, make sure the data JS file is in the same folder as this HTML file.
    </div>
</div>

<div class="header">
    <div class="header-top">
        <div class="header-top-content">
            <div class="gov-badge"><i class="bi bi-building"></i><span>Australian Government</span></div>
        </div>
    </div>
    <div class="header-main">
        <div class="header-logo">
            <div class="header-logo-icon"><i class="bi bi-diagram-3"></i></div>
            <div>
                <h1>VET Skills Taxonomy Explorer</h1>
                <p>Comprehensive taxonomy with ability archetypes and progression ladders</p>
            </div>
        </div>
    </div>
</div>

<div class="stats-dashboard">
    <div class="stat-card"><i class="bi bi-mortarboard-fill"></i><div class="stat-value" id="totalSkills">-</div><div class="stat-label">Total Skills</div></div>
    <div class="stat-card"><i class="bi bi-folder2-open"></i><div class="stat-value" id="totalDomains">-</div><div class="stat-label">Domains</div></div>
    <div class="stat-card"><i class="bi bi-collection"></i><div class="stat-value" id="totalFamilies">-</div><div class="stat-label">Families</div></div>
    <div class="stat-card"><i class="bi bi-diagram-3-fill"></i><div class="stat-value" id="totalArchetypes">-</div><div class="stat-label">Archetypes</div></div>
    <div class="stat-card"><i class="bi bi-upc-scan"></i><div class="stat-value" id="totalCodes">-</div><div class="stat-label">Unit Codes</div></div>
    <div class="stat-card"><i class="bi bi-tags"></i><div class="stat-value" id="totalKeywords">-</div><div class="stat-label">Keywords</div></div>
</div>

<div class="main-container">
    <div class="view-tabs-container">
        <div class="view-tabs">
            <button class="view-tab active" data-view="tree"><i class="bi bi-diagram-3"></i> Hierarchy View</button>
            <button class="view-tab" data-view="archetypes"><i class="bi bi-bar-chart-steps"></i> Archetypes</button>
            <button class="view-tab" data-view="table"><i class="bi bi-table"></i> Table View</button>
        </div>
    </div>

    <div class="content-area">
        <!-- Tree View -->
        <div class="view-section active" id="treeView">
            <div class="tree-panel">
                <div class="tree-controls">
                    <input type="text" class="tree-search" id="treeSearch" placeholder="Search skills, domains, codes...">
                    <button class="btn-custom btn-outline-custom" onclick="expandAllDomains()"><i class="bi bi-arrows-expand"></i> Expand Domains</button>
                    <button class="btn-custom btn-outline-custom" onclick="collapseAll()"><i class="bi bi-arrows-collapse"></i> Collapse All</button>
                </div>
                <div class="tree-container" id="treeContainer"></div>
            </div>
            <div class="detail-panel" id="detailPanel">
                <div class="detail-header"><h3><i class="bi bi-info-circle"></i> Skill Details</h3></div>
                <div class="detail-content" id="detailContent">
                    <div class="detail-placeholder"><i class="bi bi-hand-index"></i><p>Select a skill from the tree to view details</p></div>
                </div>
            </div>
        </div>

        <!-- Archetypes View -->
        <div class="view-section" id="archetypesView">
            <div class="archetype-view-content" id="archetypeViewContent">
                <p style="padding:20px;color:var(--jsa-grey-500);">Loading archetypes...</p>
            </div>
        </div>

        <!-- Table View -->
        <div class="view-section" id="tableView">
            <div class="table-view-content">
                <div class="table-controls">
                    <div class="export-buttons">
                        <button class="btn-custom btn-primary-custom" onclick="exportToExcel()"><i class="bi bi-file-earmark-excel"></i> Export Excel</button>
                        <button class="btn-custom btn-outline-custom" onclick="exportToCSV()"><i class="bi bi-file-earmark-spreadsheet"></i> CSV</button>
                    </div>
                    <div class="filter-group">
                        <input type="text" id="tableSearch" placeholder="Search skills...">
                        <select id="filterDomain"><option value="">All Domains</option></select>
                        <select id="filterCategory"><option value="">All Categories</option></select>
                    </div>
                </div>
                <div class="table-wrapper">
                    <table class="skills-table" id="skillsTable">
                        <thead><tr><th>ID</th><th>Skill Name</th><th>Domain</th><th>Family</th><th>Category</th><th>Level</th><th>Confidence</th></tr></thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
                <div class="table-pagination" id="tablePagination"></div>
            </div>
        </div>
    </div>
</div>
"""


JAVASCRIPT_CONTENT = r"""
let taxonomyData = null;
let flatSkillsData = [];
let skillsIndex = new Map();
let selectedSkillId = null;
let archetypesData = [];

let currentPage = 1;
const pageSize = 50;
let filteredData = [];

document.addEventListener('DOMContentLoaded', function() {
    try {
        if (typeof TAXONOMY_DATA !== 'undefined') taxonomyData = TAXONOMY_DATA;
        else if (typeof EMBEDDED_DATA !== 'undefined') taxonomyData = EMBEDDED_DATA;
        else throw new Error('No taxonomy data found.');

        flatSkillsData = flattenTaxonomy(taxonomyData);
        flatSkillsData.forEach(skill => skillsIndex.set(skill.id, skill));
        filteredData = [...flatSkillsData];
        archetypesData = taxonomyData.archetypes || [];

        initializeStats();
        renderTree();
        initializeArchetypes();
        initializeTable();
        initializeEventListeners();

        document.getElementById('loadingOverlay').style.display = 'none';
    } catch (error) {
        console.error('Failed to load taxonomy:', error);
        document.querySelector('.loading-text').textContent = 'Error: ' + error.message;
        document.querySelector('.loading-text').style.color = '#c62828';
    }
});

function flattenTaxonomy(node, path = {}, result = []) {
    const cp = { ...path };
    if (node.type === 'domain') cp.domain = node.name;
    else if (node.type === 'family') cp.family = node.name;
    else if (node.type === 'group') cp.group = node.name;
    if (node.skills) node.skills.forEach(skill => result.push({ ...skill, ...cp }));
    if (node.children) node.children.forEach(child => flattenTaxonomy(child, cp, result));
    return result;
}

function initializeStats() {
    const stats = taxonomyData.metadata?.statistics || {};
    document.getElementById('totalSkills').textContent = (stats.total_skills || flatSkillsData.length).toLocaleString();
    document.getElementById('totalDomains').textContent = stats.total_domains || taxonomyData.children?.length || 0;
    document.getElementById('totalFamilies').textContent = stats.total_families || '-';
    document.getElementById('totalArchetypes').textContent = archetypesData.length || 0;
    document.getElementById('totalCodes').textContent = (stats.total_related_codes || countUniqueCodes()).toLocaleString();
    document.getElementById('totalKeywords').textContent = (stats.total_related_keywords || '-').toLocaleString();
}

function countUniqueCodes() { const c = new Set(); flatSkillsData.forEach(s => (s.all_related_codes||[]).forEach(x => c.add(x))); return c.size; }

// ══════════════════════════════════════════════════════════
//  TREE VIEW
// ══════════════════════════════════════════════════════════

function renderTree() {
    const container = document.getElementById('treeContainer');
    container.innerHTML = '';
    if (taxonomyData.children) taxonomyData.children.forEach(domain => container.appendChild(createNodeElement(domain, 0)));
}

function createNodeElement(node, depth) {
    const div = document.createElement('div');
    div.className = 'tree-node';
    div.dataset.nodeId = node.id || node.name;
    div.dataset.loaded = 'false';
    const hasChildren = (node.children && node.children.length > 0) || (node.skills && node.skills.length > 0);
    const row = document.createElement('div');
    row.className = 'node-row node-' + (node.type || 'group');
    const toggle = document.createElement('span');
    toggle.className = 'node-toggle';
    toggle.innerHTML = hasChildren ? '<i class="bi bi-chevron-right"></i>' : '';
    row.appendChild(toggle);
    const icon = document.createElement('i');
    icon.className = 'bi node-icon ' + getIconClass(node.type);
    row.appendChild(icon);
    const label = document.createElement('span');
    label.className = 'node-label';
    label.textContent = node.name;
    label.title = node.name;
    row.appendChild(label);
    const size = node.statistics?.size || node.size || node.skills?.length;
    if (size) { const badge = document.createElement('span'); badge.className = 'node-badge'; badge.textContent = size; row.appendChild(badge); }
    div.appendChild(row);
    if (hasChildren) { const cd = document.createElement('div'); cd.className = 'node-children'; div.appendChild(cd); div._nodeData = node; }
    row.addEventListener('click', (e) => {
        e.stopPropagation();
        if (node.type === 'skill' || (node.skills && node.skills.length === 1 && !node.children)) {
            showSkillDetail(node.type === 'skill' ? node : node.skills[0]);
        } else if (hasChildren) toggleNodeExpansion(div);
    });
    return div;
}

function toggleNodeExpansion(nodeDiv) {
    const row = nodeDiv.querySelector('.node-row');
    const cd = nodeDiv.querySelector('.node-children');
    if (!cd) return;
    if (cd.classList.contains('expanded')) { cd.classList.remove('expanded'); row.classList.remove('expanded'); }
    else {
        if (nodeDiv.dataset.loaded === 'false' && nodeDiv._nodeData) { loadNodeChildren(nodeDiv, cd); nodeDiv.dataset.loaded = 'true'; }
        cd.classList.add('expanded'); row.classList.add('expanded');
    }
}

function loadNodeChildren(nodeDiv, cd) {
    const node = nodeDiv._nodeData;
    if (node.children) node.children.forEach(child => cd.appendChild(createNodeElement(child, 1)));
    if (node.skills) node.skills.forEach(skill => {
        const sr = document.createElement('div');
        sr.className = 'node-row node-skill';
        sr.innerHTML = '<span class="node-toggle"></span><i class="bi bi-mortarboard node-icon"></i><span class="node-label" title="'+skill.name+'">'+skill.name+'</span><span class="node-badge" style="font-family:monospace;font-size:0.65rem;">'+(skill.id||'')+'</span>';
        sr.addEventListener('click', (e) => { e.stopPropagation(); showSkillDetail(skill); document.querySelectorAll('.node-row.selected').forEach(r => r.classList.remove('selected')); sr.classList.add('selected'); });
        cd.appendChild(sr);
    });
}

function getIconClass(type) { return {'domain':'bi-folder2-open','family':'bi-collection','cluster':'bi-grid-3x3-gap','group':'bi-layers','skill':'bi-mortarboard'}[type]||'bi-circle-fill'; }
function expandAllDomains() { document.querySelectorAll('.tree-node').forEach(n => { if (n._nodeData?.type === 'domain') { const cd = n.querySelector('.node-children'); if (cd) { if (n.dataset.loaded==='false' && n._nodeData) { loadNodeChildren(n, cd); n.dataset.loaded='true'; } cd.classList.add('expanded'); n.querySelector('.node-row')?.classList.add('expanded'); } } }); }
function collapseAll() { document.querySelectorAll('.node-children').forEach(c => c.classList.remove('expanded')); document.querySelectorAll('.node-row').forEach(r => r.classList.remove('expanded')); }

function showSkillDetail(skill) {
    const content = document.getElementById('detailContent');
    selectedSkillId = skill.id;
    const dims = skill.dimensions || {};
    const confPct = ((skill.confidence||0)*100).toFixed(0);
    const confClass = confPct >= 80 ? 'high' : (confPct >= 50 ? 'medium' : 'low');
    let html = '<div class="skill-card"><div class="skill-card-header"><div class="skill-card-name"><i class="bi bi-mortarboard-fill"></i>'+skill.name+'</div><span class="skill-card-id">'+(skill.id||'N/A')+'</span></div>';
    if (skill.description) html += '<div class="skill-card-description">'+skill.description+'</div>';
    html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-bar-chart"></i> Metrics</div><div class="meta-grid"><div class="meta-item"><div class="meta-label">Confidence</div><div class="meta-value">'+confPct+'%</div><div class="confidence-bar"><div class="confidence-fill confidence-'+confClass+'" style="width:'+confPct+'%"></div></div></div><div class="meta-item"><div class="meta-label">Level</div><div class="meta-value">'+(skill.level||'N/A')+'</div></div>';
    if (skill.code) html += '<div class="meta-item"><div class="meta-label">Primary Code</div><div class="meta-value" style="font-family:monospace">'+skill.code+'</div></div>';
    if (skill.context) html += '<div class="meta-item"><div class="meta-label">Context</div><div class="meta-value">'+formatLabel(skill.context)+'</div></div>';
    html += '</div></div>';
    html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-tags"></i> Dimensions</div><div class="dimension-list">';
    if (skill.category) html += '<span class="dim-badge dim-category"><i class="bi bi-bookmark"></i> '+skill.category+'</span>';
    if (dims.complexity_level) html += '<span class="dim-badge dim-complexity">Level '+dims.complexity_level+'</span>';
    if (dims.transferability) html += '<span class="dim-badge dim-transfer">'+formatLabel(dims.transferability)+'</span>';
    html += '</div></div>';
    const alt = skill.alternative_titles||[];
    if (alt.length) { html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-card-heading"></i> Alternative Titles ('+alt.length+')</div><div class="tag-list">'+alt.slice(0,10).map(t=>'<span class="tag tag-alt">'+t+'</span>').join('')+(alt.length>10?'<span class="tag tag-more">+'+( alt.length-10)+' more</span>':'')+'</div></div>'; }
    const codes = skill.all_related_codes||[];
    if (codes.length) { html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-upc-scan"></i> Related Codes ('+codes.length+')</div><div class="tag-list">'+codes.slice(0,12).map(c=>'<span class="tag tag-code">'+c+'</span>').join('')+(codes.length>12?'<span class="tag tag-more">+'+(codes.length-12)+' more</span>':'')+'</div></div>'; }
    const kws = skill.all_related_kw||[];
    if (kws.length) { html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-key"></i> Keywords ('+kws.length+')</div><div class="tag-list">'+kws.slice(0,15).map(k=>'<span class="tag tag-keyword">'+k+'</span>').join('')+(kws.length>15?'<span class="tag tag-more">+'+(kws.length-15)+' more</span>':'')+'</div></div>'; }
    const rel = skill.relationships?.related||[];
    if (rel.length) { html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-link-45deg"></i> Related Skills</div><div>'+rel.slice(0,8).map(r=>'<span class="related-skill" onclick="navigateToSkill(\''+r.skill_id+'\')">'+r.skill_name+'<span class="similarity-score">'+(r.similarity?(r.similarity*100).toFixed(0)+'%':'')+'</span></span>').join('')+'</div></div>'; }
    html += '</div>';
    content.innerHTML = html;
}

function navigateToSkill(sid) { const s = skillsIndex.get(sid); if (s) showSkillDetail(s); }
function formatLabel(s) { if (!s) return ''; return s.replace(/_/g,' ').replace(/\b\w/g, c=>c.toUpperCase()); }

let searchTimeout;
document.getElementById('treeSearch')?.addEventListener('input', (e) => { clearTimeout(searchTimeout); searchTimeout = setTimeout(()=>performTreeSearch(e.target.value), 300); });

function performTreeSearch(query) {
    if (!query || query.length < 2) { document.querySelectorAll('.tree-node').forEach(n => n.style.display=''); return; }
    const q = query.toLowerCase();
    const matches = flatSkillsData.filter(s => s.name?.toLowerCase().includes(q) || s.id?.toLowerCase().includes(q) || s.domain?.toLowerCase().includes(q) || (s.all_related_codes||[]).some(c=>c.toLowerCase().includes(q))).slice(0,100);
    const container = document.getElementById('treeContainer');
    container.innerHTML = '<div style="padding:10px;color:var(--jsa-grey-500);">Found '+matches.length+' results'+(matches.length>=100?' (showing first 100)':'')+'</div>';
    matches.forEach(skill => {
        const row = document.createElement('div');
        row.className = 'node-row node-skill';
        row.innerHTML = '<span class="node-toggle"></span><i class="bi bi-mortarboard node-icon"></i><span class="node-label">'+skill.name+'</span><span class="node-badge" style="font-size:0.65rem;">'+(skill.domain||'')+'</span>';
        row.addEventListener('click', () => showSkillDetail(skill));
        container.appendChild(row);
    });
    const btn = document.createElement('button');
    btn.className = 'btn-custom btn-outline-custom';
    btn.style.margin = '10px';
    btn.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i> Reset Tree';
    btn.onclick = () => { document.getElementById('treeSearch').value=''; renderTree(); };
    container.prepend(btn);
}

// ══════════════════════════════════════════════════════════
//  ARCHETYPE EXPLORER
// ══════════════════════════════════════════════════════════

function initializeArchetypes() {
    const container = document.getElementById('archetypeViewContent');
    if (!archetypesData.length) { container.innerHTML = '<p style="padding:20px;color:var(--jsa-grey-500);">No archetype data available. Run the pipeline with archetype clustering enabled.</p>'; return; }

    const sorted = [...archetypesData].sort((a,b) => b.total_skills - a.total_skills);
    let sidebar = '<div class="arch-sidebar-search"><input type="text" placeholder="Search archetypes..." id="archSearch"></div>';

    for (const arch of sorted) {
        const scCount = arch.sub_clusters?.length || 0;
        const ascedCount = Object.keys(arch.asced_coverage||{}).length;
        const levels = Object.keys(arch.level_distribution||{}).sort();
        const lr = levels.length > 0 ? 'L'+levels[0]+'-'+levels[levels.length-1] : '-';
        sidebar += '<div class="arch-card" data-aid="'+arch.archetype_id+'"><div class="arch-card-label">'+arch.label+'</div><div class="arch-card-badges"><span class="arch-badge arch-badge-nat">'+arch.nat.name+'</span><span class="arch-badge arch-badge-trf">'+arch.trf.name+'</span><span class="arch-badge arch-badge-cog">'+arch.cog.name+'</span></div><div class="arch-card-stats"><span><i class="bi bi-people"></i> '+arch.total_skills+'</span><span><i class="bi bi-collection"></i> '+scCount+'</span><span><i class="bi bi-mortarboard"></i> '+ascedCount+'</span><span><i class="bi bi-bar-chart-steps"></i> '+lr+'</span></div></div>';
    }

    container.innerHTML = '<div class="arch-layout"><div class="arch-sidebar">'+sidebar+'</div><div id="archMain"><p style="color:var(--jsa-grey-500);padding:20px;">Select an archetype to view sub-clusters</p></div><div class="arch-detail"><div class="arch-detail-head"><h3><i class="bi bi-bar-chart-steps"></i> Progression Ladder</h3></div><div id="archDetailPanel" class="detail-placeholder"><i class="bi bi-bar-chart-steps"></i><p>Select a sub-cluster to view progression</p></div></div></div>';

    container.querySelectorAll('.arch-card').forEach(card => {
        card.addEventListener('click', () => {
            container.querySelectorAll('.arch-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            loadSubClusters(card.dataset.aid);
        });
    });

    document.getElementById('archSearch')?.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        container.querySelectorAll('.arch-card').forEach(card => {
            const a = archetypesData.find(x => x.archetype_id === card.dataset.aid);
            const match = !q || q.length < 2 || a?.label?.toLowerCase().includes(q) || a?.nat?.name?.toLowerCase().includes(q) || a?.trf?.name?.toLowerCase().includes(q) || a?.cog?.name?.toLowerCase().includes(q);
            card.style.display = match ? '' : 'none';
        });
    });
}

function loadSubClusters(aid) {
    const arch = archetypesData.find(a => a.archetype_id === aid);
    if (!arch) return;
    const el = document.getElementById('archMain');
    let html = '<div style="margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--jsa-grey-200);"><h3 style="font-size:1rem;color:var(--jsa-navy);margin-bottom:4px;">'+arch.label+'</h3><div style="font-size:0.85rem;color:var(--jsa-grey-600);">'+arch.total_skills+' skills across '+(arch.sub_clusters?.length||0)+' sub-clusters</div></div>';

    if (!arch.sub_clusters?.length) { el.innerHTML = html + '<p style="color:var(--jsa-grey-500);">No sub-clusters</p>'; return; }

    const sortedSC = [...arch.sub_clusters].sort((a,b) => {
        const o = {full:0, partial:1, sparse:2, flat:3};
        const d = (o[a.progression_type]||9) - (o[b.progression_type]||9);
        return d !== 0 ? d : b.total_skills - a.total_skills;
    });

    for (const sc of sortedSC) {
        const prog = sc.progression || [];
        const levels = new Set(prog.map(r => r.level));
        const minL = sc.level_span?.[0] || 1;
        const maxL = sc.level_span?.[1] || 7;

        let ladder = '<div class="ladder-mini">';
        for (let l = minL; l <= maxL; l++) {
            if (l > minL) {
                const cls = (levels.has(l-1) && levels.has(l)) ? 'on' : 'gap';
                ladder += '<div class="ladder-conn '+cls+'"></div>';
            }
            const rung = prog.find(r => r.level === l);
            if (rung) ladder += '<div style="display:flex;flex-direction:column;align-items:center;flex:1"><div class="ladder-dot on">'+l+'</div><div class="ladder-dot-count">'+rung.skill_count+'</div></div>';
            else ladder += '<div style="display:flex;flex-direction:column;align-items:center;flex:1"><div class="ladder-dot gap">'+l+'</div></div>';
        }
        ladder += '</div>';

        const ac = Object.keys(sc.asced_spread||{}).length;
        html += '<div class="sc-card" data-cid="'+sc.cluster_id+'" data-aid="'+aid+'"><div class="sc-header"><div class="sc-label">'+sc.label+'</div><div class="sc-badges"><span class="prog-badge '+sc.progression_type+'">'+sc.progression_type+'</span><span class="node-badge">'+sc.total_skills+'</span></div></div>'+ladder+'<div style="font-size:0.75rem;color:var(--jsa-grey-500);display:flex;gap:12px;"><span><i class="bi bi-mortarboard"></i> '+ac+' ASCED field'+(ac!==1?'s':'')+'</span><span><i class="bi bi-bar-chart-steps"></i> Level '+(sc.level_span?.[0]||'?')+' – '+(sc.level_span?.[1]||'?')+'</span><span>Sim: '+(sc.avg_intra_similarity*100).toFixed(0)+'%</span></div></div>';
    }

    el.innerHTML = html;
    el.querySelectorAll('.sc-card').forEach(card => {
        card.addEventListener('click', () => {
            el.querySelectorAll('.sc-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showSubClusterDetail(card.dataset.aid, card.dataset.cid);
        });
    });
}

function showSubClusterDetail(aid, cid) {
    const arch = archetypesData.find(a => a.archetype_id === aid);
    if (!arch) return;
    const sc = arch.sub_clusters?.find(s => s.cluster_id === cid);
    if (!sc) return;
    const panel = document.getElementById('archDetailPanel');
    panel.classList.remove('detail-placeholder');

    let html = '<div class="skill-card"><div style="margin-bottom:16px;"><div class="skill-card-name"><i class="bi bi-collection"></i> '+sc.label+'</div><span class="skill-card-id">'+sc.cluster_id+'</span></div>';

    // Full progression ladder
    html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-bar-chart-steps"></i> Progression Ladder</div><div class="ladder-full">';
    const prog = sc.progression || [];
    const minL = sc.level_span?.[0] || 1;
    const maxL = sc.level_span?.[1] || 7;
    const gaps = sc.level_gaps || [];

    for (let l = minL; l <= maxL; l++) {
        const rung = prog.find(r => r.level === l);
        if (rung) {
            html += '<div class="ladder-rung"><span class="rung-lvl">LVL '+rung.level+'</span><div class="rung-body"><div class="rung-name">'+rung.level_name+' ('+rung.skill_count+' skill'+(rung.skill_count!==1?'s':'')+')</div><div class="rung-skills">'+rung.skill_names.slice(0,8).map(n=>'<div class="rung-skill">'+n+'</div>').join('')+(rung.skill_names.length>8?'<div class="rung-skill" style="color:var(--jsa-grey-400);font-style:italic;">+'+(rung.skill_names.length-8)+' more</div>':'')+'</div>';
            if (rung.asced_names?.length) html += '<div class="rung-asced-tags">'+rung.asced_names.slice(0,5).map(n=>'<span class="rung-asced-tag">'+n+'</span>').join('')+(rung.asced_names.length>5?'<span class="rung-asced-tag">+'+(rung.asced_names.length-5)+'</span>':'')+'</div>';
            html += '</div></div>';
        } else if (gaps.includes(l)) {
            html += '<div class="ladder-rung gap-rung">Level '+l+' — no skills (gap)</div>';
        }
    }
    html += '</div></div>';

    // ASCED spread
    if (sc.asced_spread && Object.keys(sc.asced_spread).length) {
        html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-mortarboard"></i> ASCED Field Spread</div><div class="asced-spread-list">';
        const sorted = Object.entries(sc.asced_spread).sort((a,b)=>b[1]-a[1]);
        for (const [code, count] of sorted.slice(0,10)) {
            const name = sc.asced_names?.[code] || code;
            html += '<div class="asced-spread-item"><span class="asced-spread-name"><span class="asced-code-badge">'+code+'</span>'+name+'</span><span class="asced-spread-count">'+count+'</span></div>';
        }
        if (sorted.length > 10) html += '<div style="font-size:0.75rem;color:var(--jsa-grey-400);font-style:italic;">+'+(sorted.length-10)+' more fields</div>';
        html += '</div></div>';
    }

    // Representative skills
    if (sc.representative_skills?.length) {
        html += '<div class="skill-section"><div class="skill-section-title"><i class="bi bi-star"></i> Representative Skills</div><div style="display:flex;flex-direction:column;gap:6px;">';
        sc.representative_skills.forEach(rs => { html += '<div style="display:flex;justify-content:space-between;padding:6px 8px;background:var(--jsa-grey-100);border-radius:4px;font-size:0.85rem;"><span>'+rs.name+'</span>'+(rs.level?'<span style="font-size:0.7rem;color:var(--jsa-grey-500);">L'+rs.level+'</span>':'')+'</div>'; });
        html += '</div></div>';
    }

    html += '</div>';
    panel.innerHTML = html;
}

// ══════════════════════════════════════════════════════════
//  TABLE VIEW
// ══════════════════════════════════════════════════════════

function initializeTable() {
    const domains = [...new Set(flatSkillsData.map(s=>s.domain).filter(Boolean))].sort();
    const ds = document.getElementById('filterDomain');
    domains.forEach(d => { const o = document.createElement('option'); o.value=d; o.textContent=d; ds.appendChild(o); });
    const cats = [...new Set(flatSkillsData.map(s=>s.category).filter(Boolean))].sort();
    const cs = document.getElementById('filterCategory');
    cats.forEach(c => { const o = document.createElement('option'); o.value=c; o.textContent=formatLabel(c); cs.appendChild(o); });
    renderTable();
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    const start = (currentPage-1)*pageSize;
    const pd = filteredData.slice(start, start+pageSize);
    tbody.innerHTML = pd.map(s => '<tr onclick="showSkillDetail(skillsIndex.get(\''+s.id+'\'))"><td style="font-family:monospace;font-size:0.8rem;">'+(s.id||'-')+'</td><td>'+s.name+'</td><td>'+(s.domain||'-')+'</td><td>'+(s.family||'-')+'</td><td>'+(formatLabel(s.category)||'-')+'</td><td>'+(s.level||'-')+'</td><td>'+(s.confidence?(s.confidence*100).toFixed(0)+'%':'-')+'</td></tr>').join('');
    renderPagination();
}

function renderPagination() {
    const tp = Math.ceil(filteredData.length/pageSize);
    document.getElementById('tablePagination').innerHTML = '<div class="pagination-info">Showing '+((currentPage-1)*pageSize+1)+'-'+Math.min(currentPage*pageSize,filteredData.length)+' of '+filteredData.length.toLocaleString()+'</div><div class="pagination-buttons"><button class="page-btn" onclick="goToPage(1)"'+(currentPage===1?' disabled':'')+'><i class="bi bi-chevron-double-left"></i></button><button class="page-btn" onclick="goToPage('+(currentPage-1)+')"'+(currentPage===1?' disabled':'')+'><i class="bi bi-chevron-left"></i></button><span style="padding:6px 12px;">Page '+currentPage+' of '+tp+'</span><button class="page-btn" onclick="goToPage('+(currentPage+1)+')"'+(currentPage>=tp?' disabled':'')+'><i class="bi bi-chevron-right"></i></button><button class="page-btn" onclick="goToPage('+tp+')"'+(currentPage>=tp?' disabled':'')+'><i class="bi bi-chevron-double-right"></i></button></div>';
}

function goToPage(p) { currentPage=p; renderTable(); }

function applyTableFilters() {
    const search = document.getElementById('tableSearch').value.toLowerCase();
    const domain = document.getElementById('filterDomain').value;
    const cat = document.getElementById('filterCategory').value;
    filteredData = flatSkillsData.filter(s => {
        if (domain && s.domain !== domain) return false;
        if (cat && s.category !== cat) return false;
        if (search && !s.name?.toLowerCase().includes(search) && !s.id?.toLowerCase().includes(search)) return false;
        return true;
    });
    currentPage = 1;
    renderTable();
}

// ══════════════════════════════════════════════════════════
//  EVENT LISTENERS & EXPORT
// ══════════════════════════════════════════════════════════

function initializeEventListeners() {
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const view = tab.dataset.view;
            document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            document.getElementById(view+'View').classList.add('active');
        });
    });
    let ft;
    ['tableSearch','filterDomain','filterCategory'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', () => { clearTimeout(ft); ft=setTimeout(applyTableFilters,300); });
        document.getElementById(id)?.addEventListener('change', applyTableFilters);
    });
}

function exportToExcel() {
    const ed = flatSkillsData.map(s => ({'Skill ID':s.id||'','Name':s.name||'','Domain':s.domain||'','Family':s.family||'','Category':s.category||'','Level':s.level||'','Confidence':s.confidence?(s.confidence*100).toFixed(1)+'%':'','Code':s.code||'','Alt Titles':(s.alternative_titles||[]).join('; '),'Codes':(s.all_related_codes||[]).join('; ')}));
    const ws = XLSX.utils.json_to_sheet(ed);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Skills');
    XLSX.writeFile(wb, 'vet_skills_taxonomy.xlsx');
}

function exportToCSV() {
    const h = ['ID','Name','Domain','Family','Category','Level','Confidence','Code'];
    const rows = flatSkillsData.map(s=>[s.id,s.name,s.domain,s.family,s.category||'',s.level||'',s.confidence?(s.confidence*100).toFixed(0)+'%':'',s.code||''].map(v=>'"'+String(v||'').replace(/"/g,'""')+'"').join(','));
    const csv = [h.join(','),...rows].join('\n');
    const blob = new Blob([csv],{type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href=url; a.download='vet_skills_taxonomy.csv'; a.click();
    URL.revokeObjectURL(url);
}
"""


HTML_TEMPLATE_EXTERNAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VET Skills Taxonomy Explorer | Jobs and Skills Australia</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>{CSS_CONTENT}</style>
</head>
<body>
    {BODY_CONTENT}
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script src="{DATA_FILE}"></script>
    <script>const LAZY_LOAD = true; {JAVASCRIPT_CONTENT}</script>
</body>
</html>
"""

HTML_TEMPLATE_EMBEDDED = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VET Skills Taxonomy Explorer | Jobs and Skills Australia</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>{CSS_CONTENT}</style>
</head>
<body>
    {BODY_CONTENT}
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>const EMBEDDED_DATA = {TAXONOMY_DATA}; const LAZY_LOAD = true; {JAVASCRIPT_CONTENT}</script>
</body>
</html>
"""


def count_skills(node):
    count = 0
    if 'skills' in node: count += len(node['skills'])
    if 'children' in node:
        for child in node['children']: count += count_skills(child)
    return count


def generate_html(taxonomy_json_path: str, output_html_path: str):
    print(f"Loading taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)

    total_skills = taxonomy_data.get('metadata', {}).get('statistics', {}).get('total_skills', 0)
    if total_skills == 0: total_skills = count_skills(taxonomy_data)
    n_archetypes = len(taxonomy_data.get('archetypes', []))
    print(f"Taxonomy loaded: {total_skills} skills, {n_archetypes} archetypes")

    if total_skills > EXTERNAL_DATA_THRESHOLD:
        data_file = output_html_path.replace('.html', '_data.js')
        data_file_name = Path(data_file).name
        with open(data_file, 'w') as f:
            f.write('const TAXONOMY_DATA = ')
            json.dump(taxonomy_data, f, separators=(',', ':'))
            f.write(';\n')
        print(f"Data saved to: {data_file}")
        html_content = HTML_TEMPLATE_EXTERNAL.format(CSS_CONTENT=CSS_CONTENT, BODY_CONTENT=BODY_CONTENT, DATA_FILE=data_file_name, JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT)
    else:
        html_content = HTML_TEMPLATE_EMBEDDED.format(CSS_CONTENT=CSS_CONTENT, BODY_CONTENT=BODY_CONTENT, TAXONOMY_DATA=json.dumps(taxonomy_data), JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT)

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n{'='*60}\n✓ HTML visualization generated: {output_html_path}\n{'='*60}")


def flatten_taxonomy_to_dataframe(taxonomy_data: dict) -> pd.DataFrame:
    flat = []
    def extract(node, path=None):
        if path is None: path = {'domain':'','family':'','group':''}
        if node.get('type')=='domain': path={**path,'domain':node.get('name','')}
        elif node.get('type')=='family': path={**path,'family':node.get('name','')}
        elif node.get('type')=='group': path={**path,'group':node.get('name','')}
        if 'skills' in node:
            for s in node['skills']:
                flat.append({'skill_id':s.get('id',''),'name':s.get('name',''),'description':s.get('description',''),'domain':path['domain'],'family':path['family'],'group':path['group'],'category':s.get('category',''),'level':s.get('level',''),'context':s.get('context',''),'confidence':s.get('confidence',''),'primary_code':s.get('code',''),'alternative_titles':'; '.join(s.get('alternative_titles',[])),'all_related_codes':'; '.join(s.get('all_related_codes',[])),'all_related_keywords':'; '.join(s.get('all_related_kw',[]))})
        if 'children' in node:
            for child in node['children']: extract(child, path.copy())
    extract(taxonomy_data)
    return pd.DataFrame(flat)


def export_taxonomy_to_excel(taxonomy_json_path: str, output_excel_path: str):
    with open(taxonomy_json_path, 'r') as f: taxonomy_data = json.load(f)
    df = flatten_taxonomy_to_dataframe(taxonomy_data)
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Skills Taxonomy', index=False)
    print(f"✓ Excel: {output_excel_path}")
    return df


if __name__ == '__main__':
    taxonomy_path = "./output/taxonomy.json"
    html_output_path = './output/taxonomy_visualization.html'
    if not Path(taxonomy_path).exists():
        print(f"Error: {taxonomy_path} not found"); sys.exit(1)
    generate_html(taxonomy_path, html_output_path)