"""
Generate Interactive HTML Taxonomy Visualization

This script takes your taxonomy.json file and creates a beautiful interactive
HTML visualization with the data embedded.

Theme: Jobs and Skills Australia (Australian Government)

Usage:
    python generate_visualization.py taxonomy.json output.html
"""

import json
import sys
from pathlib import Path
import pandas as pd


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VET Skills Taxonomy Explorer | Jobs and Skills Australia</title>
    
    <!-- External Libraries -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        {CSS_CONTENT}
    </style>
</head>
<body>
    {BODY_CONTENT}

    <!-- External Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

    <script>
        // Embedded taxonomy data
        const EMBEDDED_TAXONOMY_DATA = {TAXONOMY_DATA};
        
        {JAVASCRIPT_CONTENT}
    </script>
</body>
</html>
"""


CSS_CONTENT = """
/* ========================================
   Jobs and Skills Australia Theme
   Australian Government Design System
   ======================================== */

:root {
    /* Primary Colors - Australian Government */
    --jsa-navy: #1e3a5f;
    --jsa-navy-dark: #0d2137;
    --jsa-navy-light: #2c5282;
    --jsa-teal: #00838f;
    --jsa-teal-light: #4fb3bf;
    --jsa-green: #2e7d32;
    --jsa-green-light: #4caf50;
    
    /* Secondary Colors */
    --jsa-gold: #c9a227;
    --jsa-orange: #e65100;
    --jsa-purple: #6a1b9a;
    --jsa-red: #c62828;
    
    /* Neutrals */
    --jsa-white: #ffffff;
    --jsa-grey-100: #f5f7fa;
    --jsa-grey-200: #e8ecf1;
    --jsa-grey-300: #d1d9e6;
    --jsa-grey-400: #9aa5b5;
    --jsa-grey-500: #6b7785;
    --jsa-grey-600: #4a5568;
    --jsa-grey-700: #2d3748;
    --jsa-grey-800: #1a202c;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(30, 58, 95, 0.05);
    --shadow-md: 0 4px 6px rgba(30, 58, 95, 0.07), 0 2px 4px rgba(30, 58, 95, 0.06);
    --shadow-lg: 0 10px 15px rgba(30, 58, 95, 0.1), 0 4px 6px rgba(30, 58, 95, 0.05);
    --shadow-xl: 0 20px 25px rgba(30, 58, 95, 0.1), 0 10px 10px rgba(30, 58, 95, 0.04);
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}

* { 
    box-sizing: border-box; 
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--jsa-grey-100);
    color: var(--jsa-grey-800);
    line-height: 1.6;
    min-height: 100vh;
}

/* ========================================
   Header - Government Style
   ======================================== */

.header {
    background: linear-gradient(135deg, var(--jsa-navy) 0%, var(--jsa-navy-dark) 100%);
    color: var(--jsa-white);
    padding: 0;
    position: relative;
    overflow: hidden;
}

.header::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 40%;
    height: 100%;
    background: linear-gradient(135deg, transparent 0%, rgba(0, 131, 143, 0.1) 100%);
    pointer-events: none;
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

.gov-badge i {
    font-size: 1rem;
}

.header-main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 24px;
    position: relative;
    z-index: 1;
}

.header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.header p {
    font-size: 1rem;
    opacity: 0.9;
    max-width: 600px;
}

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

.header-logo-icon i {
    font-size: 1.5rem;
    color: white;
}

/* ========================================
   Main Container
   ======================================== */

.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px 48px;
}

/* ========================================
   Stats Dashboard
   ======================================== */

.stats-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
    padding: 20px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid var(--jsa-grey-200);
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
}

.stat-card i {
    font-size: 1.75rem;
    color: var(--jsa-teal);
    margin-bottom: 8px;
}

.stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--jsa-navy);
    margin: 4px 0;
}

.stat-label {
    font-size: 0.8rem;
    color: var(--jsa-grey-500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}

/* ========================================
   View Tabs
   ======================================== */

.view-tabs-container {
    background: var(--jsa-white);
    margin-top: 24px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--jsa-grey-200);
    border-bottom: none;
}

.view-tabs {
    display: flex;
    padding: 0 16px;
    gap: 4px;
}

.view-tab {
    padding: 16px 24px;
    cursor: pointer;
    border: none;
    background: transparent;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--jsa-grey-500);
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.view-tab:hover { 
    color: var(--jsa-navy);
    background: var(--jsa-grey-100);
}

.view-tab.active {
    color: var(--jsa-teal);
    border-bottom-color: var(--jsa-teal);
    background: transparent;
}

.view-tab i {
    font-size: 1.1rem;
}

/* ========================================
   Content Area
   ======================================== */

.content-area {
    background: var(--jsa-white);
    padding: 24px;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--jsa-grey-200);
    border-top: none;
    min-height: 600px;
}

