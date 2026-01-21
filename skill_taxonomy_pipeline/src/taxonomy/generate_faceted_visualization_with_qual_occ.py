"""
Generate Interactive Multi-View HTML Visualization for Faceted Taxonomy
WITH Qualifications and Occupations

This script creates a performant HTML visualization with multiple tabs/views
for exploring skills across different facet dimensions, including
qualifications and ANZSCO occupations.

Additional Views:
- Qualifications View
- Occupations (ANZSCO) View

Usage:
    python generate_faceted_visualization_with_qual_occ.py faceted_taxonomy.json output.html
"""

import json
import sys
from pathlib import Path
import pandas as pd

# Threshold for external data loading
EXTERNAL_DATA_THRESHOLD = 0  # Always use external data file for better lazy loading


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
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
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
.stat-label { font-size: 0.65rem; color: var(--jsa-grey-500); text-transform: uppercase; letter-spacing: 0.5px; }

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
    padding: 12px 14px;
    cursor: pointer;
    border: none;
    background: transparent;
    font-size: 0.8rem;
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
    max-height: 600px;
    overflow-y: auto;
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

.facet-category-name { font-weight: 600; color: var(--jsa-navy); font-size: 0.85rem; }
.facet-category-count { 
    background: var(--jsa-teal); 
    color: white; 
    padding: 2px 8px; 
    border-radius: 12px; 
    font-size: 0.75rem; 
    font-weight: 600;
}

.facet-category-desc { font-size: 0.75rem; color: var(--jsa-grey-600); }

/* ASCED Badge styling */
.asced-code, .qual-code, .occ-code {
    display: inline-block;
    font-family: monospace;
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 4px;
    margin-right: 6px;
}

