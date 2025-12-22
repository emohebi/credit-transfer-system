"""
Generate Interactive Multi-View HTML Visualization for Faceted Taxonomy

This script creates a performant HTML visualization with multiple tabs/views
for exploring skills across different facet dimensions.

Views:
- Overview Dashboard
- Skill Nature View
- Transferability View
- Cognitive Complexity View
- Work Context View
- Future Readiness View
- Industry Domain View
- Digital Intensity View
- Table/Export View

Usage:
    python generate_faceted_visualization.py faceted_taxonomy.json output.html
"""

import json
import sys
from pathlib import Path
import pandas as pd

# Threshold for external data loading
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
    max-width: 1600px;
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
    max-width: 1600px;
    margin: 0 auto;
    padding: 24px;
}

.header h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 6px; }
.header p { font-size: 0.95rem; opacity: 0.9; }

.header-logo {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}

.header-logo-icon {
    width: 44px;
    height: 44px;
    background: var(--jsa-teal);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-logo-icon i { font-size: 1.3rem; color: white; }

/* Main Container */
.main-container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 0 24px 48px;
}

/* Stats Dashboard */
.stats-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-top: -32px;
    padding: 0 24px;
    max-width: 1600px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    z-index: 10;
}

.stat-card {
    background: var(--jsa-white);
    padding: 14px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    text-align: center;
    border: 1px solid var(--jsa-grey-200);
}

.stat-card i { font-size: 1.3rem; color: var(--jsa-teal); margin-bottom: 4px; }
.stat-value { font-size: 1.4rem; font-weight: 700; color: var(--jsa-navy); }
.stat-label { font-size: 0.7rem; color: var(--jsa-grey-500); text-transform: uppercase; letter-spacing: 0.5px; }

/* View Tabs */
.view-tabs-container {
    background: var(--jsa-white);
    margin-top: 20px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--jsa-grey-200);
    border-bottom: none;
    overflow-x: auto;
}

.view-tabs { 
    display: flex; 
    padding: 0 12px; 
    gap: 2px;
    min-width: max-content;
}

.view-tab {
    padding: 12px 16px;
    cursor: pointer;
    border: none;
    background: transparent;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--jsa-grey-500);
    border-bottom: 3px solid transparent;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
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
    min-height: 600px;
}

.view-section { display: none; padding: 20px; }
.view-section.active { display: block; }

/* Facet View Layout */
.facet-view {
    display: grid;
    grid-template-columns: 280px 1fr 400px;
    gap: 20px;
    min-height: 550px;
    align-items: start;
}

.facet-sidebar {
    border-right: 1px solid var(--jsa-grey-200);
    padding-right: 20px;
    align-self: start;
}

.facet-main {
    /* No scroll - page scrolls instead */
}

.facet-detail {
    border-left: 1px solid var(--jsa-grey-200);
    padding-left: 20px;
    align-self: start;
}

.facet-detail-header {
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--jsa-grey-200);
}

.facet-detail-header h3 {
    font-size: 0.9rem;
    color: var(--jsa-grey-500);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.facet-detail-header h3 i {
    color: var(--jsa-teal);
}

/* Facet Category Cards */
.facet-category {
    background: var(--jsa-grey-100);
    border-radius: var(--radius-md);
    padding: 12px;
    margin-bottom: 10px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}

.facet-category:hover { background: var(--jsa-grey-200); }
.facet-category.active { border-color: var(--jsa-teal); background: rgba(0, 131, 143, 0.08); }

.facet-category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.facet-category-name { font-weight: 600; color: var(--jsa-navy); font-size: 0.9rem; }
.facet-category-count { 
    background: var(--jsa-teal); 
    color: white; 
    padding: 2px 8px; 
    border-radius: 12px; 
    font-size: 0.75rem; 
    font-weight: 600;
}

.facet-category-desc { font-size: 0.8rem; color: var(--jsa-grey-600); }

/* Skill Cards in Grid */
.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
}

.skill-card-mini {
    background: var(--jsa-white);
    border: 1px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    padding: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.skill-card-mini:hover { border-color: var(--jsa-teal); box-shadow: var(--shadow-md); }
.skill-card-mini.selected { border-color: var(--jsa-teal); background: rgba(0, 131, 143, 0.05); }

.skill-card-mini-name {
    font-weight: 600;
    color: var(--jsa-grey-800);
    font-size: 0.9rem;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.skill-card-mini-meta {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.skill-mini-badge {
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--jsa-grey-100);
    color: var(--jsa-grey-600);
}

.skill-mini-badge.level { background: #e3f2fd; color: #1565c0; }
.skill-mini-badge.category { background: #fff8e1; color: #f57f17; }

/* Detail Panel */
.detail-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--jsa-grey-400);
    text-align: center;
}

.detail-placeholder i { font-size: 3rem; margin-bottom: 12px; opacity: 0.5; }

.skill-detail-card {
    animation: fadeIn 0.2s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.skill-detail-header { margin-bottom: 16px; }

.skill-detail-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--jsa-navy);
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.skill-detail-name i { color: var(--jsa-green); }

.skill-detail-id {
    display: inline-block;
    font-size: 0.75rem;
    color: var(--jsa-grey-500);
    background: var(--jsa-grey-100);
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    font-family: 'Monaco', 'Consolas', monospace;
}

.skill-detail-desc {
    font-size: 0.9rem;
    color: var(--jsa-grey-600);
    line-height: 1.6;
    margin: 16px 0;
    padding: 12px;
    background: var(--jsa-grey-100);
    border-radius: var(--radius-md);
}

.detail-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--jsa-grey-200);
}

.detail-section-title {
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

/* Facet Badges */
.facet-badges { display: flex; flex-wrap: wrap; gap: 6px; }

.facet-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 500;
}