.view-section {
    display: none;
}

.view-section.active {
    display: block;
}

/* ========================================
   Tree View
   ======================================== */

.tree-controls {
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}

.tree-search {
    flex: 1;
    min-width: 300px;
    padding: 12px 16px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.tree-search:focus {
    outline: none;
    border-color: var(--jsa-teal);
    box-shadow: 0 0 0 3px rgba(0, 131, 143, 0.1);
}

.tree-search::placeholder {
    color: var(--jsa-grey-400);
}

.tree-container {
    background: var(--jsa-grey-100);
    border: 1px solid var(--jsa-grey-200);
    border-radius: var(--radius-lg);
    padding: 20px;
}

.tree-node {
    margin: 4px 0;
}

.node-content {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.15s ease;
    border-left: 3px solid transparent;
    background: var(--jsa-white);
    margin-bottom: 4px;
}

.node-content:hover {
    background: var(--jsa-grey-100);
    border-left-color: var(--jsa-teal);
}

.node-content.expanded {
    background: rgba(0, 131, 143, 0.05);
    border-left-color: var(--jsa-teal);
}

.node-toggle {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    color: var(--jsa-grey-400);
    font-size: 0.75rem;
    transition: transform 0.2s ease;
}

.node-content.expanded .node-toggle {
    transform: rotate(90deg);
}

.node-icon {
    margin-right: 10px;
    font-size: 1.1rem;
}

.node-label {
    flex: 1;
    font-weight: 500;
    color: var(--jsa-grey-700);
}

.node-badge {
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 20px;
    background: var(--jsa-grey-200);
    color: var(--jsa-grey-600);
    margin-left: 8px;
    font-weight: 500;
}

.node-children {
    margin-left: 24px;
    border-left: 2px solid var(--jsa-grey-200);
    padding-left: 12px;
    display: none;
}

.node-children.expanded {
    display: block;
}

/* Node type colors */
.node-domain .node-icon { color: var(--jsa-navy); }
.node-domain .node-label { color: var(--jsa-navy); font-weight: 600; }
.node-family .node-icon { color: var(--jsa-teal); }
.node-cluster .node-icon { color: var(--jsa-orange); }
.node-group .node-icon { color: var(--jsa-purple); }
.node-skill .node-icon { color: var(--jsa-green); }

/* ========================================
   Skill Detail Card
   ======================================== */

.skill-detail {
    background: var(--jsa-white);
    border-radius: var(--radius-md);
    padding: 16px;
    margin: 8px 0;
    border: 1px solid var(--jsa-grey-200);
    transition: box-shadow 0.2s ease;
}

.skill-detail:hover {
    box-shadow: var(--shadow-md);
}

.skill-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
}

.skill-name {
    font-weight: 600;
    color: var(--jsa-navy);
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.skill-name i {
    color: var(--jsa-green);
}

.skill-id {
    font-size: 0.75rem;
    color: var(--jsa-grey-500);
    background: var(--jsa-grey-100);
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    font-family: 'Monaco', 'Consolas', monospace;
}

.skill-description {
    font-size: 0.9rem;
    color: var(--jsa-grey-600);
    margin-bottom: 12px;
    line-height: 1.5;
}

.skill-meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
}

.skill-meta-item {
    background: var(--jsa-grey-100);
    padding: 10px 12px;
    border-radius: var(--radius-sm);
}

.skill-meta-label {
    font-size: 0.7rem;
    color: var(--jsa-grey-500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    font-weight: 600;
}

.skill-meta-value {
    font-size: 0.85rem;
    color: var(--jsa-grey-700);
    font-weight: 500;
}

.skill-dimensions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
}