.asced-code { background: #e3f2fd; color: #1565c0; }
.qual-code { background: #e8f5e9; color: #2e7d32; }
.occ-code { background: #fff3e0; color: #e65100; }

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
.facet-badge.ASCED { background: #fff8e1; color: #ff8f00; }
.facet-badge.IND { background: #fff8e1; color: #ff8f00; }
.facet-badge.LVL { background: #e8eaf6; color: #3f51b5; }
.facet-badge.QUAL { background: #e8f5e9; color: #2e7d32; }
.facet-badge.OCC { background: #fff3e0; color: #e65100; }

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
.tag-code.tag-primary { background: #c5cae9; color: #1a237e; font-weight: 600; }
.tag-keyword { background: #e0f7fa; color: #00838f; }

/* Primary code with code name display */
.primary-code-display {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.code-name-label {
    font-size: 0.85rem;
    color: var(--jsa-grey-700);
    padding: 4px 8px;
    background: var(--jsa-grey-100);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--jsa-teal);
}
.tag-qual { background: #e8f5e9; color: #2e7d32; }
.tag-occ { background: #fff3e0; color: #e65100; }
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

/* Qualification/Occupation items */
.qual-occ-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    background: var(--jsa-grey-100);
    border-radius: var(--radius-sm);
    margin-bottom: 4px;
}

.qual-occ-item-code {
    font-family: monospace;
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 4px;
    margin-right: 8px;
}

.qual-occ-item-title {
    font-size: 0.8rem;
    color: var(--jsa-grey-700);
    flex: 1;
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
    width: 140px;
    font-size: 0.75rem;
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
    max-height: 600px;
    overflow-y: auto;
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

.filter-btn-clear {
    background: var(--jsa-white);
    color: var(--jsa-grey-600);
    border: 2px solid var(--jsa-grey-300);
    width: 100%;
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

/* Filter option count badge */
.filter-option-count {
    color: var(--jsa-grey-500);
    font-size: 0.85em;
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
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.skills-table td {
    padding: 8px;
    border-bottom: 1px solid var(--jsa-grey-200);
    max-width: 150px;
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
                <p>Multi-dimensional taxonomy with qualifications and ANZSCO occupations</p>
            </div>
        </div>
    </div>
</div>

<div class="stats-dashboard">
    <div class="stat-card">
        <i class="bi bi-mortarboard-fill"></i>
        <div class="stat-value" id="totalSkills">-</div>
        <div class="stat-label">Skills</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-grid-3x3-gap"></i>
        <div class="stat-value" id="totalFacets">-</div>
        <div class="stat-label">Facets</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-award"></i>
        <div class="stat-value" id="totalQualifications">-</div>
        <div class="stat-label">Qualifications</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-briefcase"></i>
        <div class="stat-value" id="totalOccupations">-</div>
        <div class="stat-label">Occupations</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-upc-scan"></i>
        <div class="stat-value" id="totalCodes">-</div>
        <div class="stat-label">Unit Codes</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-tag"></i>
        <div class="stat-value" id="totalCodeNames">-</div>
        <div class="stat-label">Code Names</div>
    </div>
    <div class="stat-card">
        <i class="bi bi-card-heading"></i>
        <div class="stat-value" id="totalAltTitles">-</div>
        <div class="stat-label">Alt. Titles</div>
    </div>
</div>

<div class="main-container">
    <div class="view-tabs-container">
        <div class="view-tabs">
            <button class="view-tab active" data-view="overview">
                <i class="bi bi-speedometer2"></i> Overview
            </button>
            <button class="view-tab" data-view="NAT">
                <i class="bi bi-bookmark"></i> Nature
            </button>
            <button class="view-tab" data-view="TRF">
                <i class="bi bi-arrow-left-right"></i> Transfer
            </button>
            <button class="view-tab" data-view="COG">
                <i class="bi bi-lightbulb"></i> Cognitive
            </button>
            <button class="view-tab" data-view="CTX">
                <i class="bi bi-briefcase"></i> Context
            </button>
            <button class="view-tab" data-view="FUT">
                <i class="bi bi-robot"></i> Future
            </button>
            <button class="view-tab" data-view="DIG">
                <i class="bi bi-laptop"></i> Digital
            </button>
            <button class="view-tab" data-view="ASCED">
                <i class="bi bi-mortarboard"></i> ASCED
            </button>
            <button class="view-tab" data-view="QUAL">
                <i class="bi bi-award"></i> Qualifications
            </button>
            <button class="view-tab" data-view="OCC">
                <i class="bi bi-person-badge"></i> Occupations
            </button>
            <button class="view-tab" data-view="filter">
                <i class="bi bi-funnel"></i> Filter
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
        <div class="view-section facet-view-container" id="ASCEDView"></div>
        <div class="view-section facet-view-container" id="QUALView"></div>
        <div class="view-section facet-view-container" id="OCCView"></div>
        
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

// Qualification/Occupation lookup
let qualificationSkillsMap = {};  // qual_code -> [skill_ids]
let occupationSkillsMap = {};     // occ_code -> [skill_ids]

// Facet colors
const FACET_COLORS = {
    'NAT': '#e65100',
    'TRF': '#7b1fa2',
    'COG': '#1565c0',
    'CTX': '#2e7d32',
    'FUT': '#c2185b',
    'LRN': '#00695c',
    'DIG': '#512da8',
    'ASCED': '#ff8f00',
    'IND': '#ff8f00',
    'LVL': '#3f51b5',
    'QUAL': '#2e7d32',
    'OCC': '#e65100'
};

// Facet display names
const FACET_DISPLAY_NAMES = {
    'NAT': 'Skill Nature',
    'TRF': 'Transferability',
    'COG': 'Cognitive Complexity',
    'CTX': 'Work Context',
    'FUT': 'Future Readiness',
    'LRN': 'Learning Context',
    'DIG': 'Digital Intensity',
    'ASCED': 'ASCED Field of Education',
    'IND': 'ASCED Field of Education',
    'LVL': 'Proficiency Level',
    'QUAL': 'Qualifications',
    'OCC': 'Occupations (ANZSCO)'
};

// Store original facet counts for filter view
let originalFacetCounts = {};

// Initialize - wait for data to be available
function initializeTaxonomy() {
    try {
        if (typeof TAXONOMY_DATA !== 'undefined') {
            taxonomyData = TAXONOMY_DATA;
        } else if (typeof EMBEDDED_DATA !== 'undefined') {
            taxonomyData = EMBEDDED_DATA;
        } else {
            throw new Error('No taxonomy data found.');
        }
        
        if (!taxonomyData.skills || taxonomyData.skills.length === 0) {
            throw new Error('Taxonomy data is empty or invalid.');
        }
        
        // Build index
        taxonomyData.skills.forEach(skill => skillsIndex.set(skill.id, skill));
        filteredData = [...taxonomyData.skills];
        
        // Normalize facet names
        normalizeFacetData();
        
        // Build qualification/occupation lookup maps
        buildQualOccMaps();
        
        // Build original facet counts
        buildOriginalFacetCounts();
        
        initializeStats();
        initializeOverview();
        initializeFacetViews();
        initializeQualOccViews();
        initializeFilterView();
        initializeTableView();
        initializeEventListeners();
        
        document.getElementById('loadingOverlay').style.display = 'none';
    } catch (error) {
        console.error('Failed to load taxonomy:', error);
        document.querySelector('.loading-text').textContent = 'Error: ' + error.message;
        document.querySelector('.loading-text').style.color = '#c62828';
    }
}

function normalizeFacetData() {
    // If we have IND facet but not ASCED, copy IND to ASCED
    if (taxonomyData.facets && taxonomyData.facets.IND && !taxonomyData.facets.ASCED) {
        taxonomyData.facets.ASCED = {
            ...taxonomyData.facets.IND,
            name: 'ASCED Field of Education'
        };
    }
    
    taxonomyData.skills.forEach(skill => {
        if (skill.facets) {
            if (skill.facets.IND && !skill.facets.ASCED) {
                skill.facets.ASCED = {...skill.facets.IND};
            }
            if (skill.facets.ASCED && !skill.facets.IND) {
                skill.facets.IND = {...skill.facets.ASCED};
            }
        }
    });
}

function buildQualOccMaps() {
    qualificationSkillsMap = {};
    occupationSkillsMap = {};
    
    taxonomyData.skills.forEach(skill => {
        // Build qualification map
        (skill.qualifications || []).forEach(qual => {
            if (!qualificationSkillsMap[qual.code]) {
                qualificationSkillsMap[qual.code] = [];
            }
            qualificationSkillsMap[qual.code].push(skill.id);
        });
        
        // Build occupation map
        (skill.occupations || []).forEach(occ => {
            if (!occupationSkillsMap[occ.code]) {
                occupationSkillsMap[occ.code] = [];
            }
            occupationSkillsMap[occ.code].push(skill.id);
        });
    });
}

function buildOriginalFacetCounts() {
    originalFacetCounts = {};
    
    // Count for standard facets
    for (const facetId of Object.keys(taxonomyData.facets || {})) {
        if (facetId === 'QUAL' || facetId === 'OCC') continue;
        
        originalFacetCounts[facetId] = {};
        const skillFacetKey = facetId === 'ASCED' ? (taxonomyData.skills[0]?.facets?.ASCED ? 'ASCED' : 'IND') : facetId;
        
        for (const skill of taxonomyData.skills) {
            const facetData = skill.facets?.[skillFacetKey];
            if (facetData) {
                const code = facetData.code;
                if (Array.isArray(code)) {
                    code.forEach(c => { originalFacetCounts[facetId][c] = (originalFacetCounts[facetId][c] || 0) + 1; });
                } else {
                    originalFacetCounts[facetId][code] = (originalFacetCounts[facetId][code] || 0) + 1;
                }
            }
        }
    }
    
    // Count for QUAL
    originalFacetCounts['QUAL'] = {};
    for (const [code, skillIds] of Object.entries(qualificationSkillsMap)) {
        originalFacetCounts['QUAL'][code] = skillIds.length;
    }
    
    // Count for OCC
    originalFacetCounts['OCC'] = {};
    for (const [code, skillIds] of Object.entries(occupationSkillsMap)) {
        originalFacetCounts['OCC'][code] = skillIds.length;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof TAXONOMY_DATA !== 'undefined' || typeof EMBEDDED_DATA !== 'undefined') {
        initializeTaxonomy();
    } else {
        let attempts = 0;
        const maxAttempts = 50;
        const checkInterval = setInterval(function() {
            attempts++;
            if (typeof TAXONOMY_DATA !== 'undefined' || typeof EMBEDDED_DATA !== 'undefined') {
                clearInterval(checkInterval);
                initializeTaxonomy();
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                document.querySelector('.loading-text').textContent = 'Error: Failed to load data file.';
                document.querySelector('.loading-text').style.color = '#c62828';
            }
        }, 100);
    }
});

function initializeStats() {
    const stats = taxonomyData.metadata?.statistics || {};
    document.getElementById('totalSkills').textContent = (stats.total_skills || taxonomyData.skills.length).toLocaleString();
    document.getElementById('totalFacets').textContent = Object.keys(taxonomyData.facets || {}).length;
    document.getElementById('totalCodes').textContent = (stats.total_unique_codes || 0).toLocaleString();
    document.getElementById('totalAltTitles').textContent = (stats.total_alternative_titles || 0).toLocaleString();
    document.getElementById('totalQualifications').textContent = (stats.total_qualifications || Object.keys(qualificationSkillsMap).length).toLocaleString();
    document.getElementById('totalOccupations').textContent = (stats.total_occupations || Object.keys(occupationSkillsMap).length).toLocaleString();
    
    // Count skills with code names
    const skillsWithCodeNames = stats.skills_with_code_names || taxonomyData.skills.filter(s => s.code_name && s.code_name.trim() !== '').length;
    document.getElementById('totalCodeNames').textContent = skillsWithCodeNames.toLocaleString();
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
            const displayName = FACET_DISPLAY_NAMES[facetId] || data.name || facetId;
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label">${displayName}</span>
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
    
    // Top Qualifications
    const qualCounts = Object.entries(qualificationSkillsMap)
        .map(([code, skills]) => ({code, title: taxonomyData.facets?.QUAL?.values?.[code]?.name || code, count: skills.length}))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8);
    
    if (qualCounts.length > 0) {
        const maxQual = qualCounts[0].count;
        html += '<div class="overview-card"><h3><i class="bi bi-award"></i> Top Qualifications</h3>';
        for (const q of qualCounts) {
            const pct = (q.count / maxQual * 100).toFixed(1);
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label" title="${q.title}">${q.title.substring(0, 25)}${q.title.length > 25 ? '...' : ''}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${pct}%; background: #2e7d32"></div>
                    </div>
                    <span class="chart-bar-value">${q.count}</span>
                </div>
            `;
        }
        html += '</div>';
    }
    
    // Top Occupations
    const occCounts = Object.entries(occupationSkillsMap)
        .map(([code, skills]) => ({code, title: taxonomyData.facets?.OCC?.values?.[code]?.name || code, count: skills.length}))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8);
    
    if (occCounts.length > 0) {
        const maxOcc = occCounts[0].count;
        html += '<div class="overview-card"><h3><i class="bi bi-person-badge"></i> Top Occupations (ANZSCO)</h3>';
        for (const o of occCounts) {
            const pct = (o.count / maxOcc * 100).toFixed(1);
            html += `
                <div class="chart-bar">
                    <span class="chart-bar-label" title="${o.title}">${o.title.substring(0, 25)}${o.title.length > 25 ? '...' : ''}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${pct}%; background: #e65100"></div>
                    </div>
                    <span class="chart-bar-value">${o.count}</span>
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
    
    html += '</div>';
    container.innerHTML = html;
}

function initializeFacetViews() {
    const facetIds = ['NAT', 'TRF', 'COG', 'CTX', 'FUT', 'DIG', 'ASCED'];
    
    for (const facetId of facetIds) {
        const container = document.getElementById(`${facetId}View`);
        if (!container) continue;
        
        let facetInfo = taxonomyData.facets[facetId];
        if (!facetInfo && facetId === 'ASCED') {
            facetInfo = taxonomyData.facets.IND;
        }
        if (!facetInfo) continue;
        
        // Count skills per facet value
        const valueCounts = {};
        const skillFacetKey = facetId === 'ASCED' ? (taxonomyData.skills[0]?.facets?.ASCED ? 'ASCED' : 'IND') : facetId;
        
        for (const skill of taxonomyData.skills) {
            const facetData = skill.facets?.[skillFacetKey];
            if (facetData) {
                const code = facetData.code;
                if (Array.isArray(code)) {
                    code.forEach(c => { valueCounts[c] = (valueCounts[c] || 0) + 1; });
                } else {
                    valueCounts[code] = (valueCounts[code] || 0) + 1;
                }
            }
        }
        
        const displayName = FACET_DISPLAY_NAMES[facetId] || facetInfo.facet_name || facetId;
        
        let html = `
            <div class="facet-view">
                <div class="facet-sidebar">
                    <div class="facet-search">
                        <input type="text" placeholder="Search skills..." id="${facetId}Search">
                    </div>
                    <div id="${facetId}Categories">
        `;
        
        for (const [code, valueInfo] of Object.entries(facetInfo.values || {})) {
            const count = valueCounts[code] || 0;
            const codeDisplay = facetId === 'ASCED' ? `<span class="asced-code">${code}</span>` : '';
            html += `
                <div class="facet-category" data-facet="${facetId}" data-value="${code}">
                    <div class="facet-category-header">
                        <span class="facet-category-name">${codeDisplay}${valueInfo.name}</span>
                        <span class="facet-category-count">${count}</span>
                    </div>
                    <div class="facet-category-desc">${(valueInfo.description || '').substring(0, 60)}${valueInfo.description?.length > 60 ? '...' : ''}</div>
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
        
        container.querySelectorAll('.facet-category').forEach(cat => {
            cat.addEventListener('click', () => {
                container.querySelectorAll('.facet-category').forEach(c => c.classList.remove('active'));
                cat.classList.add('active');
                loadFacetSkills(facetId, cat.dataset.value);
            });
        });
        
        document.getElementById(`${facetId}Search`)?.addEventListener('input', (e) => {
            searchFacetSkills(facetId, e.target.value);
        });
    }
}

function initializeQualOccViews() {
    // Initialize Qualifications View
    initializeQualOccView('QUAL', qualificationSkillsMap, 'qualifications', 'qual-code');
    
    // Initialize Occupations View
    initializeQualOccView('OCC', occupationSkillsMap, 'occupations', 'occ-code');
}

function initializeQualOccView(facetId, skillsMap, skillField, codeClass) {
    const container = document.getElementById(`${facetId}View`);
    if (!container) return;
    
    const facetInfo = taxonomyData.facets?.[facetId];
    if (!facetInfo) {
        container.innerHTML = '<p style="padding: 20px; color: var(--jsa-grey-500);">No data available for this view.</p>';
        return;
    }
    
    // Sort by skill count
    const sortedItems = Object.entries(skillsMap)
        .map(([code, skillIds]) => ({
            code,
            title: facetInfo.values?.[code]?.name || code,
            count: skillIds.length
        }))
        .sort((a, b) => b.count - a.count);
    
    const displayName = FACET_DISPLAY_NAMES[facetId] || facetInfo.facet_name || facetId;
    
    let html = `
        <div class="facet-view">
            <div class="facet-sidebar">
                <div class="facet-search">
                    <input type="text" placeholder="Search ${displayName.toLowerCase()}..." id="${facetId}Search">
                </div>
                <div id="${facetId}Categories">
    `;
    
    for (const item of sortedItems) {
        html += `
            <div class="facet-category" data-facet="${facetId}" data-value="${item.code}">
                <div class="facet-category-header">
                    <span class="facet-category-name"><span class="${codeClass}">${item.code}</span>${item.title}</span>
                    <span class="facet-category-count">${item.count}</span>
                </div>
            </div>
        `;
    }
    
    html += `
                </div>
            </div>
            <div class="facet-main">
                <div id="${facetId}SkillsGrid" class="skills-grid">
                    <p style="color: var(--jsa-grey-500); padding: 20px;">Select a ${displayName.toLowerCase().replace('s', '')} to view skills</p>
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
    
    // Event listeners
    container.querySelectorAll('.facet-category').forEach(cat => {
        cat.addEventListener('click', () => {
            container.querySelectorAll('.facet-category').forEach(c => c.classList.remove('active'));
            cat.classList.add('active');
            loadQualOccSkills(facetId, cat.dataset.value, skillsMap, skillField);
        });
    });
    
    document.getElementById(`${facetId}Search`)?.addEventListener('input', (e) => {
        searchQualOcc(facetId, e.target.value, sortedItems);
    });
}

function loadQualOccSkills(facetId, code, skillsMap, skillField) {
    currentFacetView = facetId;
    currentFacetValue = code;
    
    const grid = document.getElementById(`${facetId}SkillsGrid`);
    if (!grid) return;
    
    const skillIds = skillsMap[code] || [];
    const skills = skillIds.map(id => skillsIndex.get(id)).filter(Boolean);
    
    if (skills.length === 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">No skills found</p>';
        return;
    }
    
    let html = '';
    for (const skill of skills) {
        html += createSkillMiniCard(skill, facetId);
    }
    
    grid.innerHTML = html;
    
    grid.querySelectorAll('.skill-card-mini').forEach(card => {
        card.addEventListener('click', () => {
            grid.querySelectorAll('.skill-card-mini').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showSkillDetail(facetId, card.dataset.skillId);
        });
    });
}

function searchQualOcc(facetId, query, items) {
    const container = document.getElementById(`${facetId}Categories`);
    if (!container || !query || query.length < 2) {
        // Show all
        container.querySelectorAll('.facet-category').forEach(cat => {
            cat.style.display = '';
        });
        return;
    }
    
    const searchLower = query.toLowerCase();
    container.querySelectorAll('.facet-category').forEach(cat => {
        const code = cat.dataset.value || '';
        const name = cat.querySelector('.facet-category-name')?.textContent || '';
        if (code.toLowerCase().includes(searchLower) || name.toLowerCase().includes(searchLower)) {
            cat.style.display = '';
        } else {
            cat.style.display = 'none';
        }
    });
}

function loadFacetSkills(facetId, valueCode) {
    currentFacetView = facetId;
    currentFacetValue = valueCode;
    
    const grid = document.getElementById(`${facetId}SkillsGrid`);
    if (!grid) return;
    
    const skillFacetKey = facetId === 'ASCED' ? (taxonomyData.skills[0]?.facets?.ASCED ? 'ASCED' : 'IND') : facetId;
    
    let skills = taxonomyData.skills.filter(s => {
        const facetData = s.facets?.[skillFacetKey];
        if (!facetData) return false;
        const code = facetData.code;
        if (Array.isArray(code)) {
            return code.includes(valueCode);
        }
        return code === valueCode;
    });
    
    skills.sort((a, b) => {
        const confA = a.facets?.[skillFacetKey]?.confidence || 0;
        const confB = b.facets?.[skillFacetKey]?.confidence || 0;
        return confB - confA;
    });
    
    if (skills.length === 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">No skills found</p>';
        return;
    }
    
    let html = '';
    for (const skill of skills) {
        html += createSkillMiniCard(skill, facetId);
    }
    
    grid.innerHTML = html;
    
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
    
    detailContainer.classList.remove('detail-placeholder');
    selectedSkillId = skillId;
    
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
            if (fId === 'IND' && skill.facets.ASCED) continue;
            
            const facetDisplayName = FACET_DISPLAY_NAMES[fId] || fId;
            const confidenceHtml = fData.confidence ? `<span class="facet-confidence">${(fData.confidence * 100).toFixed(0)}%</span>` : '';
            const badgeClass = fId === 'IND' ? 'ASCED' : fId;
            html += `
                <div class="dimension-row">
                    <span class="dimension-label">${facetDisplayName}</span>
                    <div class="dimension-value">
                        <span class="facet-badge ${badgeClass}">${fData.name}</span>
                        ${confidenceHtml}
                    </div>
                </div>
            `;
        }
    }
    
    html += `</div></div>`;
    
    // Primary code with code name
    if (skill.code) {
        const codeNameHtml = skill.code_name ? `<span class="code-name-label">${skill.code_name}</span>` : '';
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-upc"></i> Primary Code</div>
                <div class="primary-code-display">
                    <span class="tag tag-code tag-primary">${skill.code}</span>
                    ${codeNameHtml}
                </div>
            </div>
        `;
    }
    
    // Related codes (excluding primary code)
    const relatedCodes = (skill.all_related_codes || []).filter(c => c !== skill.code);
    if (relatedCodes.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-upc-scan"></i> Related Codes (${relatedCodes.length})</div>
                <div class="tag-list">
                    ${relatedCodes.slice(0, 10).map(c => `<span class="tag tag-code">${c}</span>`).join('')}
                    ${relatedCodes.length > 10 ? `<span class="tag tag-more">+${relatedCodes.length - 10} more</span>` : ''}
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
                    ${skill.related_skills.slice(0, 8).map(r => `
                        <div class="related-skill-item" onclick="navigateToSkill('${facetId}', '${r.skill_id}')">
                            <span class="related-skill-name">${r.skill_name}</span>
                            <span class="related-skill-score">${(r.similarity * 100).toFixed(0)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Qualifications section
    if (skill.qualifications?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-award"></i> Qualifications (${skill.qualifications.length})</div>
                <div class="tag-list">
                    ${skill.qualifications.slice(0, 8).map(q => `<span class="tag tag-qual" title="${q.title}"><span class="qual-code">${q.code}</span>${q.title.substring(0, 30)}${q.title.length > 30 ? '...' : ''}</span>`).join('')}
                    ${skill.qualifications.length > 8 ? `<span class="tag tag-more">+${skill.qualifications.length - 8} more</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // Occupations section
    if (skill.occupations?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-person-badge"></i> Occupations (${skill.occupations.length})</div>
                <div class="tag-list">
                    ${skill.occupations.slice(0, 8).map(o => `<span class="tag tag-occ" title="${o.title}"><span class="occ-code">${o.code}</span>${o.title.substring(0, 30)}${o.title.length > 30 ? '...' : ''}</span>`).join('')}
                    ${skill.occupations.length > 8 ? `<span class="tag tag-more">+${skill.occupations.length - 8} more</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // Alternative titles
    if (skill.alternative_titles?.length > 0) {
        html += `
            <div class="detail-section">
                <div class="detail-section-title"><i class="bi bi-card-heading"></i> Alternative Titles (${skill.alternative_titles.length})</div>
                <div class="tag-list">
                    ${skill.alternative_titles.slice(0, 8).map(t => `<span class="tag tag-alt">${t}</span>`).join('')}
                    ${skill.alternative_titles.length > 8 ? `<span class="tag tag-more">+${skill.alternative_titles.length - 8} more</span>` : ''}
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
    
    let filtersHtml = '';
    const facetIcons = {
        'NAT': 'bi-bookmark', 'TRF': 'bi-arrow-left-right', 'COG': 'bi-lightbulb',
        'CTX': 'bi-briefcase', 'FUT': 'bi-robot', 'LRN': 'bi-book', 'DIG': 'bi-laptop',
        'ASCED': 'bi-mortarboard', 'IND': 'bi-mortarboard', 'LVL': 'bi-layers',
        'QUAL': 'bi-award', 'OCC': 'bi-person-badge'
    };
    
    // Standard facets
    for (const [facetId, facetInfo] of Object.entries(taxonomyData.facets || {})) {
        if (facetId === 'IND' && taxonomyData.facets.ASCED) continue;
        if (facetId === 'QUAL' || facetId === 'OCC') continue; // Handle separately
        
        const icon = facetIcons[facetId] || 'bi-tag';
        const displayName = FACET_DISPLAY_NAMES[facetId] || facetInfo.name || facetId;
        const options = Object.entries(facetInfo.values || {})
            .map(([code, valueInfo]) => {
                const count = originalFacetCounts[facetId]?.[code] || 0;
                return `<option value="${code}" data-original-count="${count}">${valueInfo.name} (${count})</option>`;
            })
            .join('');
        
        filtersHtml += `
            <div class="filter-section">
                <div class="filter-section-title"><i class="bi ${icon}"></i> ${displayName}</div>
                <select class="filter-select" id="filter_${facetId}" data-facet="${facetId}">
                    <option value="">All</option>
                    ${options}
                </select>
            </div>
        `;
    }
    
    // Qualification filter
    if (taxonomyData.facets?.QUAL) {
        const qualOptions = Object.entries(taxonomyData.facets.QUAL.values || {})
            .sort((a, b) => (qualificationSkillsMap[b[0]]?.length || 0) - (qualificationSkillsMap[a[0]]?.length || 0))
            .slice(0, 100)
            .map(([code, valueInfo]) => {
                const count = originalFacetCounts['QUAL']?.[code] || 0;
                return `<option value="${code}" data-original-count="${count}">${valueInfo.name} (${count})</option>`;
            })
            .join('');
        
        filtersHtml += `
            <div class="filter-section">
                <div class="filter-section-title"><i class="bi bi-award"></i> Qualification</div>
                <select class="filter-select" id="filter_QUAL" data-facet="QUAL">
                    <option value="">All</option>
                    ${qualOptions}
                </select>
            </div>
        `;
    }
    
    // Occupation filter
    if (taxonomyData.facets?.OCC) {
        const occOptions = Object.entries(taxonomyData.facets.OCC.values || {})
            .sort((a, b) => (occupationSkillsMap[b[0]]?.length || 0) - (occupationSkillsMap[a[0]]?.length || 0))
            .slice(0, 100)
            .map(([code, valueInfo]) => {
                const count = originalFacetCounts['OCC']?.[code] || 0;
                return `<option value="${code}" data-original-count="${count}">${valueInfo.name} (${count})</option>`;
            })
            .join('');
        
        filtersHtml += `
            <div class="filter-section">
                <div class="filter-section-title"><i class="bi bi-person-badge"></i> Occupation</div>
                <select class="filter-select" id="filter_OCC" data-facet="OCC">
                    <option value="">All</option>
                    ${occOptions}
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
                    <button class="filter-btn filter-btn-clear" onclick="clearMultiFilters()">
                        <i class="bi bi-x-lg"></i> Clear All Filters
                    </button>
                </div>
            </div>
            <div class="filter-main">
                <div class="filter-results-header">
                    <div class="filter-results-count">Showing <strong id="filterResultsCount">0</strong> skills</div>
                    <div class="active-filters" id="activeFilterTags"></div>
                </div>
                <div id="filterSkillsGrid" class="skills-grid">
                    <p style="color: var(--jsa-grey-500); padding: 20px;">Select filters to view skills</p>
                </div>
            </div>
            <div class="filter-detail">
                <div class="facet-detail-header"><h3><i class="bi bi-info-circle"></i> Skill Details</h3></div>
                <div id="filterDetail" class="detail-placeholder">
                    <i class="bi bi-hand-index"></i>
                    <p>Select a skill to view details</p>
                </div>
            </div>
        </div>
    `;
    
    container.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', () => {
            updateActiveFilterTags();
            applyMultiFilters();
            updateFilterCounts();
        });
    });
}

function updateActiveFilterTags() {
    const tagsContainer = document.getElementById('activeFilterTags');
    let tagsHtml = '';
    
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            const facetId = select.dataset.facet;
            const facetName = FACET_DISPLAY_NAMES[facetId] || facetId;
            const selectedOption = select.options[select.selectedIndex];
            // Extract just the name without the count
            const valueName = selectedOption.text.replace(/\\s*\\(\\d+\\)$/, '');
            tagsHtml += `
                <span class="active-filter-tag">
                    ${facetName}: ${valueName.substring(0, 20)}${valueName.length > 20 ? '...' : ''}
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
        updateFilterCounts();
    }
}

function getFilteredSkills() {
    activeFilters = {};
    
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            activeFilters[select.dataset.facet] = select.value;
        }
    });
    
    return taxonomyData.skills.filter(skill => {
        for (const [facetId, value] of Object.entries(activeFilters)) {
            // Handle QUAL filter (array field)
            if (facetId === 'QUAL') {
                const quals = skill.qualifications || [];
                if (!quals.some(q => q.code === value)) return false;
                continue;
            }
            
            // Handle OCC filter (array field)
            if (facetId === 'OCC') {
                const occs = skill.occupations || [];
                if (!occs.some(o => o.code === value)) return false;
                continue;
            }
            
            // Standard facet filter
            let skillFacetKey = facetId;
            if (facetId === 'ASCED' && !skill.facets?.ASCED && skill.facets?.IND) {
                skillFacetKey = 'IND';
            }
            
            const skillFacet = skill.facets?.[skillFacetKey];
            if (!skillFacet || skillFacet.code !== value) {
                return false;
            }
        }
        return true;
    });
}

function updateFilterCounts() {
    // Get current filtered skills based on active filters
    const currentFilters = {};
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            currentFilters[select.dataset.facet] = select.value;
        }
    });
    
    // For each filter dropdown, calculate counts for each option
    // based on what would be shown if that option were selected
    // (keeping other filters as they are)
    document.querySelectorAll('.filter-select').forEach(select => {
        const thisFacetId = select.dataset.facet;
        
        // Build filters excluding this facet
        const otherFilters = {...currentFilters};
        delete otherFilters[thisFacetId];
        
        // Get skills that match all other filters
        const baseSkills = taxonomyData.skills.filter(skill => {
            for (const [facetId, value] of Object.entries(otherFilters)) {
                if (facetId === 'QUAL') {
                    const quals = skill.qualifications || [];
                    if (!quals.some(q => q.code === value)) return false;
                    continue;
                }
                if (facetId === 'OCC') {
                    const occs = skill.occupations || [];
                    if (!occs.some(o => o.code === value)) return false;
                    continue;
                }
                let skillFacetKey = facetId;
                if (facetId === 'ASCED' && !skill.facets?.ASCED && skill.facets?.IND) {
                    skillFacetKey = 'IND';
                }
                const skillFacet = skill.facets?.[skillFacetKey];
                if (!skillFacet || skillFacet.code !== value) {
                    return false;
                }
            }
            return true;
        });
        
        // Now count how many of baseSkills match each option in this dropdown
        const optionCounts = {};
        
        baseSkills.forEach(skill => {
            if (thisFacetId === 'QUAL') {
                (skill.qualifications || []).forEach(q => {
                    optionCounts[q.code] = (optionCounts[q.code] || 0) + 1;
                });
            } else if (thisFacetId === 'OCC') {
                (skill.occupations || []).forEach(o => {
                    optionCounts[o.code] = (optionCounts[o.code] || 0) + 1;
                });
            } else {
                let skillFacetKey = thisFacetId;
                if (thisFacetId === 'ASCED' && !skill.facets?.ASCED && skill.facets?.IND) {
                    skillFacetKey = 'IND';
                }
                const facetData = skill.facets?.[skillFacetKey];
                if (facetData) {
                    const code = facetData.code;
                    if (Array.isArray(code)) {
                        code.forEach(c => { optionCounts[c] = (optionCounts[c] || 0) + 1; });
                    } else {
                        optionCounts[code] = (optionCounts[code] || 0) + 1;
                    }
                }
            }
        });
        
        // Update option text with new counts
        Array.from(select.options).forEach(option => {
            if (option.value === '') return; // Skip "All" option
            
            const code = option.value;
            const count = optionCounts[code] || 0;
            const originalCount = option.dataset.originalCount || count;
            
            // Extract original name (remove old count if present)
            let name = option.text.replace(/\\s*\\(\\d+\\)$/, '');
            
            // Update with new count
            option.text = `${name} (${count})`;
            
            // Disable options with 0 count (optional - remove if you want to keep them enabled)
            // option.disabled = count === 0;
        });
    });
}

function applyMultiFilters() {
    const filtered = getFilteredSkills();
    
    const grid = document.getElementById('filterSkillsGrid');
    const countEl = document.getElementById('filterResultsCount');
    
    countEl.textContent = filtered.length.toLocaleString();
    
    if (filtered.length === 0 && Object.keys(activeFilters).length > 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">No skills match the selected filters</p>';
        return;
    } else if (Object.keys(activeFilters).length === 0) {
        grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">Select filters to view skills</p>';
        return;
    }
    
    let html = '';
    for (const skill of filtered) {
        html += `
            <div class="skill-card-mini" data-skill-id="${skill.id}">
                <div class="skill-card-mini-name">${skill.name}</div>
            </div>
        `;
    }
    
    grid.innerHTML = html;
    
    grid.querySelectorAll('.skill-card-mini').forEach(card => {
        card.addEventListener('click', () => {
            grid.querySelectorAll('.skill-card-mini').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showSkillDetail('filter', card.dataset.skillId);
        });
    });
}

function clearMultiFilters() {
    document.querySelectorAll('.filter-select').forEach(select => { select.value = ''; });
    activeFilters = {};
    updateActiveFilterTags();
    
    const grid = document.getElementById('filterSkillsGrid');
    const countEl = document.getElementById('filterResultsCount');
    
    countEl.textContent = '0';
    grid.innerHTML = '<p style="color: var(--jsa-grey-500); padding: 20px;">Select filters to view skills</p>';
    
    const detailContainer = document.getElementById('filterDetail');
    detailContainer.classList.add('detail-placeholder');
    detailContainer.innerHTML = '<i class="bi bi-hand-index"></i><p>Select a skill to view details</p>';
    
    // Reset counts to original
    document.querySelectorAll('.filter-select').forEach(select => {
        Array.from(select.options).forEach(option => {
            if (option.value === '') return;
            const code = option.value;
            const originalCount = option.dataset.originalCount || 0;
            let name = option.text.replace(/\\s*\\(\\d+\\)$/, '');
            option.text = `${name} (${originalCount})`;
        });
    });
}

function initializeTableView() {
    const container = document.getElementById('tableView');
    
    const facetOptions = Object.entries(taxonomyData.facets || {})
        .filter(([id]) => !(id === 'IND' && taxonomyData.facets.ASCED))
        .map(([id, info]) => {
            const displayName = FACET_DISPLAY_NAMES[id] || info.name || id;
            return `<option value="${id}">${displayName}</option>`;
        }).join('');
    
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
                        <th>Primary Code</th>
                        <th>Code Name</th>
                        <th>Level</th>
                        <th>Nature</th>
                        <th>ASCED</th>
                        <th>Quals</th>
                        <th>Occs</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
        <div class="table-pagination" id="tablePagination"></div>
    `;
    
    renderTable();
    
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
    for (const [code, valInfo] of Object.entries(facetInfo.values || {})) {
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
        if (search && !s.name?.toLowerCase().includes(search) && !s.id?.toLowerCase().includes(search)) {
            return false;
        }
        
        if (facetId && facetValue) {
            if (facetId === 'QUAL') {
                if (!(s.qualifications || []).some(q => q.code === facetValue)) return false;
            } else if (facetId === 'OCC') {
                if (!(s.occupations || []).some(o => o.code === facetValue)) return false;
            } else {
                let skillFacetKey = facetId;
                if (facetId === 'ASCED' && !s.facets?.ASCED && s.facets?.IND) {
                    skillFacetKey = 'IND';
                }
                
                const facetData = s.facets?.[skillFacetKey];
                if (!facetData) return false;
                const code = facetData.code;
                if (Array.isArray(code)) {
                    if (!code.includes(facetValue)) return false;
                } else if (code !== facetValue) {
                    return false;
                }
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
    
    tbody.innerHTML = pageData.map(s => {
        const ascedField = s.facets?.ASCED?.name || s.facets?.IND?.name || '-';
        const qualCount = (s.qualifications || []).length;
        const occCount = (s.occupations || []).length;
        const primaryCode = s.code || '-';
        const codeName = s.code_name || '-';
        return `
            <tr>
                <td style="font-family: monospace; font-size: 0.75rem;">${s.id || '-'}</td>
                <td title="${s.name}">${s.name}</td>
                <td style="font-family: monospace; font-size: 0.75rem;">${primaryCode}</td>
                <td title="${codeName}">${codeName.substring(0, 25)}${codeName.length > 25 ? '...' : ''}</td>
                <td>${s.level || '-'}</td>
                <td>${s.facets?.NAT?.name || '-'}</td>
                <td title="${ascedField}">${ascedField.substring(0, 20)}${ascedField.length > 20 ? '...' : ''}</td>
                <td>${qualCount}</td>
                <td>${occCount}</td>
            </tr>
        `;
    }).join('');
    
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
            } else if (view === 'filter') {
                document.getElementById('filterView').classList.add('active');
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

function exportToExcel() {
    const exportData = taxonomyData.skills.map(s => ({
        'Skill ID': s.id || '',
        'Skill Name': s.name || '',
        'Description': s.description || '',
        'Category': s.category || '',
        'Level': s.level || '',
        'Primary Code': s.code || '',
        'Code Name': s.code_name || '',
        'Skill Nature': s.facets?.NAT?.name || '',
        'Transferability': s.facets?.TRF?.name || '',
        'Cognitive Complexity': s.facets?.COG?.name || '',
        'Work Context': s.facets?.CTX?.name || '',
        'Future Readiness': s.facets?.FUT?.name || '',
        'Digital Intensity': s.facets?.DIG?.name || '',
        'ASCED Field': s.facets?.ASCED?.name || s.facets?.IND?.name || '',
        'Qualification Count': (s.qualifications || []).length,
        'Qualification Codes': (s.qualifications || []).map(q => q.code).join('; '),
        'Qualification Titles': (s.qualifications || []).map(q => q.title).join('; '),
        'Occupation Count': (s.occupations || []).length,
        'Occupation Codes': (s.occupations || []).map(o => o.code).join('; '),
        'Occupation Titles': (s.occupations || []).map(o => o.title).join('; '),
        'Alternative Titles': (s.alternative_titles || []).join('; '),
        'All Related Codes': (s.all_related_codes || []).filter(c => c !== s.code).join('; ')
    }));
    
    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Skills with Qual & Occ');
    XLSX.writeFile(wb, 'vet_skills_taxonomy_with_qual_occ.xlsx');
}

function exportToCSV() {
    const headers = ['ID', 'Name', 'Primary Code', 'Code Name', 'Level', 'Nature', 'ASCED', 'Qual Count', 'Occ Count'];
    const rows = taxonomyData.skills.map(s => [
        s.id, s.name, s.code || '', s.code_name || '', s.level || '',
        s.facets?.NAT?.name || '', s.facets?.ASCED?.name || s.facets?.IND?.name || '',
        (s.qualifications || []).length, (s.occupations || []).length
    ].map(v => `"${String(v || '').replace(/"/g, '""')}"`).join(','));
    
    const csv = [headers.join(','), ...rows].join('\\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vet_skills_taxonomy_with_qual_occ.csv';
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
    
    <script>
        window.EXPECTED_DATA_FILE = '{DATA_FILE}';
    </script>
    <script src="{DATA_FILE}" onerror="handleDataLoadError()"></script>
    <script>
        function handleDataLoadError() {{
            document.querySelector('.loading-text').innerHTML = 
                'Error: Failed to load data file.<br>' +
                '<small style="font-size: 0.8rem;">Make sure <strong>' + window.EXPECTED_DATA_FILE + '</strong> is in the same directory.</small>';
            document.querySelector('.loading-text').style.color = '#c62828';
        }}
    </script>

    <script>
        {JAVASCRIPT_CONTENT}
    </script>
</body>
</html>
"""


def count_skills(data):
    """Count total skills"""
    return len(data.get('skills', []))


def generate_faceted_html(taxonomy_json_path: str, output_html_path: str):
    """Generate faceted HTML visualization with qualifications and occupations"""
    
    print(f"Loading faceted taxonomy from: {taxonomy_json_path}")
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_data = json.load(f)
    
    total_skills = count_skills(taxonomy_data)
    print(f"Taxonomy loaded: {total_skills} skills")
    
    # Count qualifications and occupations
    qual_count = len(taxonomy_data.get('facets', {}).get('QUAL', {}).get('values', {}))
    occ_count = len(taxonomy_data.get('facets', {}).get('OCC', {}).get('values', {}))
    print(f"Qualifications: {qual_count}, Occupations: {occ_count}")
    
    data_file = output_html_path.replace('.html', '_data.js')
    data_file_name = Path(data_file).name
    
    print(f"Creating external data file: {data_file_name}")
    with open(data_file, 'w') as f:
        f.write('// VET Skills Faceted Taxonomy Data with Qualifications and Occupations\n')
        f.write('// This file is auto-generated - do not edit manually\n')
        f.write('const TAXONOMY_DATA = ')
        json.dump(taxonomy_data, f, separators=(',', ':'))
        f.write(';\n')
    
    print(f"Data file created: {data_file}")
    
    html_content = HTML_TEMPLATE_EXTERNAL.format(
        CSS_CONTENT=CSS_CONTENT,
        BODY_CONTENT=BODY_CONTENT,
        DATA_FILE=data_file_name,
        JAVASCRIPT_CONTENT=JAVASCRIPT_CONTENT
    )
    
    print(f"Writing HTML to: {output_html_path}")
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("✓ Faceted HTML visualization generated successfully!")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  1. {output_html_path}")
    print(f"  2. {data_file}")
    print(f"\n⚠️  IMPORTANT: Both files must be in the same directory to work!")
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python generate_faceted_visualization_with_qual_occ.py <taxonomy.json> <output.html>")
        sys.exit(1)
    
    taxonomy_path = sys.argv[1]
    html_output_path = sys.argv[2]
    
    if not Path(taxonomy_path).exists():
        print(f"Error: Taxonomy file not found: {taxonomy_path}")
        sys.exit(1)
    
    generate_faceted_html(taxonomy_path, html_output_path)