.facet-badge.NAT { background: #fff3e0; color: #e65100; }
.facet-badge.TRF { background: #f3e5f5; color: #7b1fa2; }
.facet-badge.COG { background: #e3f2fd; color: #1565c0; }
.facet-badge.CTX { background: #e8f5e9; color: #2e7d32; }
.facet-badge.FUT { background: #fce4ec; color: #c2185b; }
.facet-badge.LRN { background: #e0f7fa; color: #00695c; }
.facet-badge.DIG { background: #ede7f6; color: #512da8; }
.facet-badge.IND { background: #fff8e1; color: #ff8f00; }
.facet-badge.LVL { background: #e8eaf6; color: #3f51b5; }

/* Tags */
.tag-list { display: flex; flex-wrap: wrap; gap: 4px; }

.tag {
    display: inline-block;
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
}

.tag-alt { background: var(--jsa-grey-100); color: var(--jsa-grey-600); }
.tag-code { background: #e8eaf6; color: #3949ab; font-family: monospace; font-size: 0.7rem; }
.tag-keyword { background: #e0f7fa; color: #00838f; }
.tag-more { background: var(--jsa-grey-200); color: var(--jsa-grey-500); font-style: italic; }

/* Dimensions List */
.dimensions-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.dimension-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid var(--jsa-grey-100);
}

.dimension-row:last-child {
    border-bottom: none;
}

.dimension-label {
    font-size: 0.8rem;
    color: var(--jsa-grey-600);
    font-weight: 500;
}

.dimension-value {
    display: flex;
    align-items: center;
    gap: 8px;
}

.facet-confidence {
    font-size: 0.7rem;
    color: var(--jsa-grey-500);
    background: var(--jsa-white);
    padding: 2px 6px;
    border-radius: 10px;
    border: 1px solid var(--jsa-grey-200);
}

/* Related Skills */
.related-skills-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.related-skill-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    background: var(--jsa-grey-100);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 0.2s;
}

.related-skill-item:hover {
    background: rgba(0, 131, 143, 0.1);
}

.related-skill-name {
    font-size: 0.85rem;
    color: var(--jsa-grey-700);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.related-skill-score {
    font-size: 0.7rem;
    color: var(--jsa-grey-500);
    background: var(--jsa-white);
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 8px;
}

/* Search Bar */
.facet-search {
    margin-bottom: 16px;
}

.facet-search input {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.9rem;
}

.facet-search input:focus { outline: none; border-color: var(--jsa-teal); }

/* Overview Dashboard */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.overview-card {
    background: var(--jsa-white);
    border: 1px solid var(--jsa-grey-200);
    border-radius: var(--radius-lg);
    padding: 20px;
}

.overview-card h3 {
    font-size: 1rem;
    color: var(--jsa-navy);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.overview-card h3 i { color: var(--jsa-teal); }

.chart-bar {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.chart-bar-label {
    width: 120px;
    font-size: 0.8rem;
    color: var(--jsa-grey-600);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.chart-bar-track {
    flex: 1;
    height: 20px;
    background: var(--jsa-grey-100);
    border-radius: 4px;
    margin: 0 10px;
    overflow: hidden;
}

.chart-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
}

.chart-bar-value {
    width: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--jsa-grey-700);
    text-align: right;
}

/* Multi-Filter View */
.filter-view {
    display: grid;
    grid-template-columns: 320px 1fr 400px;
    gap: 20px;
    min-height: 550px;
    align-items: start;
}

.filter-sidebar {
    border-right: 1px solid var(--jsa-grey-200);
    padding-right: 20px;
    align-self: start;
}

.filter-section {
    margin-bottom: 16px;
}

.filter-section-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--jsa-grey-600);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.filter-select {
    width: 100%;
    padding: 8px 12px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    background: var(--jsa-white);
    cursor: pointer;
}

.filter-select:focus {
    outline: none;
    border-color: var(--jsa-teal);
}

.filter-actions {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--jsa-grey-200);
    display: flex;
    gap: 10px;
}

.filter-btn {
    flex: 1;
    padding: 10px 16px;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

.filter-btn-apply {
    background: var(--jsa-teal);
    color: white;
    border: none;
}

.filter-btn-apply:hover {
    background: #006874;
}

.filter-btn-clear {
    background: var(--jsa-white);
    color: var(--jsa-grey-600);
    border: 2px solid var(--jsa-grey-300);
}

.filter-btn-clear:hover {
    background: var(--jsa-grey-100);
}

.filter-results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--jsa-grey-200);
}

.filter-results-count {
    font-size: 0.9rem;
    color: var(--jsa-grey-600);
}

.filter-results-count strong {
    color: var(--jsa-teal);
}

.filter-main {
    /* Skills grid area */
}

.filter-detail {
    border-left: 1px solid var(--jsa-grey-200);
    padding-left: 20px;
    align-self: start;
}

.active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
}

.active-filter-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: rgba(0, 131, 143, 0.1);
    color: var(--jsa-teal);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-weight: 500;
}

.active-filter-tag i {
    cursor: pointer;
    opacity: 0.7;
}

.active-filter-tag i:hover {
    opacity: 1;
}

/* Table View */
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

.btn-primary { background: var(--jsa-teal); color: var(--jsa-white); }
.btn-primary:hover { background: var(--jsa-navy); }
.btn-outline { background: var(--jsa-white); color: var(--jsa-navy); border: 2px solid var(--jsa-grey-300); }
.btn-outline:hover { border-color: var(--jsa-teal); color: var(--jsa-teal); }

.filter-group { display: flex; gap: 8px; flex-wrap: wrap; flex: 1; }

.filter-group select, .filter-group input {
    padding: 8px 12px;
    border: 2px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    background: var(--jsa-white);
}

.table-wrapper {
    overflow: auto;
    border: 1px solid var(--jsa-grey-200);
    border-radius: var(--radius-md);
    max-height: 500px;
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
    padding: 10px 8px;
    text-align: left;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.skills-table td {
    padding: 8px;
    border-bottom: 1px solid var(--jsa-grey-200);
    max-width: 200px;
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
@media (max-width: 1200px) {
    .facet-view { grid-template-columns: 240px 1fr; }
    .facet-detail { display: none; }
}

@media (max-width: 768px) {
    .header h1 { font-size: 1.3rem; }
    .stats-dashboard { grid-template-columns: repeat(2, 1fr); margin-top: -20px; }
    .facet-view { grid-template-columns: 1fr; }
    .facet-sidebar { border-right: none; border-bottom: 1px solid var(--jsa-grey-200); padding-right: 0; padding-bottom: 16px; }
}
"""


BODY_CONTENT = """
<div id="loadingOverlay" class="loading-overlay">
    <div class="loading-spinner"></div>
    <div class="loading-text">Loading faceted taxonomy data...</div>
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
                <i class="bi bi-grid-3x3-gap"></i>
            </div>
            <div>
                <h1>VET Skills Faceted Explorer</h1>
                <p>Multi-dimensional taxonomy of vocational skills</p>
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
        <i class="bi bi-grid-3x3-gap"></i>
        <div class="stat-value" id="totalFacets">-</div>
        <div class="stat-label">Facets</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-upc-scan"></i>
        <div class="stat-value" id="totalCodes">-</div>
        <div class="stat-label">Unit Codes</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-card-heading"></i>
        <div class="stat-value" id="totalAltTitles">-</div>
        <div class="stat-label">Alt. Titles</div>
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
            <button class="view-tab active" data-view="overview">
                <i class="bi bi-speedometer2"></i> Overview
            </button>
            <button class="view-tab" data-view="NAT">
                <i class="bi bi-bookmark"></i> Skill Nature
            </button>
            <button class="view-tab" data-view="TRF">
                <i class="bi bi-arrow-left-right"></i> Transferability
            </button>
            <button class="view-tab" data-view="COG">
                <i class="bi bi-lightbulb"></i> Cognitive
            </button>
            <button class="view-tab" data-view="CTX">
                <i class="bi bi-briefcase"></i> Work Context
            </button>
            <button class="view-tab" data-view="FUT">
                <i class="bi bi-robot"></i> Future Ready
            </button>
            <button class="view-tab" data-view="DIG">
                <i class="bi bi-laptop"></i> Digital
            </button>
            <button class="view-tab" data-view="IND">
                <i class="bi bi-building"></i> Industry
            </button>
            <button class="view-tab" data-view="filter">
                <i class="bi bi-funnel"></i> Multi-Filter
            </button>
            <button class="view-tab" data-view="table">
                <i class="bi bi-table"></i> Table
            </button>
        </div>
    </div>

    <div class="content-area">
        <!-- Overview Dashboard -->
        <div class="view-section active" id="overviewView"></div>
        
        <!-- Facet Views (generated dynamically) -->
        <div class="view-section facet-view-container" id="NATView"></div>
        <div class="view-section facet-view-container" id="TRFView"></div>
        <div class="view-section facet-view-container" id="COGView"></div>
        <div class="view-section facet-view-container" id="CTXView"></div>
        <div class="view-section facet-view-container" id="FUTView"></div>
        <div class="view-section facet-view-container" id="DIGView"></div>
        <div class="view-section facet-view-container" id="INDView"></div>
        
        <!-- Multi-Filter View -->
        <div class="view-section" id="filterView"></div>
        
        <!-- Table View -->
        <div class="view-section" id="tableView"></div>
    </div>
</div>
"""


JAVASCRIPT_CONTENT = """
let taxonomyData = null;
let skillsIndex = new Map();
let selectedSkillId = null;
let currentFacetView = null;
let currentFacetValue = null;

// Table state
let currentPage = 1;
const pageSize = 50;
let filteredData = [];

// Facet colors
const FACET_COLORS = {
    'NAT': '#e65100',
    'TRF': '#7b1fa2',
    'COG': '#1565c0',
    'CTX': '#2e7d32',
    'FUT': '#c2185b',
    'LRN': '#00695c',
    'DIG': '#512da8',
    'IND': '#ff8f00',
    'LVL': '#3f51b5'
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    try {
        if (typeof TAXONOMY_DATA !== 'undefined') {
            taxonomyData = TAXONOMY_DATA;
        } else if (typeof EMBEDDED_DATA !== 'undefined') {
            taxonomyData = EMBEDDED_DATA;
        } else {
            throw new Error('No taxonomy data found.');
        }
        
        // Build index
        taxonomyData.skills.forEach(skill => skillsIndex.set(skill.id, skill));
        filteredData = [...taxonomyData.skills];
        
        initializeStats();
        initializeOverview();
        initializeFacetViews();
        initializeFilterView();
        initializeTableView();
        initializeEventListeners();
        
        document.getElementById('loadingOverlay').style.display = 'none';
    } catch (error) {
        console.error('Failed to load taxonomy:', error);
        document.querySelector('.loading-text').textContent = 'Error: ' + error.message;
        document.querySelector('.loading-text').style.color = '#c62828';
    }
});

function initializeStats() {
    const stats = taxonomyData.metadata?.statistics || {};
    document.getElementById('totalSkills').textContent = (stats.total_skills || taxonomyData.skills.length).toLocaleString();
    document.getElementById('totalFacets').textContent = Object.keys(taxonomyData.facets || {}).length;
    document.getElementById('totalCodes').textContent = (stats.total_unique_codes || 0).toLocaleString();
    document.getElementById('totalAltTitles').textContent = (stats.total_alternative_titles || 0).toLocaleString();
    document.getElementById('totalKeywords').textContent = (stats.total_related_keywords || 0).toLocaleString();
}

function initializeOverview() {
    const container = document.getElementById('overviewView');
    const stats = taxonomyData.metadata?.statistics || {};
    
    let html = '<div class="overview-grid">';
    
    // Facet coverage cards
    if (stats.facet_coverage) {
        html += '<div class="overview-card"><h3><i class="bi bi-check-circle"></i> Facet Coverage</h3>';
        for (const [facetId, data] of Object.entries(stats.facet_coverage)) {
            const pct = (data.coverage * 100).toFixed(1);
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label">${data.name}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${pct}%; background: ${FACET_COLORS[facetId] || '#00838f'}"></div>
                    </div>
                    <span class="chart-bar-value">${pct}%</span>
                </div>
            `;
        }
        html += '</div>';
    }
    
    // Category distribution
    if (stats.category_distribution) {
        html += '<div class="overview-card"><h3><i class="bi bi-pie-chart"></i> Category Distribution</h3>';
        const total = Object.values(stats.category_distribution).reduce((a, b) => a + b, 0);
        for (const [cat, count] of Object.entries(stats.category_distribution)) {
            const pct = ((count / total) * 100).toFixed(1);
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label">${formatLabel(cat)}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${pct}%; background: #e65100"></div>
                    </div>
                    <span class="chart-bar-value">${count}</span>
                </div>
            `;
        }
        html += '</div>';
    }
    
    // Level distribution
    if (stats.level_distribution) {
        html += '<div class="overview-card"><h3><i class="bi bi-bar-chart-steps"></i> Level Distribution</h3>';
        const total = Object.values(stats.level_distribution).reduce((a, b) => a + b, 0);
        for (const [level, count] of Object.entries(stats.level_distribution).sort((a, b) => a[0] - b[0])) {
            const pct = ((count / total) * 100).toFixed(1);
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label">Level ${level}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${pct}%; background: #1565c0"></div>
                    </div>
                    <span class="chart-bar-value">${count}</span>
                </div>
            `;
        }
        html += '</div>';
    }
    
    // Top facet values for key facets
    const keyFacets = ['NAT', 'TRF', 'FUT'];
    for (const facetId of keyFacets) {
        if (stats.facet_distributions && stats.facet_distributions[facetId]) {
            const facetInfo = taxonomyData.facets[facetId];
            html += `<div class="overview-card"><h3><i class="bi bi-diagram-3"></i> ${facetInfo?.name || facetId}</h3>`;
            const total = Object.values(stats.facet_distributions[facetId]).reduce((a, b) => a + b, 0);
            for (const [code, count] of Object.entries(stats.facet_distributions[facetId]).slice(0, 6)) {
                const valueName = facetInfo?.values?.[code]?.name || code;
                const pct = ((count / total) * 100).toFixed(1);
                html += `
                    <div class="chart-bar">
                        <span class="chart-bar-label" title="${valueName}">${valueName}</span>
                        <div class="chart-bar-track">
                            <div class="chart-bar-fill" style="width: ${pct}%; background: ${FACET_COLORS[facetId] || '#00838f'}"></div>
                        </div>
                        <span class="chart-bar-value">${count}</span>
                    </div>
                `;
            }
            html += '</div>';
        }
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function initializeFacetViews() {
    const facetIds = ['NAT', 'TRF', 'COG', 'CTX', 'FUT', 'DIG', 'IND'];
    
    for (const facetId of facetIds) {
        const container = document.getElementById(`${facetId}View`);
        if (!container) continue;
        
        const facetInfo = taxonomyData.facets[facetId];
        if (!facetInfo) continue;
        
        // Count skills per facet value
        const valueCounts = {};
        for (const skill of taxonomyData.skills) {
            const facetData = skill.facets?.[facetId];
            if (facetData) {
                const code = facetData.code;
                if (Array.isArray(code)) {
                    code.forEach(c => { valueCounts[c] = (valueCounts[c] || 0) + 1; });
                } else {
                    valueCounts[code] = (valueCounts[code] || 0) + 1;
                }
            }
        }
        
        let html = `
            <div class="facet-view">
                <div class="facet-sidebar">
                    <div class="facet-search">
                        <input type="text" placeholder="Search skills..." id="${facetId}Search">
                    </div>
                    <div id="${facetId}Categories">
        `;
        
        // Create category cards
        for (const [code, valueInfo] of Object.entries(facetInfo.values)) {
            const count = valueCounts[code] || 0;
            html += `
                <div class="facet-category" data-facet="${facetId}" data-value="${code}">
                    <div class="facet-category-header">
                        <span class="facet-category-name">${valueInfo.name}</span>
                        <span class="facet-category-count">${count}</span>
                    </div>
                    <div class="facet-category-desc">${(valueInfo.description || '').substring(0, 80)}${valueInfo.description?.length > 80 ? '...' : ''}</div>
                </div>
            `;
        }
        
        html += `
                    </div>
                </div>
                <div class="facet-main">
                    <div id="${facetId}SkillsGrid" class="skills-grid">
                        <p style="color: var(--jsa-grey-500); padding: 20px;">Select a category to view skills</p>
                    </div>
                </div>
                <div class="facet-detail">
                    <div class="facet-detail-header">
                        <h3><i class="bi bi-info-circle"></i> Skill Details</h3>
                    </div>
                    <div id="${facetId}Detail" class="detail-placeholder">
                        <i class="bi bi-hand-index"></i>
                        <p>Select a skill to view details</p>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Add event listeners for category selection
        container.querySelectorAll('.facet-category').forEach(cat => {
            cat.addEventListener('click', () => {
                container.querySelectorAll('.facet-category').forEach(c => c.classList.remove('active'));
                cat.classList.add('active');
                loadFacetSkills(facetId, cat.dataset.value);
            });
        });
        
        // Add search listener
        document.getElementById(`${facetId}Search`)?.addEventListener('input', (e) => {
            searchFacetSkills(facetId, e.target.value);
        });
    }
}

function loadFacetSkills(facetId, valueCode) {
    currentFacetView = facetId;
    currentFacetValue = valueCode;
    
    const grid = document.getElementById(`${facetId}SkillsGrid`);
    if (!grid) return;
    
    // Filter skills by facet value
    let skills = taxonomyData.skills.filter(s => {
        const facetData = s.facets?.[facetId];
        if (!facetData) return false;
        const code = facetData.code;
        if (Array.isArray(code)) {
            return code.includes(valueCode);
        }
        return code === valueCode;
    });
    
    // Sort by confidence descending
    skills.sort((a, b) => {
        const confA = a.facets?.[facetId]?.confidence || 0;
        const confB = b.facets?.[facetId]?.confidence || 0;
        return confB - confA;
    });
    
    if (skills.length === 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">No skills found</p>';
        return;
    }
    
    // Render ALL skill cards - page scrolls instead of pane
    let html = '';
    
    for (const skill of skills) {
        html += createSkillMiniCard(skill, facetId);
    }
    
    grid.innerHTML = html;
    
    // Add click handlers
    grid.querySelectorAll('.skill-card-mini').forEach(card => {
        card.addEventListener('click', () => {
            grid.querySelectorAll('.skill-card-mini').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showSkillDetail(facetId, card.dataset.skillId);
        });
    });
}

function searchFacetSkills(facetId, query) {
    const grid = document.getElementById(`${facetId}SkillsGrid`);
    if (!grid || !query || query.length < 2) {
        if (currentFacetValue) {
            loadFacetSkills(facetId, currentFacetValue);
        }
        return;
    }
    
    const searchLower = query.toLowerCase();
    const skills = taxonomyData.skills.filter(s => 
        s.name?.toLowerCase().includes(searchLower) ||
        s.id?.toLowerCase().includes(searchLower) ||
        (s.all_related_codes || []).some(c => c.toLowerCase().includes(searchLower))
    ).slice(0, 50);
    
    let html = '';
    for (const skill of skills) {
        html += createSkillMiniCard(skill, facetId);
    }
    
    grid.innerHTML = html || '<p style="color: var(--jsa-grey-500); padding: 20px;">No results found</p>';
    
    // Add click handlers
    grid.querySelectorAll('.skill-card-mini').forEach(card => {
        card.addEventListener('click', () => {
            grid.querySelectorAll('.skill-card-mini').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showSkillDetail(facetId, card.dataset.skillId);
        });
    });
}

function createSkillMiniCard(skill, facetId) {
    return `
        <div class="skill-card-mini" data-skill-id="${skill.id}">
            <div class="skill-card-mini-name">${skill.name}</div>
        </div>
    `;
}

function showSkillDetail(facetId, skillId) {
    const skill = skillsIndex.get(skillId);
    if (!skill) return;
    
    const detailContainer = document.getElementById(`${facetId}Detail`);
    if (!detailContainer) return;
    
    // Remove placeholder styling when showing skill details
    detailContainer.classList.remove('detail-placeholder');
    
    selectedSkillId = skillId;
    
    // Facet name mapping
    const facetNames = {
        'NAT': 'Skill Nature',
        'TRF': 'Transferability',
        'COG': 'Cognitive Complexity',
        'CTX': 'Work Context',
        'FUT': 'Future Readiness',
        'LRN': 'Learning Context',
        'DIG': 'Digital Intensity',
        'IND': 'Industry Domain',
        'LVL': 'Proficiency Level'
    };
    
    let html = `
        <div class="skill-detail-card">
            <div class="skill-detail-header">
                <div class="skill-detail-name">
                    <i class="bi bi-mortarboard-fill"></i>
                    ${skill.name}
                </div>
                <span class="skill-detail-id">${skill.id}</span>
            </div>
            
            ${skill.description ? `<div class="skill-detail-desc">${skill.description}</div>` : ''}
    `;
    
    // Dimensions section - vertical list
    html += `
        <div class="detail-section">
            <div class="detail-section-title"><i class="bi bi-tags"></i> Dimensions</div>
            <div class="dimensions-list">
    `;
    
    // Show all facets as vertical list
    for (const [fId, fData] of Object.entries(skill.facets || {})) {
        if (fData && fData.name) {
            const facetDisplayName = facetNames[fId] || fId;
            const confidenceHtml = fData.confidence ? `<span class="facet-confidence">${(fData.confidence * 100).toFixed(0)}%</span>` : '';
            html += `
                <div class="dimension-row">
                    <span class="dimension-label">${facetDisplayName}</span>
                    <div class="dimension-value">
                        <span class="facet-badge ${fId}">${fData.name}</span>
                        ${confidenceHtml}
                    </div>
                </div>
            `;
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    // Alternative titles
    if (skill.alternative_titles?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-card-heading"></i> Alternative Titles (${skill.alternative_titles.length})</div>
                <div class="tag-list">
                    ${skill.alternative_titles.slice(0, 10).map(t => `<span class="tag tag-alt">${t}</span>`).join('')}
                    ${skill.alternative_titles.length > 10 ? `<span class="tag tag-more">+${skill.alternative_titles.length - 10} more</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // Related codes
    if (skill.all_related_codes?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-upc-scan"></i> Related Codes (${skill.all_related_codes.length})</div>
                <div class="tag-list">
                    ${skill.all_related_codes.slice(0, 12).map(c => `<span class="tag tag-code">${c}</span>`).join('')}
                    ${skill.all_related_codes.length > 12 ? `<span class="tag tag-more">+${skill.all_related_codes.length - 12} more</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // Keywords
    if (skill.all_related_kw?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-key"></i> Related Keywords (${skill.all_related_kw.length})</div>
                <div class="tag-list">
                    ${skill.all_related_kw.slice(0, 15).map(k => `<span class="tag tag-keyword">${k}</span>`).join('')}
                    ${skill.all_related_kw.length > 15 ? `<span class="tag tag-more">+${skill.all_related_kw.length - 15} more</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // Related skills
    if (skill.related_skills?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-link-45deg"></i> Related Skills (${skill.related_skills.length})</div>
                <div class="related-skills-list">
                    ${skill.related_skills.slice(0, 10).map(r => `
                        <div class="related-skill-item" onclick="navigateToSkill('${facetId}', '${r.skill_id}')">
                            <span class="related-skill-name">${r.skill_name}</span>
                            <span class="related-skill-score">${(r.similarity * 100).toFixed(0)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    detailContainer.innerHTML = html;
}

function navigateToSkill(currentFacetId, skillId) {
    const skill = skillsIndex.get(skillId);
    if (skill) {
        showSkillDetail(currentFacetId, skillId);
        // Also highlight in grid if visible
        const grid = document.getElementById(`${currentFacetId}SkillsGrid`);
        if (grid) {
            grid.querySelectorAll('.skill-card-mini').forEach(c => {
                c.classList.remove('selected');
                if (c.dataset.skillId === skillId) {
                    c.classList.add('selected');
                    c.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        }
    }
}

// Multi-Filter View
let activeFilters = {};

function initializeFilterView() {
    const container = document.getElementById('filterView');
    
    // Build dropdown options for each facet
    let filtersHtml = '';
    const facetIcons = {
        'NAT': 'bi-bookmark',
        'TRF': 'bi-arrow-left-right',
        'COG': 'bi-lightbulb',
        'CTX': 'bi-briefcase',
        'FUT': 'bi-robot',
        'LRN': 'bi-book',
        'DIG': 'bi-laptop',
        'IND': 'bi-building',
        'LVL': 'bi-layers'
    };
    
    for (const [facetId, facetInfo] of Object.entries(taxonomyData.facets || {})) {
        const icon = facetIcons[facetId] || 'bi-tag';
        const options = Object.entries(facetInfo.values || {})
            .map(([code, valueInfo]) => `<option value="${code}">${valueInfo.name}</option>`)
            .join('');
        
        filtersHtml += `
            <div class="filter-section">
                <div class="filter-section-title">
                    <i class="bi ${icon}"></i> ${facetInfo.name}
                </div>
                <select class="filter-select" id="filter_${facetId}" data-facet="${facetId}">
                    <option value="">All</option>
                    ${options}
                </select>
            </div>
        `;
    }
    
    container.innerHTML = `
        <div class="filter-view">
            <div class="filter-sidebar">
                <h3 style="margin-bottom: 16px; font-size: 1rem; color: var(--jsa-navy);">
                    <i class="bi bi-funnel"></i> Filter by Dimensions
                </h3>
                ${filtersHtml}
                <div class="filter-actions">
                    <button class="filter-btn filter-btn-apply" onclick="applyMultiFilters()">
                        <i class="bi bi-check-lg"></i> Apply
                    </button>
                    <button class="filter-btn filter-btn-clear" onclick="clearMultiFilters()">
                        <i class="bi bi-x-lg"></i> Clear
                    </button>
                </div>
            </div>
            <div class="filter-main">
                <div class="filter-results-header">
                    <div class="filter-results-count">
                        Showing <strong id="filterResultsCount">0</strong> skills
                    </div>
                    <div class="active-filters" id="activeFilterTags"></div>
                </div>
                <div id="filterSkillsGrid" class="skills-grid">
                    <p style="color: var(--jsa-grey-500); padding: 20px;">Select filters and click Apply to view skills</p>
                </div>
            </div>
            <div class="filter-detail">
                <div class="facet-detail-header">
                    <h3><i class="bi bi-info-circle"></i> Skill Details</h3>
                </div>
                <div id="filterDetail" class="detail-placeholder">
                    <i class="bi bi-hand-index"></i>
                    <p>Select a skill to view details</p>
                </div>
            </div>
        </div>
    `;
    
    // Add event listeners for dropdowns
    container.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', updateActiveFilterTags);
    });
}

function updateActiveFilterTags() {
    const tagsContainer = document.getElementById('activeFilterTags');
    let tagsHtml = '';
    
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            const facetId = select.dataset.facet;
            const facetName = taxonomyData.facets[facetId]?.name || facetId;
            const valueName = select.options[select.selectedIndex].text;
            tagsHtml += `
                <span class="active-filter-tag">
                    ${facetName}: ${valueName}
                    <i class="bi bi-x" onclick="clearSingleFilter('${facetId}')"></i>
                </span>
            `;
        }
    });
    
    tagsContainer.innerHTML = tagsHtml;
}

function clearSingleFilter(facetId) {
    const select = document.getElementById(`filter_${facetId}`);
    if (select) {
        select.value = '';
        updateActiveFilterTags();
        applyMultiFilters();
    }
}

function applyMultiFilters() {
    activeFilters = {};
    
    // Collect all filter values
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            activeFilters[select.dataset.facet] = select.value;
        }
    });
    
    // Filter skills
    let filtered = taxonomyData.skills.filter(skill => {
        for (const [facetId, value] of Object.entries(activeFilters)) {
            const skillFacet = skill.facets?.[facetId];
            if (!skillFacet || skillFacet.code !== value) {
                return false;
            }
        }
        return true;
    });
    
    // Sort by average confidence of selected facets (descending)
    if (Object.keys(activeFilters).length > 0) {
        filtered.sort((a, b) => {
            let confA = 0, confB = 0;
            let countA = 0, countB = 0;
            
            for (const facetId of Object.keys(activeFilters)) {
                if (a.facets?.[facetId]?.confidence) {
                    confA += a.facets[facetId].confidence;
                    countA++;
                }
                if (b.facets?.[facetId]?.confidence) {
                    confB += b.facets[facetId].confidence;
                    countB++;
                }
            }
            
            const avgA = countA > 0 ? confA / countA : 0;
            const avgB = countB > 0 ? confB / countB : 0;
            return avgB - avgA;  // Descending
        });
    }
    
    // Render results
    const grid = document.getElementById('filterSkillsGrid');
    const countEl = document.getElementById('filterResultsCount');
    
    countEl.textContent = filtered.length.toLocaleString();
    
    if (filtered.length === 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">No skills match the selected filters</p>';
        return;
    }
    
    let html = '';
    for (const skill of filtered) {
        // Calculate average confidence for display
        let totalConf = 0, confCount = 0;
        for (const facetId of Object.keys(activeFilters)) {
            if (skill.facets?.[facetId]?.confidence) {
                totalConf += skill.facets[facetId].confidence;
                confCount++;
            }
        }
        const avgConf = confCount > 0 ? (totalConf / confCount * 100).toFixed(0) : null;
        
        html += `
            <div class="skill-card-mini" data-skill-id="${skill.id}">
                <div class="skill-card-mini-name">${skill.name}</div>
                ${avgConf ? `<div class="skill-card-mini-meta"><span class="skill-mini-badge level">${avgConf}% conf</span></div>` : ''}
            </div>
        `;
    }
    
    grid.innerHTML = html;
    
    // Add click handlers
    grid.querySelectorAll('.skill-card-mini').forEach(card => {
        card.addEventListener('click', () => {
            grid.querySelectorAll('.skill-card-mini').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showFilterSkillDetail(card.dataset.skillId);
        });
    });
}

function showFilterSkillDetail(skillId) {
    const skill = skillsIndex.get(skillId);
    if (!skill) return;
    
    const detailContainer = document.getElementById('filterDetail');
    if (!detailContainer) return;
    
    detailContainer.classList.remove('detail-placeholder');
    
    // Facet name mapping
    const facetNames = {
        'NAT': 'Skill Nature',
        'TRF': 'Transferability',
        'COG': 'Cognitive Complexity',
        'CTX': 'Work Context',
        'FUT': 'Future Readiness',
        'LRN': 'Learning Context',
        'DIG': 'Digital Intensity',
        'IND': 'Industry Domain',
        'LVL': 'Proficiency Level'
    };
    
    let html = `
        <div class="skill-detail-card">
            <div class="skill-detail-header">
                <div class="skill-detail-name">
                    <i class="bi bi-mortarboard-fill"></i>
                    ${skill.name}
                </div>
                <span class="skill-detail-id">${skill.id}</span>
            </div>
            
            ${skill.description ? `<div class="skill-detail-desc">${skill.description}</div>` : ''}
    `;
    
    // Dimensions section
    html += `
        <div class="detail-section">
            <div class="detail-section-title"><i class="bi bi-tags"></i> Dimensions</div>
            <div class="dimensions-list">
    `;
    
    for (const [fId, fData] of Object.entries(skill.facets || {})) {
        if (fData && fData.name) {
            const facetDisplayName = facetNames[fId] || fId;
            const confidenceHtml = fData.confidence ? `<span class="facet-confidence">${(fData.confidence * 100).toFixed(0)}%</span>` : '';
            const isActive = activeFilters[fId] ? 'style="background: rgba(0, 131, 143, 0.1);"' : '';
            html += `
                <div class="dimension-row" ${isActive}>
                    <span class="dimension-label">${facetDisplayName}</span>
                    <div class="dimension-value">
                        <span class="facet-badge ${fId}">${fData.name}</span>
                        ${confidenceHtml}
                    </div>
                </div>
            `;
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    // Alternative titles
    if (skill.alternative_titles?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-card-heading"></i> Alternative Titles (${skill.alternative_titles.length})</div>
                <div class="tag-list">
                    ${skill.alternative_titles.slice(0, 10).map(t => `<span class="tag tag-alt">${t}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    detailContainer.innerHTML = html;
}

function clearMultiFilters() {
    document.querySelectorAll('.filter-select').forEach(select => {
        select.value = '';
    });
    activeFilters = {};
    updateActiveFilterTags();
    
    const grid = document.getElementById('filterSkillsGrid');
    const countEl = document.getElementById('filterResultsCount');
    
    countEl.textContent = '0';
    grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">Select filters and click Apply to view skills</p>';
    
    const detailContainer = document.getElementById('filterDetail');
    detailContainer.classList.add('detail-placeholder');
    detailContainer.innerHTML = `
        <i class="bi bi-hand-index"></i>
        <p>Select a skill to view details</p>
    `;
}

function initializeTableView() {
    const container = document.getElementById('tableView');
    
    // Build filter options
    const facetOptions = Object.entries(taxonomyData.facets || {}).map(([id, info]) => 
        `<option value="${id}">${info.name}</option>`
    ).join('');
    
    container.innerHTML = `
        <div class="table-controls">
            <div class="export-buttons">
                <button class="btn-custom btn-primary" onclick="exportToExcel()">
                    <i class="bi bi-file-earmark-excel"></i> Export Excel
                </button>
                <button class="btn-custom btn-outline" onclick="exportToCSV()">
                    <i class="bi bi-file-earmark-spreadsheet"></i> CSV
                </button>
            </div>
            <div class="filter-group">
                <input type="text" id="tableSearch" placeholder="Search skills...">
                <select id="filterFacet">
                    <option value="">Filter by Facet</option>
                    ${facetOptions}
                </select>
                <select id="filterFacetValue" disabled>
                    <option value="">Select value</option>
                </select>
            </div>
        </div>
        <div class="table-wrapper">
            <table class="skills-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Skill Name</th>
                        <th>Category</th>
                        <th>Level</th>
                        <th>Nature</th>
                        <th>Transferability</th>
                        <th>Cognitive</th>
                        <th>Future</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
        <div class="table-pagination" id="tablePagination"></div>
    `;
    
    renderTable();
    
    // Event listeners
    document.getElementById('tableSearch')?.addEventListener('input', applyTableFilters);
    document.getElementById('filterFacet')?.addEventListener('change', onFacetFilterChange);
    document.getElementById('filterFacetValue')?.addEventListener('change', applyTableFilters);
}

function onFacetFilterChange() {
    const facetId = document.getElementById('filterFacet').value;
    const valueSelect = document.getElementById('filterFacetValue');
    
    if (!facetId) {
        valueSelect.disabled = true;
        valueSelect.innerHTML = '<option value="">Select value</option>';
        applyTableFilters();
        return;
    }
    
    const facetInfo = taxonomyData.facets[facetId];
    if (!facetInfo) return;
    
    let options = '<option value="">All Values</option>';
    for (const [code, valInfo] of Object.entries(facetInfo.values)) {
        options += `<option value="${code}">${valInfo.name}</option>`;
    }
    
    valueSelect.innerHTML = options;
    valueSelect.disabled = false;
    applyTableFilters();
}

function applyTableFilters() {
    const search = document.getElementById('tableSearch')?.value?.toLowerCase() || '';
    const facetId = document.getElementById('filterFacet')?.value || '';
    const facetValue = document.getElementById('filterFacetValue')?.value || '';
    
    filteredData = taxonomyData.skills.filter(s => {
        // Search filter
        if (search && !s.name?.toLowerCase().includes(search) && !s.id?.toLowerCase().includes(search)) {
            return false;
        }
        
        // Facet filter
        if (facetId && facetValue) {
            const facetData = s.facets?.[facetId];
            if (!facetData) return false;
            const code = facetData.code;
            if (Array.isArray(code)) {
                if (!code.includes(facetValue)) return false;
            } else if (code !== facetValue) {
                return false;
            }
        }
        
        return true;
    });
    
    currentPage = 1;
    renderTable();
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = filteredData.slice(start, end);
    
    tbody.innerHTML = pageData.map(s => `
        <tr>
            <td style="font-family: monospace; font-size: 0.8rem;">${s.id || '-'}</td>
            <td title="${s.name}">${s.name}</td>
            <td>${formatLabel(s.category) || '-'}</td>
            <td>${s.level || '-'}</td>
            <td>${s.facets?.NAT?.name || '-'}</td>
            <td>${s.facets?.TRF?.name || '-'}</td>
            <td>${s.facets?.COG?.name || '-'}</td>
            <td>${s.facets?.FUT?.name || '-'}</td>
        </tr>
    `).join('');
    
    renderPagination();
}

function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / pageSize);
    const pag = document.getElementById('tablePagination');
    if (!pag) return;
    
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

function initializeEventListeners() {
    // Tab switching
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const view = tab.dataset.view;
            document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            
            if (view === 'overview') {
                document.getElementById('overviewView').classList.add('active');
            } else if (view === 'table') {
                document.getElementById('tableView').classList.add('active');
            } else {
                document.getElementById(`${view}View`)?.classList.add('active');
            }
        });
    });
}

function formatLabel(str) {
    if (!str) return '';
    return str.toString().replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}

// Export functions
function exportToExcel() {
    const exportData = taxonomyData.skills.map(s => ({
        'Skill ID': s.id || '',
        'Skill Name': s.name || '',
        'Description': s.description || '',
        'Category': s.category || '',
        'Level': s.level || '',
        'Context': s.context || '',
        'Confidence': s.confidence ? (s.confidence * 100).toFixed(1) + '%' : '',
        'Skill Nature': s.facets?.NAT?.name || '',
        'Transferability': s.facets?.TRF?.name || '',
        'Cognitive Complexity': s.facets?.COG?.name || '',
        'Work Context': s.facets?.CTX?.name || '',
        'Future Readiness': s.facets?.FUT?.name || '',
        'Learning Context': s.facets?.LRN?.name || '',
        'Digital Intensity': s.facets?.DIG?.name || '',
        'Industry Domains': s.facets?.IND?.name || '',
        'Proficiency Level': s.facets?.LVL?.name || '',
        'Primary Code': s.code || '',
        'Alternative Titles': (s.alternative_titles || []).join('; '),
        'All Related Codes': (s.all_related_codes || []).join('; '),
        'All Related Keywords': (s.all_related_kw || []).join('; ')
    }));
    
    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Faceted Skills');
    XLSX.writeFile(wb, 'vet_skills_faceted_taxonomy.xlsx');
}

function exportToCSV() {
    const headers = ['ID', 'Name', 'Category', 'Level', 'Nature', 'Transferability', 'Cognitive', 'Future', 'Code'];
    const rows = taxonomyData.skills.map(s => [
        s.id, s.name, s.category || '', s.level || '',
        s.facets?.NAT?.name || '', s.facets?.TRF?.name || '',
        s.facets?.COG?.name || '', s.facets?.FUT?.name || '', s.code || ''
    ].map(v => `"${String(v || '').replace(/"/g, '""')}"`).join(','));
    
    const csv = [headers.join(','), ...rows].join('\\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vet_skills_faceted_taxonomy.csv';
    a.click();
    URL.revokeObjectURL(url);
}
"""


HTML_TEMPLATE_EXTERNAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VET Skills Faceted Explorer | Jobs and Skills Australia</title>
    
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
    
    <script src="{DATA_FILE}"></script>

    <script>
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
    <title>VET Skills Faceted Explorer | Jobs and Skills Australia</title>
    
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
        const EMBEDDED_DATA = {TAXONOMY_DATA};
        
        {JAVASCRIPT_CONTENT}
    </script>
</body>
</html>
"""


def count_skills(data):
    """Count total skills"""
    return len(data.get('skills', []))


def generate_faceted_html(taxonomy_json_path: str, output_html_path: str):
    """Generate faceted HTML visualization"""
    
    print(f"Loading faceted taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)
    
    total_skills = count_skills(taxonomy_data)
    print(f"Taxonomy loaded: {total_skills} skills")
    
    if total_skills > EXTERNAL_DATA_THRESHOLD:
        print(f"Large dataset ({total_skills} skills). Using external data file.")
        
        data_file = output_html_path.replace('.html', '_data.js')
        data_file_name = Path(data_file).name
        
        with open(data_file, 'w') as f:
            f.write('// VET Skills Faceted Taxonomy Data\\n')
            f.write('const TAXONOMY_DATA = ')
            json.dump(taxonomy_data, f, separators=(',', ':'))
            f.write(';\\n')
        
        print(f"Data saved to: {data_file}")
        
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
    
    print("\\n" + "=" * 60)
    print("✓ Faceted HTML visualization generated successfully!")
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python generate_faceted_visualization.py <taxonomy.json> <output.html>")
        sys.exit(1)
    
    taxonomy_path = sys.argv[1]
    html_output_path = sys.argv[2]
    
    if not Path(taxonomy_path).exists():
        print(f"Error: Taxonomy file not found: {taxonomy_path}")
        sys.exit(1)
    
    generate_faceted_html(taxonomy_path, html_output_path)