.dimension-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* Dimension badge colors */
.dim-complexity { background: #e3f2fd; color: #1565c0; }
.dim-transferability { background: #f3e5f5; color: #7b1fa2; }
.dim-digital { background: #e0f2f1; color: #00695c; }
.dim-future { background: #fff3e0; color: #e65100; }
.dim-nature { background: #fce4ec; color: #c2185b; }
.dim-context { background: #e8f5e9; color: #2e7d32; }
.dim-category { background: #fff8e1; color: #f57f17; }

/* Alternative titles */
.alt-titles-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--jsa-grey-200);
}

.alt-titles-label {
    font-size: 0.75rem;
    color: var(--jsa-grey-500);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.alt-title-tag {
    display: inline-block;
    background: var(--jsa-grey-100);
    color: var(--jsa-grey-600);
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    font-size: 0.8rem;
    margin: 2px;
}

/* Related codes and keywords */
.related-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--jsa-grey-200);
}

.related-label {
    font-size: 0.75rem;
    color: var(--jsa-grey-500);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.code-tag {
    display: inline-block;
    background: #e8eaf6;
    color: #3949ab;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-family: 'Monaco', 'Consolas', monospace;
    margin: 2px;
}

.keyword-tag {
    display: inline-block;
    background: #e0f7fa;
    color: #00838f;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    margin: 2px;
}

/* Related skills */
.related-skills-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--jsa-grey-200);
}

.relationship-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    background: rgba(106, 27, 154, 0.08);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    color: var(--jsa-purple);
    text-decoration: none;
    margin: 3px;
    transition: all 0.15s ease;
}

.relationship-link:hover {
    background: rgba(106, 27, 154, 0.15);
    color: #4a148c;
}

.similarity-score {
    font-size: 0.7rem;
    color: var(--jsa-grey-500);
    margin-left: 4px;
}

/* ========================================
   Table View
   ======================================== */

.table-controls {
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}

.filter-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.filter-group select {
    padding: 10px 14px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    color: var(--jsa-grey-700);
    background: var(--jsa-white);
    cursor: pointer;
    transition: border-color 0.2s ease;
}

.filter-group select:focus {
    outline: none;
    border-color: var(--jsa-teal);
}

#skillsTable_wrapper {
    background: var(--jsa-white);
}

.table {
    font-size: 0.85rem;
}

.table thead th {
    background: var(--jsa-navy);
    color: var(--jsa-white);
    font-weight: 600;
    border: none;
    padding: 14px 12px;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.table tbody td {
    padding: 12px;
    vertical-align: middle;
    border-bottom: 1px solid var(--jsa-grey-200);
}

.table tbody tr:hover {
    background: rgba(0, 131, 143, 0.03);
}

.dataTables_wrapper .dataTables_paginate .paginate_button.current {
    background: var(--jsa-teal) !important;
    color: white !important;
    border: none !important;
}

.dataTables_wrapper .dataTables_paginate .paginate_button:hover {
    background: var(--jsa-navy) !important;
    color: white !important;
    border: none !important;
}

/* ========================================
   Buttons
   ======================================== */

.btn-custom {
    padding: 10px 20px;
    border-radius: var(--radius-md);
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
}

.btn-primary-custom {
    background: var(--jsa-teal);
    color: var(--jsa-white);
}

.btn-primary-custom:hover {
    background: var(--jsa-navy);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn-outline-custom {
    background: var(--jsa-white);
    color: var(--jsa-navy);
    border: 2px solid var(--jsa-grey-300);
}

.btn-outline-custom:hover {
    border-color: var(--jsa-teal);
    color: var(--jsa-teal);
    background: rgba(0, 131, 143, 0.05);
}

.export-buttons {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

/* ========================================
   Confidence Indicator
   ======================================== */

.confidence-bar {
    width: 100%;
    height: 6px;
    background: var(--jsa-grey-200);
    border-radius: 3px;
    overflow: hidden;
}

.confidence-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.confidence-high { background: var(--jsa-green); }
.confidence-medium { background: var(--jsa-gold); }
.confidence-low { background: var(--jsa-orange); }

/* ========================================
   Responsive
   ======================================== */

@media (max-width: 768px) {
    .header h1 { font-size: 1.5rem; }
    .stats-dashboard { 
        grid-template-columns: repeat(2, 1fr); 
        margin-top: -24px;
    }
    .view-tabs { overflow-x: auto; }
    .tree-search { min-width: 100%; }
    .skill-meta-grid { grid-template-columns: 1fr; }
}

/* ========================================
   Print Styles
   ======================================== */

@media print {
    .header { background: var(--jsa-navy) !important; }
    .btn-custom, .tree-controls, .view-tabs-container { display: none !important; }
    .content-area { box-shadow: none !important; border: none !important; }
}
"""


BODY_CONTENT = """
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
                <p>Comprehensive taxonomy of vocational education and training skills across multiple dimensions</p>
            </div>
        </div>
    </div>
</div>

<div class="stats-dashboard" id="statsDashboard">
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
        <div class="view-section active" id="treeView">
            <div class="tree-controls">
                <input type="text" class="tree-search" id="treeSearch" 
                       placeholder="Search skills, domains, families, or codes...">
                <button class="btn-custom btn-outline-custom" onclick="expandAll()">
                    <i class="bi bi-arrows-expand"></i> Expand All
                </button>
                <button class="btn-custom btn-outline-custom" onclick="collapseAll()">
                    <i class="bi bi-arrows-collapse"></i> Collapse All
                </button>
            </div>
            <div class="tree-container" id="treeContainer"></div>
        </div>

        <div class="view-section" id="tableView">
            <div class="export-buttons">
                <button class="btn-custom btn-primary-custom" onclick="exportToExcel()">
                    <i class="bi bi-file-earmark-excel"></i> Export to Excel
                </button>
                <button class="btn-custom btn-outline-custom" onclick="exportToCSV()">
                    <i class="bi bi-file-earmark-spreadsheet"></i> Export CSV
                </button>
                <button class="btn-custom btn-outline-custom" onclick="exportToJSON()">
                    <i class="bi bi-file-earmark-code"></i> Export JSON
                </button>
            </div>

            <div class="table-controls">
                <div class="filter-group">
                    <select id="filterDomain">
                        <option value="">All Domains</option>
                    </select>
                    <select id="filterComplexity">
                        <option value="">All Complexity</option>
                        <option value="1">1 - FOLLOW</option>
                        <option value="2">2 - ASSIST</option>
                        <option value="3">3 - APPLY</option>
                        <option value="4">4 - ENABLE</option>
                        <option value="5">5 - ENSURE_ADVI</option>
                    </select>
                    <select id="filterCategory">
                        <option value="">All Categories</option>
                    </select>
                </div>
            </div>

            <table id="skillsTable" class="table table-hover">
                <thead>
                    <tr>
                        <th>Skill ID</th>
                        <th>Skill Name</th>
                        <th>Domain</th>
                        <th>Family</th>
                        <th>Category</th>
                        <th>Complexity</th>
                        <th>Confidence</th>
                        <th>Related Codes</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>
"""


JAVASCRIPT_CONTENT = """
let taxonomyData = EMBEDDED_TAXONOMY_DATA;
let flatSkillsData = [];
let dataTable = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    flatSkillsData = flattenTaxonomy(taxonomyData);
    initializeStats();
    renderTree();
    initializeTable();
});

function flattenTaxonomy(node, path = [], result = []) {
    // For groups, extract skills
    if (node.type === 'group' && node.skills) {
        node.skills.forEach(skill => {
            result.push({
                ...skill,
                domain: path[0] || '',
                family: path[1] || '',
                cluster: path[2] || '',
                group: node.name || ''
            });
        });
    }
    
    // Legacy support: if skills are directly in a non-group node
    if (node.skills && node.type !== 'group') {
        node.skills.forEach(skill => {
            result.push({
                ...skill,
                domain: path[0] || '',
                family: path[1] || '',
                cluster: path[2] || '',
                group: ''
            });
        });
    }

    if (node.children) {
        node.children.forEach(child => {
            const newPath = [...path];
            
            if (node.type === 'domain') {
                newPath[0] = node.name;
            } else if (node.type === 'family') {
                newPath[1] = node.name;
            } else if (node.type === 'cluster') {
                newPath[2] = node.name;
            }
            
            flattenTaxonomy(child, newPath, result);
        });
    }

    return result;
}

function initializeStats() {
    const stats = taxonomyData.metadata?.statistics || {};
    document.getElementById('totalSkills').textContent = (stats.total_skills || flatSkillsData.length).toLocaleString();
    document.getElementById('totalDomains').textContent = stats.total_domains || taxonomyData.children?.length || 0;
    document.getElementById('totalFamilies').textContent = stats.total_families || countNodeType(taxonomyData, 'family');
    document.getElementById('totalCodes').textContent = (stats.total_related_codes || countTotalCodes()).toLocaleString();
    document.getElementById('totalKeywords').textContent = (stats.total_related_keywords || countTotalKeywords()).toLocaleString();
}

function countTotalCodes() {
    const uniqueCodes = new Set();
    flatSkillsData.forEach(s => {
        if (s.all_related_codes && Array.isArray(s.all_related_codes)) {
            s.all_related_codes.forEach(code => uniqueCodes.add(code));
        }
    });
    return uniqueCodes.size;
}

function countTotalKeywords() {
    return flatSkillsData.reduce((sum, s) => sum + (s.all_related_kw?.length || 0), 0);
}

function countNodeType(node, type) {
    let count = 0;
    if (node.type === type) count++;
    if (node.children) {
        node.children.forEach(child => { count += countNodeType(child, type); });
    }
    return count;
}

function renderTree() {
    const container = document.getElementById('treeContainer');
    container.innerHTML = '';
    if (taxonomyData.children) {
        taxonomyData.children.forEach(domain => {
            container.appendChild(createTreeNode(domain, 0));
        });
    }
}

function createTreeNode(node, level) {
    const nodeDiv = document.createElement('div');
    nodeDiv.className = 'tree-node';
    nodeDiv.dataset.nodeId = node.id || node.name;
    nodeDiv.dataset.nodeType = node.type;
    
    const hasChildren = (node.children && node.children.length > 0) || (node.skills && node.skills.length > 0);
    const contentDiv = document.createElement('div');
    contentDiv.className = `node-content node-${node.type}`;
    
    if (hasChildren) {
        const toggle = document.createElement('span');
        toggle.className = 'node-toggle';
        toggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
        toggle.onclick = (e) => { e.stopPropagation(); toggleNode(nodeDiv); };
        contentDiv.appendChild(toggle);
    } else {
        const spacer = document.createElement('span');
        spacer.className = 'node-toggle';
        contentDiv.appendChild(spacer);
    }
    
    const icon = document.createElement('i');
    icon.className = 'bi node-icon';
    if (node.type === 'domain') icon.classList.add('bi-folder2-open');
    else if (node.type === 'family') icon.classList.add('bi-collection');
    else if (node.type === 'cluster') icon.classList.add('bi-grid-3x3-gap');
    else if (node.type === 'group') icon.classList.add('bi-layers');
    else if (node.type === 'skill') icon.classList.add('bi-mortarboard');
    else icon.classList.add('bi-circle-fill');
    contentDiv.appendChild(icon);
    
    const label = document.createElement('span');
    label.className = 'node-label';
    label.textContent = node.name;
    contentDiv.appendChild(label);
    
    if (node.statistics?.size || node.size) {
        const badge = document.createElement('span');
        badge.className = 'node-badge';
        badge.textContent = `${node.statistics?.size || node.size} skills`;
        contentDiv.appendChild(badge);
    }
    
    nodeDiv.appendChild(contentDiv);
    
    if (hasChildren) {
        const childrenDiv = document.createElement('div');
        childrenDiv.className = 'node-children';
        
        if (node.children) {
            node.children.forEach(child => {
                childrenDiv.appendChild(createTreeNode(child, level + 1));
            });
        }
        
        if (node.skills) {
            node.skills.forEach(skill => {
                childrenDiv.appendChild(createSkillNode(skill));
            });
        }
        
        nodeDiv.appendChild(childrenDiv);
    }
    
    return nodeDiv;
}

function createSkillNode(skill) {
    const skillDiv = document.createElement('div');
    skillDiv.className = 'skill-detail';
    
    // Header with name and ID
    const headerDiv = document.createElement('div');
    headerDiv.className = 'skill-header';
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'skill-name';
    nameDiv.innerHTML = `<i class="bi bi-mortarboard-fill"></i> ${skill.name}`;
    headerDiv.appendChild(nameDiv);
    
    const idDiv = document.createElement('div');
    idDiv.className = 'skill-id';
    idDiv.textContent = skill.id || 'N/A';
    headerDiv.appendChild(idDiv);
    
    skillDiv.appendChild(headerDiv);
    
    // Description
    if (skill.description) {
        const descDiv = document.createElement('div');
        descDiv.className = 'skill-description';
        descDiv.textContent = skill.description;
        skillDiv.appendChild(descDiv);
    }
    
    // Meta Grid
    const metaGrid = document.createElement('div');
    metaGrid.className = 'skill-meta-grid';
    
    // Confidence
    const confItem = document.createElement('div');
    confItem.className = 'skill-meta-item';
    const confLevel = (skill.confidence || 0) * 100;
    const confClass = confLevel >= 80 ? 'high' : (confLevel >= 50 ? 'medium' : 'low');
    confItem.innerHTML = `
        <div class="skill-meta-label">Confidence</div>
        <div class="skill-meta-value">${confLevel.toFixed(0)}%</div>
        <div class="confidence-bar"><div class="confidence-fill confidence-${confClass}" style="width: ${confLevel}%"></div></div>
    `;
    metaGrid.appendChild(confItem);
    
    // Level
    const levelItem = document.createElement('div');
    levelItem.className = 'skill-meta-item';
    levelItem.innerHTML = `
        <div class="skill-meta-label">Skill Level</div>
        <div class="skill-meta-value">Level ${skill.level || 'N/A'}</div>
    `;
    metaGrid.appendChild(levelItem);
    
    // Code
    if (skill.code) {
        const codeItem = document.createElement('div');
        codeItem.className = 'skill-meta-item';
        codeItem.innerHTML = `
            <div class="skill-meta-label">Primary Code</div>
            <div class="skill-meta-value" style="font-family: monospace;">${skill.code}</div>
        `;
        metaGrid.appendChild(codeItem);
    }
    
    skillDiv.appendChild(metaGrid);
    
    // Dimensions (including Category)
    const dimsDiv = document.createElement('div');
    dimsDiv.className = 'skill-dimensions';
    
    // Category badge
    if (skill.category) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-category"><i class="bi bi-bookmark"></i> ${skill.category}</span>`;
    }
    
    const dims = skill.dimensions || {};
    if (dims.complexity_level) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-complexity"><i class="bi bi-bar-chart"></i> Level ${dims.complexity_level}</span>`;
    }
    if (dims.transferability) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-transferability"><i class="bi bi-arrow-left-right"></i> ${formatLabel(dims.transferability)}</span>`;
    }
    if (dims.digital_intensity !== undefined) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-digital"><i class="bi bi-cpu"></i> Digital ${dims.digital_intensity}</span>`;
    }
    if (dims.future_readiness) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-future"><i class="bi bi-graph-up-arrow"></i> ${formatLabel(dims.future_readiness)}</span>`;
    }
    if (dims.skill_nature) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-nature"><i class="bi bi-gear"></i> ${formatLabel(dims.skill_nature)}</span>`;
    }
    if (skill.context) {
        dimsDiv.innerHTML += `<span class="dimension-badge dim-context"><i class="bi bi-book"></i> ${formatLabel(skill.context)}</span>`;
    }
    
    skillDiv.appendChild(dimsDiv);
    
    // Alternative Titles
    const altTitles = skill.alternative_titles || [];
    if (altTitles.length > 0) {
        const altSection = document.createElement('div');
        altSection.className = 'alt-titles-section';
        altSection.innerHTML = `<div class="alt-titles-label"><i class="bi bi-card-heading"></i> Alternative Titles (${altTitles.length})</div>`;
        altTitles.forEach(title => {
            altSection.innerHTML += `<span class="alt-title-tag">${title}</span>`;
        });
        skillDiv.appendChild(altSection);
    }
    
    // All Related Codes
    const relatedCodes = skill.all_related_codes || [];
    if (relatedCodes.length > 0) {
        const codesSection = document.createElement('div');
        codesSection.className = 'related-section';
        codesSection.innerHTML = `<div class="related-label"><i class="bi bi-upc-scan"></i> Related UOC Codes (${relatedCodes.length})</div>`;
        relatedCodes.slice(0, 10).forEach(code => {
            codesSection.innerHTML += `<span class="code-tag">${code}</span>`;
        });
        if (relatedCodes.length > 10) {
            codesSection.innerHTML += `<span class="code-tag">+${relatedCodes.length - 10} more</span>`;
        }
        skillDiv.appendChild(codesSection);
    }
    
    // All Related Keywords
    const relatedKW = skill.all_related_kw || [];
    if (relatedKW.length > 0) {
        const kwSection = document.createElement('div');
        kwSection.className = 'related-section';
        kwSection.innerHTML = `<div class="related-label"><i class="bi bi-tags"></i> Related Keywords (${relatedKW.length})</div>`;
        relatedKW.slice(0, 15).forEach(kw => {
            kwSection.innerHTML += `<span class="keyword-tag">${kw}</span>`;
        });
        if (relatedKW.length > 15) {
            kwSection.innerHTML += `<span class="keyword-tag">+${relatedKW.length - 15} more</span>`;
        }
        skillDiv.appendChild(kwSection);
    }
    
    // Related Skills with Similarity Scores
    if (skill.relationships?.related && skill.relationships.related.length > 0) {
        const relSection = document.createElement('div');
        relSection.className = 'related-skills-section';
        relSection.innerHTML = `<div class="related-label"><i class="bi bi-link-45deg"></i> Related Skills</div>`;
        
        skill.relationships.related.forEach(rel => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'relationship-link';
            const simScore = rel.similarity ? `<span class="similarity-score">(${(rel.similarity * 100).toFixed(0)}%)</span>` : '';
            link.innerHTML = `<i class="bi bi-arrow-right-short"></i> ${rel.skill_name} ${simScore}`;
            link.onclick = (e) => { e.preventDefault(); searchAndHighlight(rel.skill_id); };
            relSection.appendChild(link);
        });
        
        skillDiv.appendChild(relSection);
    }
    
    return skillDiv;
}

