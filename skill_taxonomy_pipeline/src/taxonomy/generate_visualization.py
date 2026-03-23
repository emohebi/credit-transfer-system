"""
Generate Interactive HTML Taxonomy Visualization (Optimized for Large Datasets)

This script creates a performant HTML visualization that can handle 50K+ skills
by using lazy loading, virtual rendering, and deferred detail display.

Theme: Jobs and Skills Australia (Australian Government)

Usage:
    python generate_visualization.py taxonomy.json output.html
    
Output:
    - taxonomy_visualization.html - The viewer (works offline, no server needed)
    - taxonomy_data.js - Data file (loaded via script tag, works with file://)
    
Just double-click the HTML file to open - no Python or server required!
"""

import json
import sys
from pathlib import Path
import pandas as pd

# Threshold for external data loading (skills count)
EXTERNAL_DATA_THRESHOLD = 5000


HTML_TEMPLATE_EXTERNAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VET Skills Taxonomy Explorer | Jobs and Skills Australia</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        {CSS_CONTENT}
    </style>
</head>
<body>
    {BODY_CONTENT}

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    
    <!-- Load taxonomy data from external JS file (works with file:// protocol) -->
    <script src="{DATA_FILE}"></script>

    <script>
        // Data is loaded from external file as TAXONOMY_DATA variable
        const LAZY_LOAD = true;
        
        {JAVASCRIPT_CONTENT}
    </script>
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
    
    <style>
        {CSS_CONTENT}
    </style>
</head>
<body>
    {BODY_CONTENT}

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

    <script>
        // Embedded data for small datasets
        const EMBEDDED_DATA = {TAXONOMY_DATA};
        const LAZY_LOAD = true;
        
        {JAVASCRIPT_CONTENT}
    </script>
</body>
</html>
"""


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

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--jsa-grey-100);
    color: var(--jsa-grey-800);
    line-height: 1.6;
}

/* Header */
.header {
    background: linear-gradient(135deg, var(--jsa-navy) 0%, var(--jsa-navy-dark) 100%);
    color: var(--jsa-white);
    position: relative;
}

.header-top {
    background: rgba(0, 0, 0, 0.15);
    padding: 8px 0;
    font-size: 0.85rem;
}

.header-top-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.gov-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--jsa-grey-200);
}

.header-main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 24px;
}

.header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
.header p { font-size: 1rem; opacity: 0.9; }

.header-logo {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}

.header-logo-icon {
    width: 48px;
    height: 48px;
    background: var(--jsa-teal);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-logo-icon i { font-size: 1.5rem; color: white; }

/* Main Container */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px 48px;
}

/* Stats */
.stats-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-top: -40px;
    padding: 0 24px;
    max-width: 1400px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    z-index: 10;
}

.stat-card {
    background: var(--jsa-white);
    padding: 16px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    text-align: center;
    border: 1px solid var(--jsa-grey-200);
}

.stat-card i { font-size: 1.5rem; color: var(--jsa-teal); margin-bottom: 4px; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: var(--jsa-navy); }
.stat-label { font-size: 0.75rem; color: var(--jsa-grey-500); text-transform: uppercase; letter-spacing: 0.5px; }

/* View Tabs */
.view-tabs-container {
    background: var(--jsa-white);
    margin-top: 24px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--jsa-grey-200);
    border-bottom: none;
}

.view-tabs { display: flex; padding: 0 16px; gap: 4px; }

.view-tab {
    padding: 14px 20px;
    cursor: pointer;
    border: none;
    background: transparent;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--jsa-grey-500);
    border-bottom: 3px solid transparent;
    display: flex;
    align-items: center;
    gap: 8px;
}

.view-tab:hover { color: var(--jsa-navy); background: var(--jsa-grey-100); }
.view-tab.active { color: var(--jsa-teal); border-bottom-color: var(--jsa-teal); }

/* Content Area */
.content-area {
    background: var(--jsa-white);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--jsa-grey-200);
    border-top: none;
    min-height: 500px;
    display: flex;
}

.view-section { display: none; flex: 1; }
.view-section.active { display: flex; }

/* Tree Panel */
.tree-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--jsa-grey-200);
    min-width: 0;
}

.tree-controls {
    padding: 16px;
    border-bottom: 1px solid var(--jsa-grey-200);
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    background: var(--jsa-grey-100);
}

.tree-search {
    flex: 1;
    min-width: 200px;
    padding: 10px 14px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.9rem;
}

.tree-search:focus { outline: none; border-color: var(--jsa-teal); }

.tree-container {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    background: var(--jsa-grey-100);
}

/* Tree Nodes - Simplified for performance */
.tree-node { margin: 2px 0; }

.node-row {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    background: var(--jsa-white);
    border-left: 3px solid transparent;
    margin-bottom: 2px;
}

.node-row:hover { background: var(--jsa-grey-100); border-left-color: var(--jsa-teal); }
.node-row.selected { background: rgba(0, 131, 143, 0.1); border-left-color: var(--jsa-teal); }
.node-row.expanded { background: rgba(0, 131, 143, 0.05); }

.node-toggle {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 6px;
    color: var(--jsa-grey-400);
    font-size: 0.7rem;
    transition: transform 0.15s;
}

.node-row.expanded .node-toggle { transform: rotate(90deg); }

.node-icon { margin-right: 8px; font-size: 1rem; }
.node-domain .node-icon { color: var(--jsa-navy); }
.node-family .node-icon { color: var(--jsa-teal); }
.node-cluster .node-icon { color: var(--jsa-orange); }
.node-group .node-icon { color: var(--jsa-purple); }
.node-skill .node-icon { color: var(--jsa-green); }

.node-label { flex: 1; font-weight: 500; font-size: 0.9rem; color: var(--jsa-grey-700); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.node-domain .node-label { font-weight: 600; color: var(--jsa-navy); }

.node-badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 12px;
    background: var(--jsa-grey-200);
    color: var(--jsa-grey-600);
    margin-left: 8px;
}

.node-children {
    margin-left: 20px;
    padding-left: 12px;
    border-left: 1px solid var(--jsa-grey-200);
    display: none;
}

.node-children.expanded { display: block; }

/* Detail Panel */
.detail-panel {
    width: 450px;
    min-width: 350px;
    max-width: 500px;
    background: var(--jsa-white);
    display: flex;
    flex-direction: column;
    border-left: 1px solid var(--jsa-grey-200);
}

.detail-header {
    padding: 16px;
    border-bottom: 1px solid var(--jsa-grey-200);
    background: var(--jsa-grey-100);
}

.detail-header h3 { font-size: 1rem; color: var(--jsa-grey-500); margin: 0; }

.detail-content {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.detail-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--jsa-grey-400);
    text-align: center;
    padding: 40px;
}

.detail-placeholder i { font-size: 3rem; margin-bottom: 16px; opacity: 0.5; }

/* Skill Detail Card */
.skill-card { animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.skill-card-header { margin-bottom: 16px; }

.skill-card-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--jsa-navy);
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.skill-card-name i { color: var(--jsa-green); }

.skill-card-id {
    display: inline-block;
    font-size: 0.75rem;
    color: var(--jsa-grey-500);
    background: var(--jsa-grey-100);
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    font-family: 'Monaco', 'Consolas', monospace;
}

.skill-card-description {
    font-size: 0.9rem;
    color: var(--jsa-grey-600);
    line-height: 1.6;
    margin: 16px 0;
    padding: 12px;
    background: var(--jsa-grey-100);
    border-radius: var(--radius-md);
}

.skill-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--jsa-grey-200);
}

.skill-section-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--jsa-grey-500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.meta-item {
    background: var(--jsa-grey-100);
    padding: 10px;
    border-radius: var(--radius-sm);
}

.meta-label { font-size: 0.7rem; color: var(--jsa-grey-500); text-transform: uppercase; margin-bottom: 2px; }
.meta-value { font-size: 0.85rem; color: var(--jsa-grey-700); font-weight: 500; }

.confidence-bar { width: 100%; height: 4px; background: var(--jsa-grey-200); border-radius: 2px; margin-top: 4px; }
.confidence-fill { height: 100%; border-radius: 2px; }
.confidence-high { background: var(--jsa-green); }
.confidence-medium { background: var(--jsa-gold); }
.confidence-low { background: var(--jsa-orange); }

/* Dimension Badges */
.dimension-list { display: flex; flex-wrap: wrap; gap: 6px; }

.dim-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

.dim-category { background: #fff8e1; color: #f57f17; }
.dim-complexity { background: #e3f2fd; color: #1565c0; }
.dim-transfer { background: #f3e5f5; color: #7b1fa2; }
.dim-digital { background: #e0f2f1; color: #00695c; }
.dim-future { background: #fff3e0; color: #e65100; }
.dim-nature { background: #fce4ec; color: #c2185b; }

/* Tags */
.tag-list { display: flex; flex-wrap: wrap; gap: 4px; }

.tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
}

.tag-alt { background: var(--jsa-grey-100); color: var(--jsa-grey-600); }
.tag-code { background: #e8eaf6; color: #3949ab; font-family: monospace; }
.tag-keyword { background: #e0f7fa; color: #00838f; }
.tag-more { background: var(--jsa-grey-200); color: var(--jsa-grey-500); font-style: italic; }

/* Related Skills */
.related-skill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px;
    background: rgba(106, 27, 154, 0.08);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    color: var(--jsa-purple);
    margin: 3px;
    cursor: pointer;
    text-decoration: none;
}

.related-skill:hover { background: rgba(106, 27, 154, 0.15); }
.similarity-score { font-size: 0.7rem; color: var(--jsa-grey-500); }

/* Table View */
.table-view-content { flex: 1; padding: 20px; flex-direction: column; display: flex; }

.table-controls {
    margin-bottom: 16px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}

.export-buttons { display: flex; gap: 10px; }

.btn-custom {
    padding: 8px 16px;
    border-radius: var(--radius-md);
    border: none;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
}

.btn-primary-custom { background: var(--jsa-teal); color: var(--jsa-white); }
.btn-primary-custom:hover { background: var(--jsa-navy); }
.btn-outline-custom { background: var(--jsa-white); color: var(--jsa-navy); border: 2px solid var(--jsa-grey-300); }
.btn-outline-custom:hover { border-color: var(--jsa-teal); color: var(--jsa-teal); }

.filter-group { display: flex; gap: 8px; flex-wrap: wrap; flex: 1; }

.filter-group select {
    padding: 8px 12px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    background: var(--jsa-white);
}

.filter-group input {
    padding: 8px 12px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    min-width: 200px;
}

/* Virtual Table */
.table-wrapper {
    flex: 1;
    overflow: auto;
    border: 1px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
}

.skills-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

.skills-table thead { position: sticky; top: 0; z-index: 10; }

.skills-table th {
    background: var(--jsa-navy);
    color: white;
    padding: 12px 10px;
    text-align: left;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.skills-table td {
    padding: 10px;
    border-bottom: 1px solid var(--jsa-grey-200);
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.skills-table tbody tr:hover { background: rgba(0, 131, 143, 0.03); }
.skills-table tbody tr { cursor: pointer; }

.table-pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    margin-top: 12px;
    border-top: 1px solid var(--jsa-grey-200);
}

.pagination-info { font-size: 0.85rem; color: var(--jsa-grey-600); }

.pagination-buttons { display: flex; gap: 4px; }

.page-btn {
    padding: 6px 12px;
    border: 1px solid var(--jsa-grey-300);
    background: white;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 0.85rem;
}

.page-btn:hover { background: var(--jsa-grey-100); }
.page-btn.active { background: var(--jsa-teal); color: white; border-color: var(--jsa-teal); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Loading */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid var(--jsa-grey-200);
    border-top-color: var(--jsa-teal);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text { margin-top: 16px; color: var(--jsa-grey-600); font-size: 0.9rem; }

/* Responsive */
@media (max-width: 1024px) {
    .detail-panel { display: none; }
    .tree-panel { border-right: none; }
}

@media (max-width: 768px) {
    .header h1 { font-size: 1.5rem; }
    .stats-dashboard { grid-template-columns: repeat(2, 1fr); margin-top: -24px; }
}
"""


BODY_CONTENT = """
<div id="loadingOverlay" class="loading-overlay">
    <div class="loading-spinner"></div>
    <div class="loading-text">Loading taxonomy data...</div>
    <div class="loading-hint" style="margin-top: 24px; font-size: 0.8rem; color: #9aa5b5; max-width: 400px; text-align: center;">
        If loading takes too long, make sure <code>taxonomy_visualization_data.js</code> is in the same folder as this HTML file.
    </div>
</div>

<div class="header">
    <div class="header-top">
        <div class="header-top-content">
            <div class="gov-badge">
                <i class="bi bi-building"></i>
                <span>Australian Government</span>
            </div>
        </div>
    </div>
    <div class="header-main">
        <div class="header-logo">
            <div class="header-logo-icon">
                <i class="bi bi-diagram-3"></i>
            </div>
            <div>
                <h1>VET Skills Taxonomy Explorer</h1>
                <p>Comprehensive taxonomy of vocational education and training skills</p>
            </div>
        </div>
    </div>
</div>

<div class="stats-dashboard">
    <div class="stat-card">
        <i class="bi bi-mortarboard-fill"></i>
        <div class="stat-value" id="totalSkills">-</div>
        <div class="stat-label">Total Skills</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-folder2-open"></i>
        <div class="stat-value" id="totalDomains">-</div>
        <div class="stat-label">Domains</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-collection"></i>
        <div class="stat-value" id="totalFamilies">-</div>
        <div class="stat-label">Families</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-upc-scan"></i>
        <div class="stat-value" id="totalCodes">-</div>
        <div class="stat-label">Unit Codes</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-tags"></i>
        <div class="stat-value" id="totalKeywords">-</div>
        <div class="stat-label">Keywords</div>
    </div>
</div>

<div class="main-container">
    <div class="view-tabs-container">
        <div class="view-tabs">
            <button class="view-tab active" data-view="tree">
                <i class="bi bi-diagram-3"></i> Hierarchy View
            </button>
            <button class="view-tab" data-view="table">
                <i class="bi bi-table"></i> Table View
            </button>
        </div>
    </div>

    <div class="content-area">
        <!-- Tree View -->
        <div class="view-section active" id="treeView">
            <div class="tree-panel">
                <div class="tree-controls">
                    <input type="text" class="tree-search" id="treeSearch" placeholder="Search skills, domains, codes...">
                    <button class="btn-custom btn-outline-custom" onclick="expandAllDomains()">
                        <i class="bi bi-arrows-expand"></i> Expand Domains
                    </button>
                    <button class="btn-custom btn-outline-custom" onclick="collapseAll()">
                        <i class="bi bi-arrows-collapse"></i> Collapse All
                    </button>
                </div>
                <div class="tree-container" id="treeContainer"></div>
            </div>
            <div class="detail-panel" id="detailPanel">
                <div class="detail-header">
                    <h3><i class="bi bi-info-circle"></i> Skill Details</h3>
                </div>
                <div class="detail-content" id="detailContent">
                    <div class="detail-placeholder">
                        <i class="bi bi-hand-index"></i>
                        <p>Select a skill from the tree to view details</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Table View -->
        <div class="view-section" id="tableView">
            <div class="table-view-content">
                <div class="table-controls">
                    <div class="export-buttons">
                        <button class="btn-custom btn-primary-custom" onclick="exportToExcel()">
                            <i class="bi bi-file-earmark-excel"></i> Export Excel
                        </button>
                        <button class="btn-custom btn-outline-custom" onclick="exportToCSV()">
                            <i class="bi bi-file-earmark-spreadsheet"></i> CSV
                        </button>
                    </div>
                    <div class="filter-group">
                        <input type="text" id="tableSearch" placeholder="Search skills...">
                        <select id="filterDomain"><option value="">All Domains</option></select>
                        <select id="filterCategory"><option value="">All Categories</option></select>
                    </div>
                </div>
                <div class="table-wrapper">
                    <table class="skills-table" id="skillsTable">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Skill Name</th>
                                <th>Domain</th>
                                <th>Family</th>
                                <th>Category</th>
                                <th>Level</th>
                                <th>Confidence</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
                <div class="table-pagination" id="tablePagination"></div>
            </div>
        </div>
    </div>
</div>
"""


JAVASCRIPT_CONTENT = """
let taxonomyData = null;
let flatSkillsData = [];
let skillsIndex = new Map();
let selectedSkillId = null;

// Table state
let currentPage = 1;
const pageSize = 50;
let filteredData = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Data loaded via script tag (TAXONOMY_DATA) or embedded (EMBEDDED_DATA)
        if (typeof TAXONOMY_DATA !== 'undefined') {
            taxonomyData = TAXONOMY_DATA;
        } else if (typeof EMBEDDED_DATA !== 'undefined') {
            taxonomyData = EMBEDDED_DATA;
        } else {
            throw new Error('No taxonomy data found. Make sure taxonomy_data.js is in the same folder.');
        }
        
        // Build flat index
        flatSkillsData = flattenTaxonomy(taxonomyData);
        flatSkillsData.forEach(skill => skillsIndex.set(skill.id, skill));
        filteredData = [...flatSkillsData];
        
        initializeStats();
        renderTree();
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
    const currentPath = { ...path };
    
    if (node.type === 'domain') currentPath.domain = node.name;
    else if (node.type === 'family') currentPath.family = node.name;
    else if (node.type === 'group') currentPath.group = node.name;
    
    if (node.skills) {
        node.skills.forEach(skill => {
            result.push({ ...skill, ...currentPath });
        });
    }
    
    if (node.children) {
        node.children.forEach(child => flattenTaxonomy(child, currentPath, result));
    }
    
    return result;
}

function initializeStats() {
    const stats = taxonomyData.metadata?.statistics || {};
    document.getElementById('totalSkills').textContent = (stats.total_skills || flatSkillsData.length).toLocaleString();
    document.getElementById('totalDomains').textContent = stats.total_domains || taxonomyData.children?.length || 0;
    document.getElementById('totalFamilies').textContent = stats.total_families || '-';
    document.getElementById('totalCodes').textContent = (stats.total_related_codes || countUniqueCodes()).toLocaleString();
    document.getElementById('totalKeywords').textContent = (stats.total_related_keywords || '-').toLocaleString();
}

function countUniqueCodes() {
    const codes = new Set();
    flatSkillsData.forEach(s => (s.all_related_codes || []).forEach(c => codes.add(c)));
    return codes.size;
}

// ============ TREE RENDERING (Lazy) ============

function renderTree() {
    const container = document.getElementById('treeContainer');
    container.innerHTML = '';
    
    if (taxonomyData.children) {
        taxonomyData.children.forEach(domain => {
            container.appendChild(createNodeElement(domain, 0));
        });
    }
}

function createNodeElement(node, depth) {
    const div = document.createElement('div');
    div.className = 'tree-node';
    div.dataset.nodeId = node.id || node.name;
    div.dataset.loaded = 'false';
    
    const hasChildren = (node.children && node.children.length > 0) || (node.skills && node.skills.length > 0);
    
    const row = document.createElement('div');
    row.className = `node-row node-${node.type}`;
    
    // Toggle icon
    const toggle = document.createElement('span');
    toggle.className = 'node-toggle';
    toggle.innerHTML = hasChildren ? '<i class="bi bi-chevron-right"></i>' : '';
    row.appendChild(toggle);
    
    // Type icon
    const icon = document.createElement('i');
    icon.className = 'bi node-icon ' + getIconClass(node.type);
    row.appendChild(icon);
    
    // Label
    const label = document.createElement('span');
    label.className = 'node-label';
    label.textContent = node.name;
    label.title = node.name;
    row.appendChild(label);
    
    // Badge
    const size = node.statistics?.size || node.size || (node.skills?.length);
    if (size) {
        const badge = document.createElement('span');
        badge.className = 'node-badge';
        badge.textContent = size;
        row.appendChild(badge);
    }
    
    div.appendChild(row);
    
    // Children container (lazy loaded)
    if (hasChildren) {
        const childrenDiv = document.createElement('div');
        childrenDiv.className = 'node-children';
        div.appendChild(childrenDiv);
        
        // Store node data for lazy loading
        div._nodeData = node;
    }
    
    // Click handler
    row.addEventListener('click', (e) => {
        e.stopPropagation();
        
        if (node.type === 'skill' || (node.skills && node.skills.length === 1 && !node.children)) {
            const skill = node.type === 'skill' ? node : node.skills[0];
            showSkillDetail(skill);
        } else if (hasChildren) {
            toggleNodeExpansion(div);
        }
    });
    
    return div;
}

function toggleNodeExpansion(nodeDiv) {
    const row = nodeDiv.querySelector('.node-row');
    const childrenDiv = nodeDiv.querySelector('.node-children');
    
    if (!childrenDiv) return;
    
    const isExpanded = childrenDiv.classList.contains('expanded');
    
    if (isExpanded) {
        childrenDiv.classList.remove('expanded');
        row.classList.remove('expanded');
    } else {
        // Lazy load children if not loaded
        if (nodeDiv.dataset.loaded === 'false' && nodeDiv._nodeData) {
            loadNodeChildren(nodeDiv, childrenDiv);
            nodeDiv.dataset.loaded = 'true';
        }
        childrenDiv.classList.add('expanded');
        row.classList.add('expanded');
    }
}

function loadNodeChildren(nodeDiv, childrenDiv) {
    const node = nodeDiv._nodeData;
    
    // Render children nodes
    if (node.children) {
        node.children.forEach(child => {
            childrenDiv.appendChild(createNodeElement(child, 1));
        });
    }
    
    // Render skills as simple rows
    if (node.skills) {
        node.skills.forEach(skill => {
            const skillRow = document.createElement('div');
            skillRow.className = 'node-row node-skill';
            skillRow.innerHTML = `
                <span class="node-toggle"></span>
                <i class="bi bi-mortarboard node-icon"></i>
                <span class="node-label" title="${skill.name}">${skill.name}</span>
                <span class="node-badge" style="font-family: monospace; font-size: 0.65rem;">${skill.id || ''}</span>
            `;
            skillRow.addEventListener('click', (e) => {
                e.stopPropagation();
                showSkillDetail(skill);
                
                // Highlight selected
                document.querySelectorAll('.node-row.selected').forEach(r => r.classList.remove('selected'));
                skillRow.classList.add('selected');
            });
            childrenDiv.appendChild(skillRow);
        });
    }
}

function getIconClass(type) {
    const icons = {
        'domain': 'bi-folder2-open',
        'family': 'bi-collection',
        'cluster': 'bi-grid-3x3-gap',
        'group': 'bi-layers',
        'skill': 'bi-mortarboard'
    };
    return icons[type] || 'bi-circle-fill';
}

function expandAllDomains() {
    document.querySelectorAll('.tree-node').forEach(node => {
        if (node._nodeData?.type === 'domain') {
            const childrenDiv = node.querySelector('.node-children');
            if (childrenDiv) {
                if (node.dataset.loaded === 'false' && node._nodeData) {
                    loadNodeChildren(node, childrenDiv);
                    node.dataset.loaded = 'true';
                }
                childrenDiv.classList.add('expanded');
                node.querySelector('.node-row')?.classList.add('expanded');
            }
        }
    });
}

function collapseAll() {
    document.querySelectorAll('.node-children').forEach(c => c.classList.remove('expanded'));
    document.querySelectorAll('.node-row').forEach(r => r.classList.remove('expanded'));
}

// ============ SKILL DETAIL PANEL ============

function showSkillDetail(skill) {
    const content = document.getElementById('detailContent');
    selectedSkillId = skill.id;
    
    const dims = skill.dimensions || {};
    const confPct = ((skill.confidence || 0) * 100).toFixed(0);
    const confClass = confPct >= 80 ? 'high' : (confPct >= 50 ? 'medium' : 'low');
    
    let html = `
        <div class="skill-card">
            <div class="skill-card-header">
                <div class="skill-card-name">
                    <i class="bi bi-mortarboard-fill"></i>
                    ${skill.name}
                </div>
                <span class="skill-card-id">${skill.id || 'N/A'}</span>
            </div>
            
            ${skill.description ? `<div class="skill-card-description">${skill.description}</div>` : ''}
            
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-bar-chart"></i> Metrics</div>
                <div class="meta-grid">
                    <div class="meta-item">
                        <div class="meta-label">Confidence</div>
                        <div class="meta-value">${confPct}%</div>
                        <div class="confidence-bar"><div class="confidence-fill confidence-${confClass}" style="width: ${confPct}%"></div></div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Level</div>
                        <div class="meta-value">${skill.level || 'N/A'}</div>
                    </div>
                    ${skill.code ? `<div class="meta-item"><div class="meta-label">Primary Code</div><div class="meta-value" style="font-family: monospace">${skill.code}</div></div>` : ''}
                    ${skill.context ? `<div class="meta-item"><div class="meta-label">Context</div><div class="meta-value">${formatLabel(skill.context)}</div></div>` : ''}
                </div>
            </div>
            
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-tags"></i> Dimensions</div>
                <div class="dimension-list">
                    ${skill.category ? `<span class="dim-badge dim-category"><i class="bi bi-bookmark"></i> ${skill.category}</span>` : ''}
                    ${dims.complexity_level ? `<span class="dim-badge dim-complexity">Level ${dims.complexity_level}</span>` : ''}
                    ${dims.transferability ? `<span class="dim-badge dim-transfer">${formatLabel(dims.transferability)}</span>` : ''}
                    ${dims.digital_intensity !== undefined ? `<span class="dim-badge dim-digital">Digital ${dims.digital_intensity}</span>` : ''}
                    ${dims.future_readiness ? `<span class="dim-badge dim-future">${formatLabel(dims.future_readiness)}</span>` : ''}
                    ${dims.skill_nature ? `<span class="dim-badge dim-nature">${formatLabel(dims.skill_nature)}</span>` : ''}
                </div>
            </div>`;
    
    // Alternative titles
    const altTitles = skill.alternative_titles || [];
    if (altTitles.length > 0) {
        html += `
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-card-heading"></i> Alternative Titles (${altTitles.length})</div>
                <div class="tag-list">
                    ${altTitles.slice(0, 10).map(t => `<span class="tag tag-alt">${t}</span>`).join('')}
                    ${altTitles.length > 10 ? `<span class="tag tag-more">+${altTitles.length - 10} more</span>` : ''}
                </div>
            </div>`;
    }
    
    // Related codes
    const codes = skill.all_related_codes || [];
    if (codes.length > 0) {
        html += `
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-upc-scan"></i> Related Codes (${codes.length})</div>
                <div class="tag-list">
                    ${codes.slice(0, 12).map(c => `<span class="tag tag-code">${c}</span>`).join('')}
                    ${codes.length > 12 ? `<span class="tag tag-more">+${codes.length - 12} more</span>` : ''}
                </div>
            </div>`;
    }
    
    // Related keywords
    const kws = skill.all_related_kw || [];
    if (kws.length > 0) {
        html += `
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-key"></i> Related Keywords (${kws.length})</div>
                <div class="tag-list">
                    ${kws.slice(0, 15).map(k => `<span class="tag tag-keyword">${k}</span>`).join('')}
                    ${kws.length > 15 ? `<span class="tag tag-more">+${kws.length - 15} more</span>` : ''}
                </div>
            </div>`;
    }
    
    // Related skills
    const related = skill.relationships?.related || [];
    if (related.length > 0) {
        html += `
            <div class="skill-section">
                <div class="skill-section-title"><i class="bi bi-link-45deg"></i> Related Skills</div>
                <div>
                    ${related.slice(0, 8).map(r => `
                        <span class="related-skill" onclick="navigateToSkill('${r.skill_id}')">
                            ${r.skill_name}
                            <span class="similarity-score">${r.similarity ? (r.similarity * 100).toFixed(0) + '%' : ''}</span>
                        </span>
                    `).join('')}
                </div>
            </div>`;
    }
    
    html += '</div>';
    content.innerHTML = html;
}

function navigateToSkill(skillId) {
    const skill = skillsIndex.get(skillId);
    if (skill) showSkillDetail(skill);
}

function formatLabel(str) {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}

// ============ SEARCH ============

let searchTimeout;
document.getElementById('treeSearch')?.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => performTreeSearch(e.target.value), 300);
});

function performTreeSearch(query) {
    if (!query || query.length < 2) {
        // Reset view
        document.querySelectorAll('.tree-node').forEach(n => n.style.display = '');
        return;
    }
    
    const searchLower = query.toLowerCase();
    const matches = flatSkillsData.filter(s => 
        s.name?.toLowerCase().includes(searchLower) ||
        s.id?.toLowerCase().includes(searchLower) ||
        s.domain?.toLowerCase().includes(searchLower) ||
        (s.all_related_codes || []).some(c => c.toLowerCase().includes(searchLower))
    ).slice(0, 100);
    
    // Show results in tree area temporarily
    const container = document.getElementById('treeContainer');
    container.innerHTML = `<div style="padding: 10px; color: var(--jsa-grey-500);">Found ${matches.length} results${matches.length >= 100 ? ' (showing first 100)' : ''}</div>`;
    
    matches.forEach(skill => {
        const row = document.createElement('div');
        row.className = 'node-row node-skill';
        row.innerHTML = `
            <span class="node-toggle"></span>
            <i class="bi bi-mortarboard node-icon"></i>
            <span class="node-label">${skill.name}</span>
            <span class="node-badge" style="font-size: 0.65rem;">${skill.domain || ''}</span>
        `;
        row.addEventListener('click', () => showSkillDetail(skill));
        container.appendChild(row);
    });
    
    // Add reset button
    const resetBtn = document.createElement('button');
    resetBtn.className = 'btn-custom btn-outline-custom';
    resetBtn.style.margin = '10px';
    resetBtn.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i> Reset Tree';
    resetBtn.onclick = () => {
        document.getElementById('treeSearch').value = '';
        renderTree();
    };
    container.prepend(resetBtn);
}

// ============ TABLE VIEW ============

function initializeTable() {
    // Populate filters
    const domains = [...new Set(flatSkillsData.map(s => s.domain).filter(Boolean))].sort();
    const domainSelect = document.getElementById('filterDomain');
    domains.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        domainSelect.appendChild(opt);
    });
    
    const categories = [...new Set(flatSkillsData.map(s => s.category).filter(Boolean))].sort();
    const catSelect = document.getElementById('filterCategory');
    categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = formatLabel(c);
        catSelect.appendChild(opt);
    });
    
    renderTable();
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = filteredData.slice(start, end);
    
    tbody.innerHTML = pageData.map(s => `
        <tr onclick="showSkillDetail(skillsIndex.get('${s.id}'))">
            <td style="font-family: monospace; font-size: 0.8rem;">${s.id || '-'}</td>
            <td>${s.name}</td>
            <td>${s.domain || '-'}</td>
            <td>${s.family || '-'}</td>
            <td>${formatLabel(s.category) || '-'}</td>
            <td>${s.level || '-'}</td>
            <td>${s.confidence ? (s.confidence * 100).toFixed(0) + '%' : '-'}</td>
        </tr>
    `).join('');
    
    renderPagination();
}

function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / pageSize);
    const pag = document.getElementById('tablePagination');
    
    pag.innerHTML = `
        <div class="pagination-info">
            Showing ${((currentPage - 1) * pageSize) + 1}-${Math.min(currentPage * pageSize, filteredData.length)} of ${filteredData.length.toLocaleString()} skills
        </div>
        <div class="pagination-buttons">
            <button class="page-btn" onclick="goToPage(1)" ${currentPage === 1 ? 'disabled' : ''}><i class="bi bi-chevron-double-left"></i></button>
            <button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}><i class="bi bi-chevron-left"></i></button>
            <span style="padding: 6px 12px;">Page ${currentPage} of ${totalPages}</span>
            <button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}><i class="bi bi-chevron-right"></i></button>
            <button class="page-btn" onclick="goToPage(${totalPages})" ${currentPage >= totalPages ? 'disabled' : ''}><i class="bi bi-chevron-double-right"></i></button>
        </div>
    `;
}

function goToPage(page) {
    currentPage = page;
    renderTable();
}

function applyTableFilters() {
    const search = document.getElementById('tableSearch').value.toLowerCase();
    const domain = document.getElementById('filterDomain').value;
    const category = document.getElementById('filterCategory').value;
    
    filteredData = flatSkillsData.filter(s => {
        if (domain && s.domain !== domain) return false;
        if (category && s.category !== category) return false;
        if (search && !s.name?.toLowerCase().includes(search) && !s.id?.toLowerCase().includes(search)) return false;
        return true;
    });
    
    currentPage = 1;
    renderTable();
}

// ============ EVENT LISTENERS ============

function initializeEventListeners() {
    // Tab switching
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const view = tab.dataset.view;
            document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            document.getElementById(`${view}View`).classList.add('active');
        });
    });
    
    // Table filters
    let filterTimeout;
    ['tableSearch', 'filterDomain', 'filterCategory'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', () => {
            clearTimeout(filterTimeout);
            filterTimeout = setTimeout(applyTableFilters, 300);
        });
        document.getElementById(id)?.addEventListener('change', applyTableFilters);
    });
}

// ============ EXPORT ============

function exportToExcel() {
    const exportData = flatSkillsData.map(s => ({
        'Skill ID': s.id || '',
        'Skill Name': s.name || '',
        'Description': s.description || '',
        'Domain': s.domain || '',
        'Family': s.family || '',
        'Group': s.group || '',
        'Category': s.category || '',
        'Level': s.level || '',
        'Context': s.context || '',
        'Confidence': s.confidence ? (s.confidence * 100).toFixed(1) + '%' : '',
        'Complexity Level': s.dimensions?.complexity_level || '',
        'Transferability': s.dimensions?.transferability || '',
        'Digital Intensity': s.dimensions?.digital_intensity || '',
        'Future Readiness': s.dimensions?.future_readiness || '',
        'Skill Nature': s.dimensions?.skill_nature || '',
        'Primary Code': s.code || '',
        'Alternative Titles': (s.alternative_titles || []).join('; '),
        'All Related Codes': (s.all_related_codes || []).join('; '),
        'All Related Keywords': (s.all_related_kw || []).join('; ')
    }));
    
    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Skills Taxonomy');
    XLSX.writeFile(wb, 'vet_skills_taxonomy.xlsx');
}

function exportToCSV() {
    const headers = ['Skill ID', 'Name', 'Domain', 'Family', 'Category', 'Level', 'Confidence', 'Primary Code'];
    const rows = flatSkillsData.map(s => [
        s.id, s.name, s.domain, s.family, s.category || '',
        s.level || '', s.confidence ? (s.confidence * 100).toFixed(0) + '%' : '', s.code || ''
    ].map(v => `"${String(v || '').replace(/"/g, '""')}"`).join(','));
    
    const csv = [headers.join(','), ...rows].join('\\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vet_skills_taxonomy.csv';
    a.click();
    URL.revokeObjectURL(url);
}
"""


def count_skills(node):
    """Count total skills in taxonomy"""
    count = 0
    if 'skills' in node:
        count += len(node['skills'])
    if 'children' in node:
        for child in node['children']:
            count += count_skills(child)
    return count


def generate_html(taxonomy_json_path: str, output_html_path: str):
    """Generate optimized HTML visualization"""
    
    print(f"Loading taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)
    
    total_skills = taxonomy_data.get('metadata', {}).get('statistics', {}).get('total_skills', 0)
    if total_skills == 0:
        total_skills = count_skills(taxonomy_data)
    
    print(f"Taxonomy loaded: {total_skills} skills")
    
    # Decide whether to embed or use external file
    if total_skills > EXTERNAL_DATA_THRESHOLD:
        print(f"Large dataset detected ({total_skills} skills). Using external data file.")
        
        # Save data to JavaScript file (works with file:// protocol unlike JSON fetch)
        data_file = output_html_path.replace('.html', '_data.js')
        data_file_name = Path(data_file).name
        
        # Write as JavaScript variable assignment
        with open(data_file, 'w') as f:
            f.write('// VET Skills Taxonomy Data\n')
            f.write('// This file is loaded by taxonomy_visualization.html\n')
            f.write('// Do not edit manually\n\n')
            f.write('const TAXONOMY_DATA = ')
            json.dump(taxonomy_data, f, separators=(',', ':'))  # Minified JSON
            f.write(';\n')
        
        print(f"Data saved to: {data_file}")
        print(f"  (Minified JSON as JavaScript variable)")
        
        # Generate HTML with script tag reference
        html_content = HTML_TEMPLATE_EXTERNAL.format(
            CSS_CONTENT=CSS_CONTENT,
            BODY_CONTENT=BODY_CONTENT,
            DATA_FILE=data_file_name,
            JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT
        )
    else:
        print(f"Small dataset ({total_skills} skills). Embedding data in HTML.")
        
        html_content = HTML_TEMPLATE_EMBEDDED.format(
            CSS_CONTENT=CSS_CONTENT,
            BODY_CONTENT=BODY_CONTENT,
            TAXONOMY_DATA=json.dumps(taxonomy_data),
            JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT
        )
    
    print(f"Writing HTML to: {output_html_path}")
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("✓ HTML visualization generated successfully!")
    print("=" * 60)
    print("\nTo view the taxonomy:")
    print(f"  1. Keep both files in the same folder:")
    if total_skills > EXTERNAL_DATA_THRESHOLD:
        print(f"     - {Path(output_html_path).name}")
        print(f"     - {data_file_name}")
    else:
        print(f"     - {Path(output_html_path).name}")
    print(f"  2. Double-click the HTML file to open in your browser")
    print("\nNo server or Python required - works offline!")
    print("=" * 60)


def flatten_taxonomy_to_dataframe(taxonomy_data: dict) -> pd.DataFrame:
    """Flatten taxonomy to pandas DataFrame for Excel export"""
    
    flat_skills = []
    
    def extract_skills(node, path=None):
        if path is None:
            path = {'domain': '', 'family': '', 'group': ''}
        
        if node.get('type') == 'domain':
            path = {**path, 'domain': node.get('name', '')}
        elif node.get('type') == 'family':
            path = {**path, 'family': node.get('name', '')}
        elif node.get('type') == 'group':
            path = {**path, 'group': node.get('name', '')}
        
        if 'skills' in node and node['skills']:
            for skill in node['skills']:
                dims = skill.get('dimensions', {})
                flat_skills.append({
                    'skill_id': skill.get('id', ''),
                    'name': skill.get('name', ''),
                    'description': skill.get('description', ''),
                    'domain': path['domain'],
                    'family': path['family'],
                    'group': path['group'],
                    'category': skill.get('category', ''),
                    'level': skill.get('level', ''),
                    'context': skill.get('context', ''),
                    'confidence': skill.get('confidence', ''),
                    # 'complexity_level': dims.get('complexity_level', ''),
                    # 'transferability': dims.get('transferability', ''),
                    # 'digital_intensity': dims.get('digital_intensity', ''),
                    # 'future_readiness': dims.get('future_readiness', ''),
                    # 'skill_nature': dims.get('skill_nature', ''),
                    'primary_code': skill.get('code', ''),
                    'alternative_titles': '; '.join(skill.get('alternative_titles', [])),
                    'all_related_codes': '; '.join(skill.get('all_related_codes', [])),
                    'all_related_keywords': '; '.join(skill.get('all_related_kw', [])),
                })
        
        if 'children' in node:
            for child in node['children']:
                extract_skills(child, path.copy())
    
    extract_skills(taxonomy_data)
    return pd.DataFrame(flat_skills)


def export_taxonomy_to_excel(taxonomy_json_path: str, output_excel_path: str):
    """Export flattened taxonomy to Excel file"""
    
    print(f"Loading taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)
    
    print("Flattening taxonomy...")
    df = flatten_taxonomy_to_dataframe(taxonomy_data)
    
    print(f"Writing Excel file with {len(df)} skills...")
    
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Skills Taxonomy', index=False)
        
        # Metadata sheet
        stats = taxonomy_data.get('metadata', {}).get('statistics', {})
        meta_df = pd.DataFrame([
            ['VET Skills Taxonomy Export', ''],
            ['', ''],
            ['Export Date', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Skills', stats.get('total_skills', len(df))],
            ['Total Domains', stats.get('total_domains', '')],
            ['Total Families', stats.get('total_families', '')],
            ['Total Related Codes', stats.get('total_related_codes', '')],
            ['Total Related Keywords', stats.get('total_related_keywords', '')],
        ], columns=['Property', 'Value'])
        meta_df.to_excel(writer, sheet_name='Metadata', index=False)
    
    print(f"✓ Excel file saved to: {output_excel_path}")
    return df


if __name__ == '__main__':
    taxonomy_path = "./output/taxonomy.json"
    html_output_path = './output/taxonomy_visualization.html'
    excel_output_path = './output/taxonomy_flat.xlsx'
    
    if not Path(taxonomy_path).exists():
        print(f"Error: Taxonomy file not found: {taxonomy_path}")
        sys.exit(1)
    
    generate_html(taxonomy_path, html_output_path)
    
    try:
        export_taxonomy_to_excel(taxonomy_path, excel_output_path)
    except Exception as e:
        print(f"Warning: Could not export to Excel: {e}")