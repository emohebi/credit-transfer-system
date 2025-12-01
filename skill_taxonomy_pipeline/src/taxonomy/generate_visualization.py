"""
Generate Interactive HTML Taxonomy Visualization

This script takes your taxonomy.json file and creates a beautiful interactive
HTML visualization with the data embedded.

Usage:
    python generate_visualization.py taxonomy.json output.html
"""

import json
import sys
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Dimensional Skill Taxonomy Explorer</title>
    
    <!-- External Libraries -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <script>
        // Embedded taxonomy data
        const EMBEDDED_TAXONOMY_DATA = {TAXONOMY_DATA};
        
        {JAVASCRIPT_CONTENT}
    </script>
</body>
</html>
"""


CSS_CONTENT = """
:root {
    --primary-color: #4A90E2;
    --secondary-color: #50C878;
    --accent-color: #FF6B6B;
    --bg-light: #F8F9FA;
    --bg-dark: #2C3E50;
    --text-primary: #2C3E50;
    --text-secondary: #6C757D;
    --border-color: #DEE2E6;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
    --shadow-lg: 0 4px 16px rgba(0,0,0,0.15);
}

* { box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    color: var(--text-primary);
    padding: 20px;
    margin: 0;
}

.main-container {
    max-width: 1600px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    box-shadow: var(--shadow-lg);
    overflow: hidden;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.header p {
    font-size: 1.1rem;
    opacity: 0.95;
    margin: 0;
}

.stats-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    padding: 30px;
    background: var(--bg-light);
    border-bottom: 1px solid var(--border-color);
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: var(--shadow);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.stat-card i {
    font-size: 2rem;
    color: var(--primary-color);
    margin-bottom: 10px;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 10px 0 5px 0;
}

.stat-label {
    font-size: 0.9rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.view-tabs {
    display: flex;
    background: white;
    border-bottom: 2px solid var(--border-color);
    padding: 0 30px;
}

.view-tab {
    padding: 20px 30px;
    cursor: pointer;
    border: none;
    background: none;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 3px solid transparent;
    transition: all 0.3s;
}

.view-tab:hover { color: var(--primary-color); }

.view-tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.content-area {
    padding: 30px;
    min-height: 600px;
}

.view-section {
    display: none;
}

.view-section.active {
    display: block;
}

.tree-controls {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.tree-search {
    flex: 1;
    min-width: 300px;
}

.tree-container {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    max-height: 800px;
    overflow-y: auto;
}

.tree-node {
    margin: 5px 0;
}

.node-content {
    display: flex;
    align-items: center;
    padding: 10px 15px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border-left: 3px solid transparent;
}

.node-content:hover {
    background: var(--bg-light);
    border-left-color: var(--primary-color);
}

.node-content.expanded {
    background: rgba(74, 144, 226, 0.1);
    border-left-color: var(--primary-color);
}

.node-toggle {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    color: var(--primary-color);
    font-weight: bold;
}

.node-icon {
    margin-right: 10px;
    font-size: 1.2rem;
}

.node-label {
    flex: 1;
    font-weight: 500;
}

.node-badge {
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 12px;
    background: var(--bg-light);
    color: var(--text-secondary);
    margin-left: 10px;
}

.node-children {
    margin-left: 30px;
    border-left: 2px solid var(--border-color);
    padding-left: 10px;
    display: none;
}

.node-children.expanded {
    display: block;
}

.node-domain .node-icon { color: #667eea; }
.node-family .node-icon { color: #50C878; }
.node-cluster .node-icon { color: #FF6B6B; }
.node-group .node-icon { color: #9B59B6; }
.node-section .node-icon { color: #95A5A6; }
.node-skill .node-icon { color: #FFA500; }

.skill-detail {
    background: var(--bg-light);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid var(--primary-color);
}

.skill-name {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.skill-description {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 10px;
}

.skill-dimensions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.dimension-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.dim-complexity { background: #E3F2FD; color: #1976D2; }
.dim-transferability { background: #F3E5F5; color: #7B1FA2; }
.dim-digital { background: #E8F5E9; color: #388E3C; }
.dim-future { background: #FFF3E0; color: #F57C00; }
.dim-nature { background: #FCE4EC; color: #C2185B; }
.dim-context { background: #E0F2F1; color: #00796B; }

.table-controls {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}

.filter-group {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

#skillsTable_wrapper {
    background: white;
    border-radius: 12px;
    padding: 20px;
}

.table {
    font-size: 0.9rem;
}

.table thead th {
    background: var(--primary-color);
    color: white;
    font-weight: 600;
    border: none;
    padding: 12px;
}

.table tbody td {
    padding: 12px;
    vertical-align: middle;
}

.table tbody tr:hover {
    background: rgba(74, 144, 226, 0.05);
}

.btn-custom {
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary-custom {
    background: var(--primary-color);
    color: white;
}

.btn-primary-custom:hover {
    background: #3A7BC8;
    transform: translateY(-1px);
    box-shadow: var(--shadow);
}

.btn-outline-custom {
    background: white;
    color: var(--primary-color);
    border: 2px solid var(--primary-color);
}

.btn-outline-custom:hover {
    background: var(--primary-color);
    color: white;
}

.export-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.chart-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: var(--shadow);
}

.chart-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--text-primary);
}

.relationship-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: rgba(155, 89, 182, 0.1);
    border-radius: 6px;
    font-size: 0.85rem;
    color: #9B59B6;
    text-decoration: none;
    margin: 2px;
    transition: all 0.2s;
}

.relationship-link:hover {
    background: rgba(155, 89, 182, 0.2);
    color: #8E44AD;
}

@media (max-width: 768px) {
    .header h1 { font-size: 1.8rem; }
    .stats-dashboard { grid-template-columns: repeat(2, 1fr); }
    .view-tabs { overflow-x: auto; }
    .tree-search { min-width: 100%; }
}
"""


# Body content remains the same as before
BODY_CONTENT = """
<div class="main-container">
    <div class="header">
        <h1><i class="bi bi-diagram-3"></i> Multi-Dimensional Skill Taxonomy</h1>
        <p>Explore skills across 5 hierarchical levels with 6 cross-cutting dimensions</p>
    </div>

    <div class="stats-dashboard" id="statsDashboard">
        <div class="stat-card">
            <i class="bi bi-diagram-3-fill"></i>
            <div class="stat-value" id="totalSkills">-</div>
            <div class="stat-label">Total Skills</div>
        </div>
        <div class="stat-card">
            <i class="bi bi-folder-fill"></i>
            <div class="stat-value" id="totalDomains">-</div>
            <div class="stat-label">Domains</div>
        </div>
        <div class="stat-card">
            <i class="bi bi-collection-fill"></i>
            <div class="stat-value" id="totalFamilies">-</div>
            <div class="stat-label">Families</div>
        </div>
        <div class="stat-card">
            <i class="bi bi-grid-fill"></i>
            <div class="stat-value" id="totalClusters">-</div>
            <div class="stat-label">Clusters</div>
        </div>
        <div class="stat-card">
            <i class="bi bi-graph-up"></i>
            <div class="stat-value" id="avgComplexity">-</div>
            <div class="stat-label">Avg Complexity</div>
        </div>
        <div class="stat-card">
            <i class="bi bi-cpu-fill"></i>
            <div class="stat-value" id="avgDigital">-</div>
            <div class="stat-label">Avg Digital</div>
        </div>
    </div>

    <div class="view-tabs">
        <button class="view-tab active" data-view="tree">
            <i class="bi bi-diagram-3"></i> Tree View
        </button>
        <button class="view-tab" data-view="table">
            <i class="bi bi-table"></i> Table View
        </button>
        <button class="view-tab" data-view="analytics">
            <i class="bi bi-bar-chart-fill"></i> Analytics
        </button>
    </div>

    <div class="content-area">
        <div class="view-section active" id="treeView">
            <div class="tree-controls">
                <input type="text" class="form-control tree-search" id="treeSearch" 
                       placeholder="🔍 Search skills, domains, or families...">
                <button class="btn btn-custom btn-outline-custom" onclick="expandAll()">
                    <i class="bi bi-arrows-expand"></i> Expand All
                </button>
                <button class="btn btn-custom btn-outline-custom" onclick="collapseAll()">
                    <i class="bi bi-arrows-collapse"></i> Collapse All
                </button>
            </div>
            <div class="tree-container" id="treeContainer"></div>
        </div>

        <div class="view-section" id="tableView">
            <div class="export-buttons">
                <button class="btn btn-custom btn-primary-custom" onclick="exportToCSV()">
                    <i class="bi bi-file-earmark-spreadsheet"></i> Export CSV
                </button>
                <button class="btn btn-custom btn-primary-custom" onclick="exportToJSON()">
                    <i class="bi bi-file-earmark-code"></i> Export JSON
                </button>
            </div>

            <div class="table-controls">
                <div class="filter-group">
                    <select class="form-select" id="filterDomain">
                        <option value="">All Domains</option>
                    </select>
                    <select class="form-select" id="filterComplexity">
                        <option value="">All Complexity</option>
                        <option value="1">1 - Foundational</option>
                        <option value="2">2 - Basic</option>
                        <option value="3">3 - Intermediate</option>
                        <option value="4">4 - Advanced</option>
                        <option value="5">5 - Expert</option>
                    </select>
                    <select class="form-select" id="filterTransferability">
                        <option value="">All Transferability</option>
                        <option value="universal">Universal</option>
                        <option value="cross_sector">Cross-Sector</option>
                        <option value="sector_specific">Sector-Specific</option>
                        <option value="occupation_specific">Occupation-Specific</option>
                    </select>
                    <select class="form-select" id="filterDigital">
                        <option value="">All Digital Intensity</option>
                        <option value="0">0 - No Digital</option>
                        <option value="1">1 - Low</option>
                        <option value="2">2 - Medium</option>
                        <option value="3">3 - High</option>
                        <option value="4">4 - Advanced</option>
                    </select>
                </div>
            </div>

            <table id="skillsTable" class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Skill Name</th>
                        <th>Domain</th>
                        <th>Family</th>
                        <th>Complexity</th>
                        <th>Transferability</th>
                        <th>Digital</th>
                        <th>Future</th>
                        <th>Nature</th>
                        <th>Context</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="view-section" id="analyticsView">
            <h3 style="margin-bottom: 20px;">Taxonomy Analytics Dashboard</h3>
            <div class="charts-grid" id="chartsContainer"></div>
        </div>
    </div>
</div>
"""


# Read the JavaScript content from the HTML file (simplified version for embedding)
JAVASCRIPT_CONTENT = """
let taxonomyData = EMBEDDED_TAXONOMY_DATA;
let flatSkillsData = [];
let dataTable = null;

flatSkillsData = flattenTaxonomy(taxonomyData);
initializeStats();
renderTree();
initializeTable();
renderAnalytics();

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
            
            // Build path based on node type
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
    document.getElementById('totalClusters').textContent = stats.total_clusters || countNodeType(taxonomyData, 'cluster');
    
    if (flatSkillsData.length > 0) {
        const avgComplexity = flatSkillsData.reduce((sum, s) => sum + (s.dimensions?.complexity_level || 3), 0) / flatSkillsData.length;
        const avgDigital = flatSkillsData.reduce((sum, s) => sum + (s.dimensions?.digital_intensity || 1), 0) / flatSkillsData.length;
        document.getElementById('avgComplexity').textContent = avgComplexity.toFixed(1);
        document.getElementById('avgDigital').textContent = avgDigital.toFixed(1);
    }
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
        toggle.innerHTML = '▶';
        toggle.onclick = (e) => { e.stopPropagation(); toggleNode(nodeDiv); };
        contentDiv.appendChild(toggle);
    } else {
        const spacer = document.createElement('span');
        spacer.className = 'node-toggle';
        contentDiv.appendChild(spacer);
    }
    
    const icon = document.createElement('i');
    icon.className = 'bi node-icon';
    if (node.type === 'domain') icon.classList.add('bi-folder-fill');
    else if (node.type === 'family') icon.classList.add('bi-collection-fill');
    else if (node.type === 'cluster') icon.classList.add('bi-grid-fill');
    else if (node.type === 'group') icon.classList.add('bi-box-seam');  // Skill groups
    else if (node.type === 'section') icon.classList.add('bi-layers');  // Balancing sections
    else if (node.type === 'skill') icon.classList.add('bi-gem');
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
        
        // Add child nodes (for domains, families, clusters)
        if (node.children) {
            node.children.forEach(child => {
                childrenDiv.appendChild(createTreeNode(child, level + 1));
            });
        }
        
        // Add skills (for groups)
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
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'skill-name';
    nameDiv.innerHTML = `<i class="bi bi-gem" style="color: #FFA500;"></i> ${skill.name}`;
    skillDiv.appendChild(nameDiv);
    
    if (skill.description) {
        const descDiv = document.createElement('div');
        descDiv.className = 'skill-description';
        descDiv.textContent = skill.description;
        skillDiv.appendChild(descDiv);
    }
    
    if (skill.dimensions) {
        const dimsDiv = document.createElement('div');
        dimsDiv.className = 'skill-dimensions';
        
        const dims = skill.dimensions;
        if (dims.complexity_level) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-complexity"><i class="bi bi-bar-chart"></i> Level ${dims.complexity_level}</span>`;
        }
        if (dims.transferability) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-transferability"><i class="bi bi-arrow-left-right"></i> ${dims.transferability}</span>`;
        }
        if (dims.digital_intensity !== undefined) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-digital"><i class="bi bi-cpu"></i> Digital ${dims.digital_intensity}</span>`;
        }
        if (dims.future_readiness) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-future"><i class="bi bi-graph-up"></i> ${dims.future_readiness}</span>`;
        }
        if (dims.skill_nature) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-nature"><i class="bi bi-gear"></i> ${dims.skill_nature}</span>`;
        }
        if (skill.context) {
            dimsDiv.innerHTML += `<span class="dimension-badge dim-context"><i class="bi bi-book"></i> ${skill.context}</span>`;
        }
        
        skillDiv.appendChild(dimsDiv);
    }
    
    if (skill.relationships?.related && skill.relationships.related.length > 0) {
        const relDiv = document.createElement('div');
        relDiv.style.marginTop = '10px';
        relDiv.innerHTML = '<strong style="font-size: 0.85rem; color: #6C757D;">Related Skills:</strong><br>';
        
        skill.relationships.related.forEach(rel => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'relationship-link';
            link.innerHTML = `<i class="bi bi-link-45deg"></i> ${rel.skill_name}`;
            link.onclick = (e) => { e.preventDefault(); searchAndHighlight(rel.skill_id); };
            relDiv.appendChild(link);
        });
        
        skillDiv.appendChild(relDiv);
    }
    
    return skillDiv;
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
            toggle.innerHTML = '▶';
        } else {
            children.classList.add('expanded');
            content.classList.add('expanded');
            toggle.innerHTML = '▼';
        }
    }
}

function expandAll() {
    document.querySelectorAll('.node-children').forEach(child => child.classList.add('expanded'));
    document.querySelectorAll('.node-content').forEach(content => content.classList.add('expanded'));
    document.querySelectorAll('.node-toggle').forEach(toggle => { toggle.innerHTML = '▼'; });
}

function collapseAll() {
    document.querySelectorAll('.node-children').forEach(child => child.classList.remove('expanded'));
    document.querySelectorAll('.node-content').forEach(content => content.classList.remove('expanded'));
    document.querySelectorAll('.node-toggle').forEach(toggle => { toggle.innerHTML = '▶'; });
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
                        const toggle = parentNode.querySelector('.node-toggle');
                        if (content) content.classList.add('expanded');
                        if (toggle) toggle.innerHTML = '▼';
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
    const tableBody = document.querySelector('#skillsTable tbody');
    tableBody.innerHTML = '';
    
    const domains = [...new Set(flatSkillsData.map(s => s.domain))];
    const domainSelect = document.getElementById('filterDomain');
    domains.forEach(domain => {
        const option = document.createElement('option');
        option.value = domain;
        option.textContent = domain;
        domainSelect.appendChild(option);
    });
    
    if (dataTable) dataTable.destroy();
    
    dataTable = $('#skillsTable').DataTable({
        data: flatSkillsData,
        columns: [
            { data: 'name' },
            { data: 'domain' },
            { data: 'family' },
            { data: 'dimensions.complexity_level', render: (data) => data || '-' },
            { data: 'dimensions.transferability', render: (data) => data || '-' },
            { data: 'dimensions.digital_intensity', render: (data) => data !== undefined ? data : '-' },
            { data: 'dimensions.future_readiness', render: (data) => data || '-' },
            { data: 'dimensions.skill_nature', render: (data) => data || '-' },
            { data: 'context', render: (data) => data || '-' }
        ],
        pageLength: 25,
        responsive: true,
        order: [[0, 'asc']]
    });
    
    ['filterDomain', 'filterComplexity', 'filterTransferability', 'filterDigital'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', applyFilters);
    });
}

function applyFilters() {
    const domain = document.getElementById('filterDomain').value;
    const complexity = document.getElementById('filterComplexity').value;
    const transferability = document.getElementById('filterTransferability').value;
    const digital = document.getElementById('filterDigital').value;
    
    let filtered = flatSkillsData;
    
    if (domain) filtered = filtered.filter(s => s.domain === domain);
    if (complexity) filtered = filtered.filter(s => s.dimensions?.complexity_level === parseInt(complexity));
    if (transferability) filtered = filtered.filter(s => s.dimensions?.transferability === transferability);
    if (digital) filtered = filtered.filter(s => s.dimensions?.digital_intensity === parseInt(digital));
    
    dataTable.clear().rows.add(filtered).draw();
}

function renderAnalytics() {
    const container = document.getElementById('chartsContainer');
    container.innerHTML = '';
    
    createChart(container, 'Complexity Level Distribution', getDistribution(flatSkillsData, 'dimensions.complexity_level'));
    createChart(container, 'Transferability Distribution', getDistribution(flatSkillsData, 'dimensions.transferability'));
    createChart(container, 'Digital Intensity Distribution', getDistribution(flatSkillsData, 'dimensions.digital_intensity'));
    createChart(container, 'Future Readiness Distribution', getDistribution(flatSkillsData, 'dimensions.future_readiness'));
    createChart(container, 'Skills by Domain', getDistribution(flatSkillsData, 'domain'));
}

function getDistribution(data, field) {
    const counts = {};
    data.forEach(item => {
        const value = field.split('.').reduce((obj, key) => obj?.[key], item) || 'Unknown';
        counts[value] = (counts[value] || 0) + 1;
    });
    return counts;
}

function createChart(container, title, data) {
    const card = document.createElement('div');
    card.className = 'chart-card';
    
    const titleDiv = document.createElement('div');
    titleDiv.className = 'chart-title';
    titleDiv.textContent = title;
    card.appendChild(titleDiv);
    
    const canvas = document.createElement('canvas');
    card.appendChild(canvas);
    container.appendChild(card);
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Count',
                data: Object.values(data),
                backgroundColor: 'rgba(74, 144, 226, 0.7)',
                borderColor: 'rgba(74, 144, 226, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function exportToCSV() {
    const csv = convertToCSV(flatSkillsData);
    downloadFile(csv, 'skills_taxonomy.csv', 'text/csv');
}

function exportToJSON() {
    const json = JSON.stringify(taxonomyData, null, 2);
    downloadFile(json, 'skills_taxonomy.json', 'application/json');
}

function convertToCSV(data) {
    const headers = ['Name', 'Domain', 'Family', 'Complexity', 'Transferability', 'Digital', 'Future', 'Nature', 'Context'];
    const rows = data.map(s => [
        s.name, s.domain, s.family,
        s.dimensions?.complexity_level || '',
        s.dimensions?.transferability || '',
        s.dimensions?.digital_intensity || '',
        s.dimensions?.future_readiness || '',
        s.dimensions?.skill_nature || '',
        s.context || ''
    ].map(v => `"${v}"`).join(','));
    return [headers.join(','), ...rows].join('\\n');
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


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Usage: python generate_visualization.py <taxonomy.json> [output.html]")
    #     print("\nExample:")
    #     print("  python generate_visualization.py output/taxonomy.json taxonomy_viz.html")
    #     sys.exit(1)
    
    taxonomy_path = "./output/taxonomy.json"
    output_path = './output/taxonomy_visualization.html'
    
    if not Path(taxonomy_path).exists():
        print(f"Error: Taxonomy file not found: {taxonomy_path}")
        sys.exit(1)
    
    generate_html(taxonomy_path, output_path)