function formatLabel(str) {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}

function toggleNode(nodeDiv) {
    const toggle = nodeDiv.querySelector('.node-toggle');
    const content = nodeDiv.querySelector('.node-content');
    const children = nodeDiv.querySelector('.node-children');
    
    if (children) {
        const isExpanded = children.classList.contains('expanded');
        if (isExpanded) {
            children.classList.remove('expanded');
            content.classList.remove('expanded');
        } else {
            children.classList.add('expanded');
            content.classList.add('expanded');
        }
    }
}

function expandAll() {
    document.querySelectorAll('.node-children').forEach(child => child.classList.add('expanded'));
    document.querySelectorAll('.node-content').forEach(content => content.classList.add('expanded'));
}

function collapseAll() {
    document.querySelectorAll('.node-children').forEach(child => child.classList.remove('expanded'));
    document.querySelectorAll('.node-content').forEach(content => content.classList.remove('expanded'));
}

function searchAndHighlight(query) {
    const searchTerm = query.toLowerCase();
    document.querySelectorAll('.tree-node').forEach(node => {
        const text = node.textContent.toLowerCase();
        node.style.display = text.includes(searchTerm) ? '' : 'none';
        
        if (text.includes(searchTerm)) {
            let parent = node.parentElement;
            while (parent) {
                if (parent.classList.contains('node-children')) {
                    parent.classList.add('expanded');
                    const parentNode = parent.parentElement;
                    if (parentNode) {
                        const content = parentNode.querySelector('.node-content');
                        if (content) content.classList.add('expanded');
                    }
                }
                parent = parent.parentElement;
            }
        }
    });
}

document.getElementById('treeSearch')?.addEventListener('input', (e) => {
    const query = e.target.value;
    if (query.length > 0) {
        searchAndHighlight(query);
    } else {
        document.querySelectorAll('.tree-node').forEach(node => { node.style.display = ''; });
    }
});

function initializeTable() {
    // Populate domain filter
    const domains = [...new Set(flatSkillsData.map(s => s.domain).filter(Boolean))];
    const domainSelect = document.getElementById('filterDomain');
    domains.sort().forEach(domain => {
        const option = document.createElement('option');
        option.value = domain;
        option.textContent = domain;
        domainSelect.appendChild(option);
    });
    
    // Populate category filter
    const categories = [...new Set(flatSkillsData.map(s => s.category).filter(Boolean))];
    const categorySelect = document.getElementById('filterCategory');
    categories.sort().forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = formatLabel(cat);
        categorySelect.appendChild(option);
    });
    
    if (dataTable) dataTable.destroy();
    
    dataTable = $('#skillsTable').DataTable({
        data: flatSkillsData,
        columns: [
            { data: 'id', render: (data) => `<span style="font-family: monospace; font-size: 0.8rem;">${data || '-'}</span>` },
            { data: 'name' },
            { data: 'domain' },
            { data: 'family' },
            { data: 'category', render: (data) => formatLabel(data) || '-' },
            { data: 'dimensions.complexity_level', render: (data) => data ? `Level ${data}` : '-' },
            { data: 'confidence', render: (data) => data ? `${(data * 100).toFixed(0)}%` : '-' },
            { data: 'all_related_codes', render: (data) => {
                if (!data || data.length === 0) return '-';
                const display = data.slice(0, 3).join(', ');
                return data.length > 3 ? `${display} +${data.length - 3}` : display;
            }}
        ],
        pageLength: 25,
        responsive: true,
        order: [[1, 'asc']],
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ skills per page"
        }
    });
    
    ['filterDomain', 'filterComplexity', 'filterCategory'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', applyFilters);
    });
}

function applyFilters() {
    const domain = document.getElementById('filterDomain').value;
    const complexity = document.getElementById('filterComplexity').value;
    const category = document.getElementById('filterCategory').value;
    
    let filtered = flatSkillsData;
    
    if (domain) filtered = filtered.filter(s => s.domain === domain);
    if (complexity) filtered = filtered.filter(s => s.dimensions?.complexity_level === parseInt(complexity));
    if (category) filtered = filtered.filter(s => s.category === category);
    
    dataTable.clear().rows.add(filtered).draw();
}

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
        'All Related Keywords': (s.all_related_kw || []).join('; '),
        'Assignment Family': s.assignment?.family || '',
        'Assignment Method': s.assignment?.method || '',
        'Assignment Confidence': s.assignment?.confidence ? (s.assignment.confidence * 100).toFixed(1) + '%' : ''
    }));
    
    const ws = XLSX.utils.json_to_sheet(exportData);
    
    // Set column widths
    ws['!cols'] = [
        {wch: 12}, {wch: 40}, {wch: 60}, {wch: 25}, {wch: 25}, {wch: 20},
        {wch: 15}, {wch: 8}, {wch: 12}, {wch: 10}, {wch: 15}, {wch: 18},
        {wch: 15}, {wch: 15}, {wch: 15}, {wch: 15}, {wch: 50}, {wch: 50}, {wch: 80},
        {wch: 25}, {wch: 20}, {wch: 18}
    ];
    
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Skills Taxonomy');
    
    // Add metadata sheet
    const metaData = [
        ['VET Skills Taxonomy Export'],
        [''],
        ['Export Date', new Date().toISOString()],
        ['Total Skills', flatSkillsData.length],
        ['Total Domains', taxonomyData.metadata?.statistics?.total_domains || ''],
        ['Total Families', taxonomyData.metadata?.statistics?.total_families || ''],
        ['Total Related Codes', taxonomyData.metadata?.statistics?.total_related_codes || ''],
        ['Total Related Keywords', taxonomyData.metadata?.statistics?.total_related_keywords || '']
    ];
    const metaWs = XLSX.utils.aoa_to_sheet(metaData);
    XLSX.utils.book_append_sheet(wb, metaWs, 'Metadata');
    
    XLSX.writeFile(wb, 'vet_skills_taxonomy.xlsx');
}

function exportToCSV() {
    const headers = ['Skill ID', 'Name', 'Domain', 'Family', 'Category', 'Level', 'Complexity', 
                     'Confidence', 'Primary Code', 'Alternative Titles', 'Related Codes', 'Related Keywords'];
    const rows = flatSkillsData.map(s => [
        s.id, s.name, s.domain, s.family, s.category || '',
        s.level || '', s.dimensions?.complexity_level || '',
        s.confidence ? (s.confidence * 100).toFixed(0) + '%' : '',
        s.code || '',
        (s.alternative_titles || []).join('; '),
        (s.all_related_codes || []).join('; '),
        (s.all_related_kw || []).join('; ')
    ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','));
    
    const csv = [headers.join(','), ...rows].join('\\n');
    downloadFile(csv, 'vet_skills_taxonomy.csv', 'text/csv');
}

function exportToJSON() {
    const json = JSON.stringify(taxonomyData, null, 2);
    downloadFile(json, 'vet_skills_taxonomy.json', 'application/json');
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

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
"""


def generate_html(taxonomy_json_path: str, output_html_path: str):
    """Generate standalone HTML with embedded taxonomy data"""
    
    print(f"Loading taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)
    
    print(f"Taxonomy loaded: {len(taxonomy_data.get('children', []))} domains")
    
    # Create HTML with embedded data
    html_content = HTML_TEMPLATE.format(
        CSS_CONTENT=CSS_CONTENT,
        BODY_CONTENT=BODY_CONTENT,
        TAXONOMY_DATA=json.dumps(taxonomy_data, indent=2),
        JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT
    )
    
    print(f"Writing HTML to: {output_html_path}")
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ HTML visualization generated successfully!")
    print(f"\nOpen {output_html_path} in your web browser to view the interactive taxonomy.")


def flatten_taxonomy_to_dataframe(taxonomy_data: dict) -> pd.DataFrame:
    """Flatten taxonomy to a pandas DataFrame for Excel export"""
    
    flat_skills = []
    
    def extract_skills(node, path=None):
        if path is None:
            path = {'domain': '', 'family': '', 'group': ''}
        
        # Update path based on node type
        if node.get('type') == 'domain':
            path = {**path, 'domain': node.get('name', '')}
        elif node.get('type') == 'family':
            path = {**path, 'family': node.get('name', '')}
        elif node.get('type') == 'group':
            path = {**path, 'group': node.get('name', '')}
        
        # Extract skills from this node
        if 'skills' in node and node['skills']:
            for skill in node['skills']:
                dims = skill.get('dimensions', {})
                assignment = skill.get('assignment', {})
                
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
                    'complexity_level': dims.get('complexity_level', ''),
                    'transferability': dims.get('transferability', ''),
                    'digital_intensity': dims.get('digital_intensity', ''),
                    'future_readiness': dims.get('future_readiness', ''),
                    'skill_nature': dims.get('skill_nature', ''),
                    'primary_code': skill.get('code', ''),
                    'alternative_titles': '; '.join(skill.get('alternative_titles', [])),
                    'all_related_codes': '; '.join(skill.get('all_related_codes', [])),
                    'all_related_keywords': '; '.join(skill.get('all_related_kw', [])),
                    'assignment_family': assignment.get('family', ''),
                    'assignment_method': assignment.get('method', ''),
                    'assignment_confidence': assignment.get('confidence', ''),
                })
        
        # Recursively process children
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
    
    # Create Excel writer with xlsxwriter engine for formatting
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Skills Taxonomy', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Skills Taxonomy']
        
        # Auto-adjust column widths
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            # Cap at 60 characters
            max_length = min(max_length, 60)
            worksheet.column_dimensions[chr(65 + idx) if idx < 26 else f'A{chr(65 + idx - 26)}'[:2]].width = max_length
        
        # Create metadata sheet
        metadata = taxonomy_data.get('metadata', {})
        stats = metadata.get('statistics', {})
        
        meta_df = pd.DataFrame([
            ['VET Skills Taxonomy Export', ''],
            ['', ''],
            ['Export Date', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Skills', stats.get('total_skills', len(df))],
            ['Total Domains', stats.get('total_domains', '')],
            ['Total Families', stats.get('total_families', '')],
            ['Total Related Codes', stats.get('total_related_codes', '')],
            ['Total Related Keywords', stats.get('total_related_keywords', '')],
            ['Total Alternative Titles', stats.get('total_alternative_titles', '')],
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
    
    # Generate HTML visualization
    generate_html(taxonomy_path, html_output_path)
    
    # Export to Excel
    try:
        export_taxonomy_to_excel(taxonomy_path, excel_output_path)
    except Exception as e:
        print(f"Warning: Could not export to Excel: {e}")
        print("Make sure pandas and openpyxl are installed.")