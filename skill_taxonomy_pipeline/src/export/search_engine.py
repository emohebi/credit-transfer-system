"""
Generate an HTML-based search engine for the Skill Assertion schema.

Features:
  - Full-text search across skills, units, alternative labels
  - Lazy-loaded skill detail panels with assertions
  - Facet filters
  - Context/level distribution bars
  - Unit → Skill reverse lookup
  - External data file for performance
"""
import json
from pathlib import Path


def generate_search_html(export_data: dict, html_path: str, data_js_path: str):
    """Write the search engine HTML + data JS file."""

    # Write data JS
    with open(data_js_path, "w") as f:
        f.write("// Skill Assertion Pipeline — Search Data\n")
        f.write("// Auto-generated, do not edit\n")
        f.write("const ASSERTION_DATA = ")
        json.dump(export_data, f, separators=(",", ":"), default=str)
        f.write(";\n")

    data_file_name = Path(data_js_path).name

    html = _build_html(data_file_name)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


def _build_html(data_file: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VET Skill Assertion Explorer</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{_css()}</style>
</head>
<body>

<div id="app">
  <header class="hdr">
    <div class="hdr-inner">
      <div class="hdr-brand">
        <div class="hdr-icon"><i class="bi bi-diagram-3"></i></div>
        <div>
          <h1>Skill Assertion Explorer</h1>
          <p class="hdr-sub">Search skills, view teaching context, explore unit linkages</p>
        </div>
      </div>
      <div class="hdr-stats" id="headerStats"></div>
    </div>
  </header>

  <div class="shell">
    <!-- Tabs -->
    <nav class="tabs">
      <button class="tab active" data-tab="skills"><i class="bi bi-mortarboard"></i> Skills</button>
      <button class="tab" data-tab="units"><i class="bi bi-journal-code"></i> Units</button>
      <button class="tab" data-tab="quals"><i class="bi bi-award"></i> Qualifications</button>
      <button class="tab" data-tab="occs"><i class="bi bi-person-badge"></i> Occupations</button>
      <button class="tab" data-tab="matrix"><i class="bi bi-water"></i> Sankey Flow</button>
    </nav>

    <!-- Skills Tab -->
    <section class="panel" id="skillsPanel">
      <div class="search-row">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input type="text" id="skillSearch" placeholder="Search skills, alternative names, unit codes…" autocomplete="off">
        </div>
        <div class="filter-chips" id="facetFilters"></div>
      </div>
      <div class="results-meta" id="skillResultsMeta"></div>
      <div class="results-grid" id="skillResults"></div>
      <div class="load-more-wrap" id="skillLoadMore" style="display:none">
        <button class="btn-load" onclick="loadMoreSkills()">Load more</button>
      </div>
    </section>

    <!-- Units Tab -->
    <section class="panel hidden" id="unitsPanel">
      <div class="search-row">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input type="text" id="unitSearch" placeholder="Search unit codes or titles…" autocomplete="off">
        </div>
      </div>
      <div class="results-meta" id="unitResultsMeta"></div>
      <div class="results-grid" id="unitResults"></div>
      <div class="load-more-wrap" id="unitLoadMore" style="display:none">
        <button class="btn-load" onclick="loadMoreUnits()">Load more</button>
      </div>
    </section>

    <!-- Qualifications Tab -->
    <section class="panel hidden" id="qualsPanel">
      <div class="search-row">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input type="text" id="qualSearch" placeholder="Search qualification codes or titles…" autocomplete="off">
        </div>
      </div>
      <div class="results-meta" id="qualResultsMeta"></div>
      <div class="results-grid" id="qualResults"></div>
      <div class="load-more-wrap" id="qualLoadMore" style="display:none">
        <button class="btn-load" onclick="loadMoreQuals()">Load more</button>
      </div>
    </section>

    <!-- Occupations Tab -->
    <section class="panel hidden" id="occsPanel">
      <div class="search-row">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input type="text" id="occSearch" placeholder="Search ANZSCO codes or titles…" autocomplete="off">
        </div>
      </div>
      <div class="results-meta" id="occResultsMeta"></div>
      <div class="results-grid" id="occResults"></div>
      <div class="load-more-wrap" id="occLoadMore" style="display:none">
        <button class="btn-load" onclick="loadMoreOccs()">Load more</button>
      </div>
    </section>

    <!-- Sankey Flow Tab -->
    <section class="panel hidden" id="matrixPanel">
      <div class="matrix-controls">
        <div class="search-box" style="flex:1;min-width:260px">
          <i class="bi bi-search"></i>
          <input type="text" id="matrixSearch" placeholder="Search a skill, unit, qualification or occupation…" autocomplete="off">
        </div>
        <div class="matrix-legend">
          <span class="legend-dot" style="background:#0f6b5e"></span> Skill
          <span class="legend-dot" style="background:#6d28d9"></span> Assertion
          <span class="legend-dot" style="background:#2563ab"></span> Unit
          <span class="legend-dot" style="background:#16a34a"></span> Qualification
          <span class="legend-dot" style="background:#dc6b16"></span> Occupation
        </div>
      </div>
      <div id="matrixHint" class="graph-hint">Search for any entity to see the full Skill → Unit → Qualification → Occupation flow</div>
      <div id="matrixContainer" style="overflow-x:auto"></div>
      <div id="matrixDetail" style="margin-top:16px"></div>
    </section>

  </div>

  <!-- Skill Detail Drawer -->
  <div class="drawer-overlay hidden" id="drawerOverlay" onclick="closeDrawer()"></div>
  <aside class="drawer hidden" id="drawer">
    <div class="drawer-head">
      <h2 id="drawerTitle"></h2>
      <button class="drawer-close" onclick="closeDrawer()"><i class="bi bi-x-lg"></i></button>
    </div>
    <div class="drawer-body" id="drawerBody"></div>
  </aside>
</div>

<script src="{data_file}" onerror="document.getElementById('skillResults').innerHTML='<p class=\\'err\\'>Failed to load data file. Ensure <b>{data_file}</b> is in the same directory.</p>'"></script>
<script>{_js()}</script>
</body>
</html>"""


def _css() -> str:
    return """
:root {
  --c-bg: #f4f6f9;
  --c-surface: #ffffff;
  --c-border: #e2e6ed;
  --c-text: #1a1f36;
  --c-text2: #5a6072;
  --c-text3: #8892a4;
  --c-accent: #0f6b5e;
  --c-accent-light: #e8f5f1;
  --c-accent2: #1e3a5f;
  --c-tag-bg: #eef1f6;
  --c-tag-text: #3d4663;
  --c-prac: #0d7c3e;
  --c-theo: #2563ab;
  --c-hybrid: #7c3aed;
  --radius: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.1);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DM Sans', sans-serif; background: var(--c-bg); color: var(--c-text); line-height: 1.55; }

/* Header */
.hdr { background: linear-gradient(135deg, var(--c-accent2) 0%, #0d2137 100%); color: #fff; }
.hdr-inner { max-width: 1280px; margin: 0 auto; padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.hdr-brand { display: flex; align-items: center; gap: 14px; }
.hdr-icon { width: 42px; height: 42px; background: var(--c-accent); border-radius: 10px; display: grid; place-items: center; font-size: 1.2rem; }
.hdr h1 { font-size: 1.35rem; font-weight: 700; letter-spacing: -.02em; }
.hdr-sub { font-size: .82rem; opacity: .75; font-weight: 400; }
.hdr-stats { display: flex; gap: 20px; font-size: .8rem; opacity: .85; }
.hdr-stat b { font-weight: 600; }

/* Shell */
.shell { max-width: 1280px; margin: 0 auto; padding: 0 24px 60px; }

/* Tabs */
.tabs { display: flex; gap: 4px; margin-top: 20px; margin-bottom: 0; }
.tab { padding: 10px 20px; background: transparent; border: none; font: inherit; font-weight: 500; font-size: .88rem; color: var(--c-text3); cursor: pointer; border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 6px; }
.tab:hover { color: var(--c-text); }
.tab.active { color: var(--c-accent); border-bottom-color: var(--c-accent); }

/* Panel */
.panel { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: 0 0 var(--radius) var(--radius); padding: 20px; min-height: 400px; }
.panel.hidden { display: none; }

/* Search */
.search-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
.search-box { flex: 1; min-width: 280px; position: relative; }
.search-box i { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--c-text3); }
.search-box input { width: 100%; padding: 11px 14px 11px 40px; border: 2px solid var(--c-border); border-radius: var(--radius); font: inherit; font-size: .92rem; }
.search-box input:focus { outline: none; border-color: var(--c-accent); }

/* Filter chips */
.filter-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 20px; font-size: .78rem; font-weight: 500; cursor: pointer; border: 1.5px solid var(--c-border); background: var(--c-surface); color: var(--c-text2); transition: all .15s; }
.chip:hover { border-color: var(--c-accent); color: var(--c-accent); }
.chip.active { background: var(--c-accent-light); border-color: var(--c-accent); color: var(--c-accent); }

/* Results */
.results-meta { font-size: .82rem; color: var(--c-text3); margin-bottom: 12px; }
.results-meta b { color: var(--c-accent); }
.results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }

/* Skill card */
.skill-card { background: var(--c-surface); border: 1.5px solid var(--c-border); border-radius: var(--radius); padding: 16px; cursor: pointer; transition: all .15s; }
.skill-card:hover { border-color: var(--c-accent); box-shadow: var(--shadow); }
.skill-card-name { font-weight: 600; font-size: .95rem; color: var(--c-text); margin-bottom: 6px; }
.skill-card-def { font-size: .82rem; color: var(--c-text2); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 10px; }
.skill-card-meta { display: flex; gap: 6px; flex-wrap: wrap; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: .72rem; font-weight: 600; }
.badge-count { background: var(--c-accent-light); color: var(--c-accent); }
.badge-ctx { font-size: .7rem; }
.badge-prac { background: #dcfce7; color: var(--c-prac); }
.badge-theo { background: #dbeafe; color: var(--c-theo); }
.badge-hybrid { background: #ede9fe; color: var(--c-hybrid); }
.badge-facet { background: var(--c-tag-bg); color: var(--c-tag-text); }
.badge-alt { background: #fff7ed; color: #92400e; font-weight: 400; }

/* Unit card */
.unit-card { background: var(--c-surface); border: 1.5px solid var(--c-border); border-radius: var(--radius); padding: 14px; cursor: pointer; transition: all .15s; }
.unit-card:hover { border-color: var(--c-accent); }
.unit-code { font-family: 'JetBrains Mono', monospace; font-size: .88rem; font-weight: 600; color: var(--c-accent2); }
.unit-skill-count { font-size: .78rem; color: var(--c-text3); margin-top: 4px; }

/* Load more */
.load-more-wrap { text-align: center; margin-top: 16px; }
.btn-load { padding: 10px 28px; border: 2px solid var(--c-border); border-radius: var(--radius); background: var(--c-surface); font: inherit; font-weight: 600; color: var(--c-text2); cursor: pointer; }
.btn-load:hover { border-color: var(--c-accent); color: var(--c-accent); }

/* Drawer */
.drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.35); z-index: 900; }
.drawer-overlay.hidden { display: none; }
.drawer { position: fixed; top: 0; right: 0; width: 560px; max-width: 95vw; height: 100vh; background: var(--c-surface); z-index: 1000; box-shadow: var(--shadow-lg); overflow-y: auto; transform: translateX(0); transition: transform .2s ease; }
.drawer.hidden { transform: translateX(100%); pointer-events: none; }
.drawer-head { position: sticky; top: 0; background: var(--c-surface); padding: 18px 20px; border-bottom: 1px solid var(--c-border); display: flex; justify-content: space-between; align-items: flex-start; z-index: 10; }
.drawer-head h2 { font-size: 1.1rem; font-weight: 700; color: var(--c-accent2); flex: 1; line-height: 1.3; }
.drawer-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--c-text3); padding: 4px; }
.drawer-body { padding: 20px; }

/* Drawer sections */
.d-section { margin-bottom: 20px; }
.d-label { font-size: .72rem; font-weight: 600; color: var(--c-text3); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.d-def { font-size: .88rem; color: var(--c-text2); line-height: 1.6; padding: 12px; background: var(--c-bg); border-radius: 8px; }
.d-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.d-tag { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: .75rem; background: var(--c-tag-bg); color: var(--c-tag-text); }
.d-tag.code { font-family: 'JetBrains Mono', monospace; font-size: .7rem; background: #e8eaf6; color: #3949ab; }

/* Distribution bars */
.dist-row { display: flex; align-items: center; margin-bottom: 6px; }
.dist-label { width: 100px; font-size: .78rem; color: var(--c-text2); font-weight: 500; }
.dist-bar-track { flex: 1; height: 18px; background: var(--c-bg); border-radius: 4px; overflow: hidden; margin: 0 8px; }
.dist-bar-fill { height: 100%; border-radius: 4px; transition: width .3s; }
.dist-bar-fill.prac { background: #86efac; }
.dist-bar-fill.theo { background: #93c5fd; }
.dist-bar-fill.hybrid { background: #c4b5fd; }
.dist-bar-fill.level { background: var(--c-accent); opacity: .7; }
.dist-val { width: 36px; text-align: right; font-size: .78rem; font-weight: 600; color: var(--c-text); }

/* Assertion table */
.a-table { width: 100%; border-collapse: collapse; font-size: .8rem; }
.a-table th { text-align: left; padding: 8px 6px; font-size: .7rem; text-transform: uppercase; letter-spacing: .5px; color: var(--c-text3); border-bottom: 2px solid var(--c-border); }
.a-table td { padding: 8px 6px; border-bottom: 1px solid var(--c-border); vertical-align: top; }
.a-table tr:hover td { background: var(--c-bg); }
.a-evidence { font-size: .75rem; color: var(--c-text2); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.a-ctx-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.a-ctx-dot.prac { background: var(--c-prac); }
.a-ctx-dot.theo { background: var(--c-theo); }
.a-ctx-dot.hybrid { background: var(--c-hybrid); }

/* Facet dimension rows */
.facet-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--c-bg); }
.facet-row:last-child { border-bottom: none; }
.facet-dim { font-size: .78rem; color: var(--c-text2); }
.facet-val { font-size: .78rem; font-weight: 600; color: var(--c-text); }

.err { color: #c62828; padding: 20px; font-size: .9rem; }

/* Graph */
.matrix-controls { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
.graph-legend, .matrix-legend { display: flex; gap: 14px; align-items: center; font-size: .78rem; color: var(--c-text2); flex-wrap: wrap; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 3px; }
.graph-hint { text-align: center; margin-top: 12px; font-size: .82rem; color: var(--c-text3); }

/* Sankey flow */
.sk-node { transition: opacity .2s ease; }
.sk-flow { transition: stroke-opacity .2s ease, stroke-width .2s ease; }

/* Assertion detail card (below matrix/scatter) */
.assertion-detail-card { background: var(--c-bg); border-radius: var(--radius); padding: 16px; border: 1px solid var(--c-border); animation: fadeIn .15s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.assertion-detail-card h4 { font-size: .9rem; color: var(--c-accent2); margin-bottom: 10px; }
.assertion-meta-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }
.assertion-meta-item { font-size: .8rem; }
.assertion-meta-item b { color: var(--c-text); }
.assertion-evidence { font-size: .82rem; color: var(--c-text2); padding: 10px; background: white; border-radius: 6px; margin-top: 8px; line-height: 1.5; border-left: 3px solid var(--c-accent); }

@media (max-width: 640px) {
  .results-grid { grid-template-columns: 1fr; }
  .drawer { width: 100vw; }
  .hdr-stats { display: none; }
}
"""


def _js() -> str:
    return r"""
let data = null;
let skillIndex = new Map();
let unitIndex = new Map();
let qualIndex = new Map();
let occIndex = new Map();

// Lazy loading state
let skillPage = 0, unitPage = 0, qualPage = 0, occPage = 0;
const PAGE_SIZE = 40;
let filteredSkills = [], filteredUnits = [], filteredQuals = [], filteredOccs = [];
let activeFilters = {};

const FACET_NAMES = { NAT:'Nature', TRF:'Transfer', COG:'Cognitive', ASCED:'ASCED', LRN:'Learning', DIG:'Digital', FUT:'Future', LVL:'Level' };
const CTX_CLASS = { PRACTICAL:'prac', THEORETICAL:'theo', HYBRID:'hybrid' };

document.addEventListener('DOMContentLoaded', () => {
  const check = setInterval(() => {
    if (typeof ASSERTION_DATA !== 'undefined') {
      clearInterval(check);
      init(ASSERTION_DATA);
    }
  }, 80);
  setTimeout(() => clearInterval(check), 8000);
});

function init(d) {
  data = d;
  data.skills.forEach(s => skillIndex.set(s.skill_id, s));
  (data.units||[]).forEach(u => unitIndex.set(u.unit_code, u));
  (data.qualifications||[]).forEach(q => qualIndex.set(q.qualification_code, q));
  (data.occupations||[]).forEach(o => occIndex.set(o.anzsco_code, o));

  filteredSkills = [...data.skills];
  filteredUnits = [...(data.units||[])];
  filteredQuals = [...(data.qualifications||[])];
  filteredOccs = [...(data.occupations||[])];

  renderHeaderStats();
  renderFacetFilters();
  resetSkillResults();
  resetUnitResults();
  resetQualResults();
  resetOccResults();

  document.getElementById('skillSearch').addEventListener('input', debounce(onSkillSearch, 200));
  document.getElementById('unitSearch').addEventListener('input', debounce(onUnitSearch, 200));
  document.getElementById('qualSearch').addEventListener('input', debounce(onQualSearch, 200));
  document.getElementById('occSearch').addEventListener('input', debounce(onOccSearch, 200));
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', onTabClick));
}

function renderHeaderStats() {
  const m = data.metadata;
  let html = `<span><b>${m.total_skills.toLocaleString()}</b> Skills</span>` +
    `<span><b>${m.total_assertions.toLocaleString()}</b> Assertions</span>` +
    `<span><b>${m.total_units.toLocaleString()}</b> Units</span>`;
  if (m.total_qualifications) html += `<span><b>${m.total_qualifications.toLocaleString()}</b> Quals</span>`;
  if (m.total_occupations) html += `<span><b>${m.total_occupations.toLocaleString()}</b> Occupations</span>`;
  document.getElementById('headerStats').innerHTML = html;
}

function renderFacetFilters() {
  const container = document.getElementById('facetFilters');
  if (!data.facets) return;
  let html = '';
  for (const [fid, fi] of Object.entries(data.facets)) {
    for (const [code, vi] of Object.entries(fi.values || {})) {
      const count = data.skills.filter(s => {
        const fc = s.facets?.[fid]?.code;
        if (Array.isArray(fc)) return fc.includes(code);
        return fc === code;
      }).length;
      if (count > 0) {
        html += `<button class="chip" data-facet="${fid}" data-code="${code}" onclick="toggleFilter('${fid}','${code}')">${vi.name} <span style="opacity:.6">${count}</span></button>`;
      }
    }
  }
  container.innerHTML = html;
}

function toggleFilter(fid, code) {
  const key = fid + '|' + code;
  if (activeFilters[key]) { delete activeFilters[key]; }
  else { Object.keys(activeFilters).forEach(k => { if (k.startsWith(fid + '|')) delete activeFilters[k]; }); activeFilters[key] = true; }
  document.querySelectorAll('.chip').forEach(c => { c.classList.toggle('active', !!activeFilters[c.dataset.facet + '|' + c.dataset.code]); });
  onSkillSearch();
}

// ── SKILLS ───────────────────────────────────────────────
function onSkillSearch() {
  const q = document.getElementById('skillSearch').value.toLowerCase().trim();
  filteredSkills = data.skills.filter(s => {
    if (q) {
      const match = s.preferred_label.toLowerCase().includes(q) ||
        (s.alternative_labels || []).some(a => a.toLowerCase().includes(q)) ||
        s.skill_id.toLowerCase().includes(q) ||
        (s.unit_codes || []).some(c => c.toLowerCase().includes(q)) ||
        (s.qualifications || []).some(qq => qq.code.toLowerCase().includes(q) || qq.title.toLowerCase().includes(q)) ||
        (s.occupations || []).some(oo => oo.code.toLowerCase().includes(q) || oo.title.toLowerCase().includes(q));
      if (!match) return false;
    }
    for (const key of Object.keys(activeFilters)) {
      const [fid, code] = key.split('|');
      const fc = s.facets?.[fid]?.code;
      if (Array.isArray(fc)) { if (!fc.includes(code)) return false; }
      else { if (fc !== code) return false; }
    }
    return true;
  });
  resetSkillResults();
}

function resetSkillResults() {
  skillPage = 0;
  document.getElementById('skillResults').innerHTML = '';
  document.getElementById('skillResultsMeta').innerHTML = `Showing <b>${filteredSkills.length}</b> skills`;
  loadMoreSkills();
}

function loadMoreSkills() {
  const start = skillPage * PAGE_SIZE;
  const slice = filteredSkills.slice(start, start + PAGE_SIZE);
  const container = document.getElementById('skillResults');
  for (const s of slice) { container.insertAdjacentHTML('beforeend', skillCardHTML(s)); }
  skillPage++;
  document.getElementById('skillLoadMore').style.display = (start + PAGE_SIZE < filteredSkills.length) ? '' : 'none';
}

function skillCardHTML(s) {
  const ctxBadges = Object.entries(s.context_distribution || {}).map(([ctx, n]) => `<span class="badge badge-ctx badge-${CTX_CLASS[ctx] || 'hybrid'}">${ctx} ${n}</span>`).join('');
  const facetBadges = Object.entries(s.facets || {}).filter(([,v]) => v?.name).map(([,v]) => `<span class="badge badge-facet">${v.name}</span>`).join('');
  const altBadge = s.alternative_labels?.length ? `<span class="badge badge-alt">${s.alternative_labels.length} alt</span>` : '';
  const qualBadge = s.qualifications?.length ? `<span class="badge" style="background:#dcfce7;color:#166534">${s.qualifications.length} quals</span>` : '';
  const occBadge = s.occupations?.length ? `<span class="badge" style="background:#fff7ed;color:#9a3412">${s.occupations.length} occs</span>` : '';
  return `<div class="skill-card" onclick="openSkill('${s.skill_id}')">
    <div class="skill-card-name">${esc(s.preferred_label)}</div>
    ${s.definition ? `<div class="skill-card-def">${esc(s.definition)}</div>` : ''}
    <div class="skill-card-meta"><span class="badge badge-count">${s.assertion_count} assertions</span>${ctxBadges}${facetBadges}${altBadge}${qualBadge}${occBadge}</div>
  </div>`;
}

// ── UNITS ────────────────────────────────────────────────
function onUnitSearch() {
  const q = document.getElementById('unitSearch').value.toLowerCase().trim();
  filteredUnits = (data.units||[]).filter(u => !q || u.unit_code.toLowerCase().includes(q) || (u.unit_title||'').toLowerCase().includes(q));
  resetUnitResults();
}
function resetUnitResults() { unitPage = 0; document.getElementById('unitResults').innerHTML = ''; document.getElementById('unitResultsMeta').innerHTML = `Showing <b>${filteredUnits.length}</b> units`; loadMoreUnits(); }
function loadMoreUnits() {
  const start = unitPage * PAGE_SIZE; const slice = filteredUnits.slice(start, start + PAGE_SIZE);
  const container = document.getElementById('unitResults');
  for (const u of slice) {
    container.insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openUnit('${u.unit_code}')"><div class="unit-code">${esc(u.unit_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(u.unit_title||'')}</div><div class="unit-skill-count">${u.skill_count} skills${u.qualifications?.length ? ' · ' + u.qualifications.length + ' quals' : ''}</div></div>`);
  }
  unitPage++; document.getElementById('unitLoadMore').style.display = (start + PAGE_SIZE < filteredUnits.length) ? '' : 'none';
}

// ── QUALIFICATIONS ───────────────────────────────────────
function onQualSearch() {
  const q = document.getElementById('qualSearch').value.toLowerCase().trim();
  filteredQuals = (data.qualifications||[]).filter(qq => !q || qq.qualification_code.toLowerCase().includes(q) || qq.qualification_title.toLowerCase().includes(q));
  resetQualResults();
}
function resetQualResults() { qualPage = 0; document.getElementById('qualResults').innerHTML = ''; document.getElementById('qualResultsMeta').innerHTML = `Showing <b>${filteredQuals.length}</b> qualifications`; loadMoreQuals(); }
function loadMoreQuals() {
  const start = qualPage * PAGE_SIZE; const slice = filteredQuals.slice(start, start + PAGE_SIZE);
  const container = document.getElementById('qualResults');
  for (const q of slice) {
    container.insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openQual('${q.qualification_code}')"><div class="unit-code">${esc(q.qualification_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(q.qualification_title)}</div><div class="unit-skill-count">${q.skill_count} skills · ${q.unit_codes.length} units · ${q.occupation_codes.length} occupations</div></div>`);
  }
  qualPage++; document.getElementById('qualLoadMore').style.display = (start + PAGE_SIZE < filteredQuals.length) ? '' : 'none';
}

// ── OCCUPATIONS ──────────────────────────────────────────
function onOccSearch() {
  const q = document.getElementById('occSearch').value.toLowerCase().trim();
  filteredOccs = (data.occupations||[]).filter(o => !q || o.anzsco_code.toLowerCase().includes(q) || o.anzsco_title.toLowerCase().includes(q));
  resetOccResults();
}
function resetOccResults() { occPage = 0; document.getElementById('occResults').innerHTML = ''; document.getElementById('occResultsMeta').innerHTML = `Showing <b>${filteredOccs.length}</b> occupations`; loadMoreOccs(); }
function loadMoreOccs() {
  const start = occPage * PAGE_SIZE; const slice = filteredOccs.slice(start, start + PAGE_SIZE);
  const container = document.getElementById('occResults');
  for (const o of slice) {
    container.insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openOcc('${o.anzsco_code}')"><div class="unit-code">${esc(o.anzsco_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(o.anzsco_title)}</div><div class="unit-skill-count">${o.skill_count} skills · ${o.qualification_codes.length} qualifications</div></div>`);
  }
  occPage++; document.getElementById('occLoadMore').style.display = (start + PAGE_SIZE < filteredOccs.length) ? '' : 'none';
}

// ── DRAWER: Skill detail ─────────────────────────────────
function openSkill(sid) {
  const s = skillIndex.get(sid);
  if (!s) return;
  document.getElementById('drawerTitle').textContent = s.preferred_label;
  let html = '';

  if (s.definition) html += `<div class="d-section"><div class="d-label"><i class="bi bi-info-circle"></i> Definition</div><div class="d-def">${esc(s.definition)}</div></div>`;

  // Facets
  const fe = Object.entries(s.facets || {}).filter(([,v]) => v?.name);
  if (fe.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-tags"></i> Dimensions</div>`;
    for (const [fid, fv] of fe) { html += `<div class="facet-row"><span class="facet-dim">${FACET_NAMES[fid]||fid}</span><span class="facet-val">${esc(fv.name)}${fv.confidence ? ` <span style="opacity:.5;font-size:.7rem">${(fv.confidence*100).toFixed(0)}%</span>`:''}</span></div>`; }
    html += '</div>';
  }

  // Qualifications
  if (s.qualifications?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-award"></i> Qualifications (${s.qualifications.length})</div><div class="d-tags">`;
    s.qualifications.slice(0,15).forEach(q => { html += `<span class="d-tag" style="cursor:pointer;background:#dcfce7;color:#166534" onclick="openQual('${q.code}')" title="${esc(q.title)}">${esc(q.code)} ${esc(q.title).substring(0,30)}${q.title.length>30?'...':''}</span>`; });
    if (s.qualifications.length > 15) html += `<span class="d-tag" style="opacity:.6">+${s.qualifications.length-15} more</span>`;
    html += '</div></div>';
  }

  // Occupations
  if (s.occupations?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-person-badge"></i> Occupations (${s.occupations.length})</div><div class="d-tags">`;
    s.occupations.slice(0,15).forEach(o => { html += `<span class="d-tag" style="cursor:pointer;background:#fff7ed;color:#9a3412" onclick="openOcc('${o.code}')" title="${esc(o.title)}">${esc(o.code)} ${esc(o.title).substring(0,30)}${o.title.length>30?'...':''}</span>`; });
    if (s.occupations.length > 15) html += `<span class="d-tag" style="opacity:.6">+${s.occupations.length-15} more</span>`;
    html += '</div></div>';
  }

  // Alt labels
  if (s.alternative_labels?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-card-heading"></i> Alternative Labels (${s.alternative_labels.length})</div><div class="d-tags">`;
    s.alternative_labels.forEach(a => { html += `<span class="d-tag">${esc(a)}</span>`; });
    html += '</div></div>';
  }

  // Context distribution
  const ctxE = Object.entries(s.context_distribution || {});
  if (ctxE.length) {
    const total = ctxE.reduce((a,[,n])=>a+n,0);
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-bar-chart"></i> Teaching Context</div>`;
    for (const [ctx,n] of ctxE) { const p=(n/total*100).toFixed(1); html += `<div class="dist-row"><span class="dist-label">${ctx}</span><div class="dist-bar-track"><div class="dist-bar-fill ${CTX_CLASS[ctx]||'hybrid'}" style="width:${p}%"></div></div><span class="dist-val">${n}</span></div>`; }
    html += '</div>';
  }

  // Level distribution
  const lvlE = Object.entries(s.level_distribution || {}).sort();
  if (lvlE.length) {
    const total = lvlE.reduce((a,[,n])=>a+n,0);
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-layers"></i> Level of Engagement</div>`;
    for (const [l,n] of lvlE) { const p=(n/total*100).toFixed(1); html += `<div class="dist-row"><span class="dist-label">${l}</span><div class="dist-bar-track"><div class="dist-bar-fill level" style="width:${p}%"></div></div><span class="dist-val">${n}</span></div>`; }
    html += '</div>';
  }

  // Unit codes
  if (s.unit_codes?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-journal-code"></i> Units (${s.unit_codes.length})</div><div class="d-tags">`;
    s.unit_codes.slice(0,30).forEach(c => { html += `<span class="d-tag code" style="cursor:pointer" onclick="openUnit('${c}')">${c}</span>`; });
    if (s.unit_codes.length > 30) html += `<span class="d-tag" style="opacity:.6">+${s.unit_codes.length-30} more</span>`;
    html += '</div></div>';
  }

  // Assertions table
  if (s.assertions?.length) {
    const show = s.assertions.slice(0,20);
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-link-45deg"></i> Assertions (${s.assertions.length})</div>`;
    html += `<table class="a-table"><thead><tr><th>Unit</th><th>Context</th><th>Level</th><th>Quals</th><th>Occs</th><th>Evidence</th></tr></thead><tbody>`;
    for (const a of show) {
      const cls=CTX_CLASS[a.teaching_context]||'hybrid';
      const qCodes = (a.qualification_codes||[]).join(', ');
      const oCodes = (a.occupation_codes||[]).join(', ');
      html += `<tr><td><span class="d-tag code" style="cursor:pointer" onclick="openUnit('${a.unit_code}')">${a.unit_code}</span></td><td><span class="a-ctx-dot ${cls}"></span>${a.teaching_context}</td><td>${a.level_of_engagement}</td><td style="font-size:.7rem;max-width:100px" title="${esc(qCodes)}">${esc(qCodes.substring(0,20))}${qCodes.length>20?'…':''}</td><td style="font-size:.7rem;max-width:100px" title="${esc(oCodes)}">${esc(oCodes.substring(0,20))}${oCodes.length>20?'…':''}</td><td class="a-evidence" title="${esc(a.evidence)}">${esc(a.evidence)}</td></tr>`;
    }
    html += '</tbody></table>';
    if (s.assertions.length > 20) html += `<div style="text-align:center;margin-top:8px;font-size:.78rem;color:var(--c-text3)">Showing 20 of ${s.assertions.length}</div>`;
    html += '</div>';
  }

  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

// ── DRAWER: Unit detail ──────────────────────────────────
function openUnit(code) {
  const u = unitIndex.get(code);
  if (!u) return;
  document.getElementById('drawerTitle').textContent = u.unit_title ? `${code} — ${u.unit_title}` : code;
  let html = '';
  if (u.qualifications?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-award"></i> Qualifications (${u.qualifications.length})</div><div class="d-tags">`;
    u.qualifications.forEach(q => { html += `<span class="d-tag" style="cursor:pointer;background:#dcfce7;color:#166534" onclick="openQual('${q.code}')">${esc(q.code)} ${esc(q.title).substring(0,35)}</span>`; });
    html += '</div></div>';
  }
  html += `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${u.skill_ids.length})</div><div class="d-tags">`;
  for (const sid of u.skill_ids) { const s = skillIndex.get(sid); html += `<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`; }
  html += '</div></div>';
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

// ── DRAWER: Qualification detail ─────────────────────────
function openQual(code) {
  const q = qualIndex.get(code);
  if (!q) return;
  document.getElementById('drawerTitle').textContent = `${code} — ${q.qualification_title}`;
  let html = '';
  if (q.occupation_codes?.length) {
    html += `<div class="d-section"><div class="d-label"><i class="bi bi-person-badge"></i> ANZSCO Occupations (${q.occupation_codes.length})</div><div class="d-tags">`;
    q.occupation_codes.forEach(ac => { const o = occIndex.get(ac); html += `<span class="d-tag" style="cursor:pointer;background:#fff7ed;color:#9a3412" onclick="openOcc('${ac}')">${ac} ${esc(o?o.anzsco_title:'')}</span>`; });
    html += '</div></div>';
  }
  html += `<div class="d-section"><div class="d-label"><i class="bi bi-journal-code"></i> Units (${q.unit_codes.length})</div><div class="d-tags">`;
  q.unit_codes.slice(0,40).forEach(uc => { html += `<span class="d-tag code" style="cursor:pointer" onclick="openUnit('${uc}')">${uc}</span>`; });
  if (q.unit_codes.length > 40) html += `<span class="d-tag" style="opacity:.6">+${q.unit_codes.length-40}</span>`;
  html += '</div></div>';
  html += `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${q.skill_ids.length})</div><div class="d-tags">`;
  q.skill_ids.slice(0,40).forEach(sid => { const s = skillIndex.get(sid); html += `<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`; });
  if (q.skill_ids.length > 40) html += `<span class="d-tag" style="opacity:.6">+${q.skill_ids.length-40}</span>`;
  html += '</div></div>';
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

// ── DRAWER: Occupation detail ────────────────────────────
function openOcc(code) {
  const o = occIndex.get(code);
  if (!o) return;
  document.getElementById('drawerTitle').textContent = `${code} — ${o.anzsco_title}`;
  let html = '';
  html += `<div class="d-section"><div class="d-label"><i class="bi bi-award"></i> Qualifications (${o.qualification_codes.length})</div><div class="d-tags">`;
  o.qualification_codes.forEach(qc => { const q = qualIndex.get(qc); html += `<span class="d-tag" style="cursor:pointer;background:#dcfce7;color:#166534" onclick="openQual('${qc}')">${qc} ${esc(q?q.qualification_title:'')}</span>`; });
  html += '</div></div>';
  html += `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${o.skill_ids.length})</div><div class="d-tags">`;
  o.skill_ids.slice(0,50).forEach(sid => { const s = skillIndex.get(sid); html += `<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`; });
  if (o.skill_ids.length > 50) html += `<span class="d-tag" style="opacity:.6">+${o.skill_ids.length-50}</span>`;
  html += '</div></div>';
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

// ── Drawer toggle ────────────────────────────────────────
function showDrawer() { document.getElementById('drawer').classList.remove('hidden'); document.getElementById('drawerOverlay').classList.remove('hidden'); }
function closeDrawer() { document.getElementById('drawer').classList.add('hidden'); document.getElementById('drawerOverlay').classList.add('hidden'); }

// ── Tabs ─────────────────────────────────────────────────
function onTabClick(e) {
  const tab = e.currentTarget.dataset.tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  ['skills','units','quals','occs','matrix'].forEach(p => { document.getElementById(p+'Panel').classList.toggle('hidden', p !== tab); });
  if (tab === 'matrix' && !matrixInitialized) initMatrix();
}

function esc(s) { if (!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }

// ══════════════════════════════════════════════════════════
//  SANKEY: Skill → Assertion → Unit → Qual → Occ (5 columns)
//  One assertion node per unique (context, level) per skill
//  Multiple flows out from one assertion to different units
// ══════════════════════════════════════════════════════════
let matrixInitialized = false;
const CTX_CLS = { PRACTICAL:'prac', THEORETICAL:'theo', HYBRID:'hybrid' };
const CTX_COL = { PRACTICAL:'#16a34a', THEORETICAL:'#2563ab', HYBRID:'#7c3aed' };
const SANKEY_COLORS = { skill:'#0f6b5e', assertion:'#6d28d9', unit:'#2563ab', qual:'#16a34a', occ:'#dc6b16' };

function initMatrix() {
  matrixInitialized = true;
  document.getElementById('matrixSearch').addEventListener('input', debounce(onMatrixSearch, 300));
}

function onMatrixSearch() {
  const q = document.getElementById('matrixSearch').value.toLowerCase().trim();
  document.getElementById('matrixDetail').innerHTML = '';
  if (q.length < 2) { document.getElementById('matrixContainer').innerHTML = ''; document.getElementById('matrixHint').textContent = 'Type at least 2 characters'; return; }

  let skills = [];
  const ms = data.skills.filter(s => s.preferred_label.toLowerCase().includes(q) || s.skill_id.toLowerCase().includes(q) || (s.alternative_labels||[]).some(a=>a.toLowerCase().includes(q)));
  if (ms.length) skills = ms.slice(0,6);
  if (!skills.length) { const mq = (data.qualifications||[]).find(x => x.qualification_code.toLowerCase().includes(q) || x.qualification_title.toLowerCase().includes(q)); if (mq) skills = mq.skill_ids.map(sid => skillIndex.get(sid)).filter(Boolean).slice(0,10); }
  if (!skills.length) { const mo = (data.occupations||[]).find(x => x.anzsco_code.toLowerCase().includes(q) || x.anzsco_title.toLowerCase().includes(q)); if (mo) skills = mo.skill_ids.map(sid => skillIndex.get(sid)).filter(Boolean).slice(0,10); }
  if (!skills.length) { const mu = (data.units||[]).find(x => x.unit_code.toLowerCase().includes(q) || (x.unit_title||'').toLowerCase().includes(q)); if (mu) skills = (mu.skill_ids||[]).map(sid => skillIndex.get(sid)).filter(Boolean).slice(0,10); }

  if (!skills.length) { document.getElementById('matrixHint').textContent = 'No match found'; document.getElementById('matrixContainer').innerHTML = ''; return; }
  document.getElementById('matrixHint').textContent = '';
  renderSankey(skills);
}

function renderSankey(skills) {
  const skillNodes=[], assertNodes=[], unitNodes=[], qualNodes=[], occNodes=[];
  const skillSet=new Set(), assertSet=new Set(), unitSet=new Set(), qualSet=new Set(), occSet=new Set();
  const flows_sa=[], flows_au=[], flows_uq=[], flows_qo=[];

  skills.forEach(s => {
    if (skillSet.has(s.skill_id)) return;
    skillSet.add(s.skill_id);
    skillNodes.push({ id:s.skill_id, label:s.preferred_label });

    // Group by (context, level, unit) per skill — each unit gets its own assertion node
    const grouped = {};
    (s.assertions||[]).forEach(a => {
      const key = s.skill_id + '|' + a.teaching_context + '|' + a.level_of_engagement + '|' + a.unit_code;
      if (!grouped[key]) grouped[key] = { ctx:a.teaching_context, lvl:a.level_of_engagement, unitCode:a.unit_code, evidence:'' };
      if (!grouped[key].evidence && a.evidence) grouped[key].evidence = a.evidence;
    });

    for (const [key, g] of Object.entries(grouped)) {
      const aId = 'AG_' + key.replace(/[^a-zA-Z0-9]/g, '_');
      if (!assertSet.has(aId)) {
        assertSet.add(aId);
        assertNodes.push({ id:aId, ctx:g.ctx, lvl:g.lvl, color:CTX_COL[g.ctx]||'#999', evidence:g.evidence });
      }
      // One flow: skill → this assertion node
      if (!flows_sa.find(f=>f.from===s.skill_id&&f.to===aId)) flows_sa.push({ from:s.skill_id, to:aId });

      // One flow: assertion node → its unit
      const uc = g.unitCode;
      if (!unitSet.has(uc)) {
        unitSet.add(uc);
        const u = unitIndex.get(uc);
        unitNodes.push({ id:uc, code:uc, label:u?(u.unit_title||'').substring(0,32):'', fullTitle:u?(u.unit_title||''):'' });
      }
      if (!flows_au.find(f=>f.from===aId&&f.to===uc)) flows_au.push({ from:aId, to:uc });

      // Unit → Quals
      const u = unitIndex.get(uc);
      (u?.qualification_codes||[]).forEach(qc => {
        if (!qualSet.has(qc)) { qualSet.add(qc); const q=qualIndex.get(qc); qualNodes.push({ id:qc, code:qc, label:q?q.qualification_title.substring(0,30):'', fullTitle:q?q.qualification_title:'' }); }
        if (!flows_uq.find(f=>f.from===uc&&f.to===qc)) flows_uq.push({ from:uc, to:qc });
      });
    }
  });

  // Qual → Occ
  qualNodes.forEach(qn => {
    const q = qualIndex.get(qn.id);
    (q?.occupation_codes||[]).forEach(ac => {
      if (!occSet.has(ac)) { occSet.add(ac); const o=occIndex.get(ac); occNodes.push({ id:ac, code:ac, label:o?o.anzsco_title.substring(0,30):'', fullTitle:o?o.anzsco_title:'' }); }
      if (!flows_qo.find(f=>f.from===qn.id&&f.to===ac)) flows_qo.push({ from:qn.id, to:ac });
    });
  });

  // ── Layout (fill container width) ───────────────────────
  const container = document.getElementById('matrixContainer');
  const W = container.clientWidth || 1100;
  const PAD=12, GAP=36;
  const totalGap = PAD*2 + GAP*4;
  const colSpace = W - totalGap;
  // Proportional column widths — all space goes to columns
  const ratios = [1, 0.8, 1.15, 1.15, 1];
  const ratioSum = ratios.reduce((a,b)=>a+b,0);
  const CW = ratios.map(r => Math.floor(colSpace * r / ratioSum));
  const colX=[PAD];
  for(let i=1;i<5;i++) colX.push(colX[i-1]+CW[i-1]+GAP);

  const NH=36, AH=48, NG=5;
  const allCols = [
    { nodes:skillNodes, h:NH, color:SANKEY_COLORS.skill },
    { nodes:assertNodes, h:AH, color:SANKEY_COLORS.assertion },
    { nodes:unitNodes, h:NH, color:SANKEY_COLORS.unit },
    { nodes:qualNodes, h:NH, color:SANKEY_COLORS.qual },
    { nodes:occNodes, h:NH, color:SANKEY_COLORS.occ },
  ];

  const colHeights = allCols.map(c => c.nodes.length*(c.h+NG));
  const maxH = Math.max(...colHeights, 200);
  const H = maxH + 80;

  const nodePos = {};
  allCols.forEach((col, ci) => {
    const totalH = col.nodes.length*(col.h+NG);
    const y0 = Math.max(50, (H-totalH)/2);
    col.nodes.forEach((n,i) => {
      const c = n.color || col.color;
      nodePos[n.id] = { x:colX[ci], y:y0+i*(col.h+NG), w:CW[ci], h:col.h, color:c };
    });
  });

  // ── SVG ────────────────────────────────────────────────
  let svg = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" style="font-family:DM Sans,sans-serif;user-select:none">`;
  svg += `<defs><linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="0">`;
  svg += `<stop offset="0%" stop-color="#f0fdf4" stop-opacity="0.35"/><stop offset="20%" stop-color="#f5f3ff" stop-opacity="0.35"/>`;
  svg += `<stop offset="40%" stop-color="#eff6ff" stop-opacity="0.35"/><stop offset="70%" stop-color="#f0fdf4" stop-opacity="0.35"/>`;
  svg += `<stop offset="100%" stop-color="#fff7ed" stop-opacity="0.35"/></linearGradient></defs>`;
  svg += `<rect width="${W}" height="${H}" fill="url(#bgGrad)" rx="8"/>`;

  // Column headers
  const hdrLabels = ['SKILLS','ASSERTIONS','UNITS','QUALIFICATIONS','OCCUPATIONS'];
  const hdrColors = [SANKEY_COLORS.skill, SANKEY_COLORS.assertion, SANKEY_COLORS.unit, SANKEY_COLORS.qual, SANKEY_COLORS.occ];
  hdrLabels.forEach((lbl,i) => {
    svg += `<text x="${colX[i]+CW[i]/2}" y="24" text-anchor="middle" font-size="9.5" font-weight="700" fill="${hdrColors[i]}" letter-spacing="0.5">${lbl}</text>`;
    svg += `<line x1="${colX[i]}" y1="33" x2="${colX[i]+CW[i]}" y2="33" stroke="${hdrColors[i]}" stroke-width="2" stroke-opacity="0.2"/>`;
  });

  // ── Flows (with data-from/data-to for highlighting) ─────
  let flowIdx = 0;
  function drawFlow(from, to, color) {
    const s=nodePos[from], t=nodePos[to];
    if(!s||!t) return;
    const x1=s.x+s.w, y1=s.y+s.h/2, x2=t.x, y2=t.y+t.h/2;
    svg += `<path class="sk-flow" data-from="${from}" data-to="${to}" d="M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}" fill="none" stroke="${color}" stroke-width="2" stroke-opacity="0.22" stroke-linecap="round"/>`;
  }
  flows_sa.forEach(f => drawFlow(f.from, f.to, SANKEY_COLORS.skill));
  flows_au.forEach(f => { const a=nodePos[f.from]; drawFlow(f.from, f.to, a?a.color:'#999'); });
  flows_uq.forEach(f => drawFlow(f.from, f.to, SANKEY_COLORS.unit));
  flows_qo.forEach(f => drawFlow(f.from, f.to, SANKEY_COLORS.qual));

  // ── Skill nodes ────────────────────────────────────────
  skillNodes.forEach(n => {
    const p=nodePos[n.id];
    svg += `<g class="sk-node" data-nid="${n.id}" style="cursor:pointer" onclick="sankeyNodeClick('${n.id}')" onmouseenter="sankeyHighlight('${n.id}')" onmouseleave="sankeyClear()">`;
    svg += `<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="6" fill="${p.color}" fill-opacity="0.1" stroke="${p.color}" stroke-width="1.5"/>`;
    svg += `<text x="${p.x+8}" y="${p.y+p.h/2+4}" font-size="10" fill="${p.color}" font-weight="600" pointer-events="none">${esc(n.label.substring(0,28))}</text>`;
    svg += `</g>`;
  });

  // ── Assertion nodes ────────────────────────────────────
  assertNodes.forEach(n => {
    const p=nodePos[n.id], col=n.color;
    const evMaxChars = Math.floor(p.w / 5.5);
    const evText = n.evidence ? n.evidence.substring(0, evMaxChars) + (n.evidence.length > evMaxChars ? '…' : '') : '';
    svg += `<g class="sk-node" data-nid="${n.id}" onmouseenter="sankeyHighlight('${n.id}')" onmouseleave="sankeyClear()">`;
    svg += `<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="6" fill="${col}" fill-opacity="0.1" stroke="${col}" stroke-width="1.5"/>`;
    svg += `<circle cx="${p.x+11}" cy="${p.y+14}" r="4" fill="${col}"/>`;
    svg += `<text x="${p.x+19}" y="${p.y+17}" font-size="9" fill="${col}" font-weight="700" pointer-events="none">${n.ctx}</text>`;
    svg += `<text x="${p.x+p.w-8}" y="${p.y+17}" text-anchor="end" font-size="8.5" fill="#5a6072" font-weight="500" pointer-events="none">${n.lvl}</text>`;
    if (evText) svg += `<text x="${p.x+8}" y="${p.y+33}" font-size="7.5" fill="#8892a4" font-style="italic" pointer-events="none">${esc(evText)}</text>`;
    if (n.evidence) svg += `<title>${esc(n.evidence)}</title>`;
    svg += `</g>`;
  });

  // ── Unit / Qual / Occ nodes ────────────────────────────
  function drawCodeNode(n) {
    const p=nodePos[n.id];
    const tip = n.code + (n.fullTitle ? ' \u2014 ' + n.fullTitle : '');
    svg += `<g class="sk-node" data-nid="${n.id}" style="cursor:pointer" onclick="sankeyNodeClick('${n.id}')" onmouseenter="sankeyHighlight('${n.id}')" onmouseleave="sankeyClear()">`;
    svg += `<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="6" fill="${p.color}" fill-opacity="0.1" stroke="${p.color}" stroke-width="1.5"/>`;
    svg += `<text x="${p.x+8}" y="${p.y+13}" font-size="9.5" fill="${p.color}" font-weight="700" pointer-events="none">${esc(n.code)}</text>`;
    svg += `<text x="${p.x+8}" y="${p.y+25}" font-size="7.5" fill="#6b7785" pointer-events="none">${esc(n.label)}</text>`;
    svg += `<title>${esc(tip)}</title></g>`;
  }
  unitNodes.forEach(drawCodeNode);
  qualNodes.forEach(drawCodeNode);
  occNodes.forEach(drawCodeNode);

  svg += '</svg>';
  document.getElementById('matrixContainer').innerHTML = svg;

  // ── Build adjacency for path tracing ───────────────────
  window._sankeyAdj = { fwd:{}, rev:{} };
  const allFlows = [...flows_sa, ...flows_au, ...flows_uq, ...flows_qo];
  allFlows.forEach(f => {
    if (!window._sankeyAdj.fwd[f.from]) window._sankeyAdj.fwd[f.from] = [];
    window._sankeyAdj.fwd[f.from].push(f.to);
    if (!window._sankeyAdj.rev[f.to]) window._sankeyAdj.rev[f.to] = [];
    window._sankeyAdj.rev[f.to].push(f.from);
  });
}

function sankeyNodeClick(id) {
  if (skillIndex.has(id)) openSkill(id);
  else if (qualIndex.has(id)) openQual(id);
  else if (occIndex.has(id)) openOcc(id);
  else if (unitIndex.has(id)) openUnit(id);
}

function sankeyHighlight(nodeId) {
  // Trace full path: walk forward and backward from this node
  const adj = window._sankeyAdj;
  if (!adj) return;
  const connected = new Set();
  connected.add(nodeId);

  // Walk forward (right)
  function walkFwd(id) {
    (adj.fwd[id]||[]).forEach(nxt => { if (!connected.has(nxt)) { connected.add(nxt); walkFwd(nxt); } });
  }
  // Walk backward (left)
  function walkRev(id) {
    (adj.rev[id]||[]).forEach(prev => { if (!connected.has(prev)) { connected.add(prev); walkRev(prev); } });
  }
  walkFwd(nodeId);
  walkRev(nodeId);

  // Dim all nodes and flows, then highlight connected ones
  const container = document.getElementById('matrixContainer');
  if (!container) return;

  container.querySelectorAll('.sk-node').forEach(el => {
    const nid = el.dataset.nid;
    if (connected.has(nid)) {
      el.style.opacity = '1';
    } else {
      el.style.opacity = '0.15';
    }
  });

  container.querySelectorAll('.sk-flow').forEach(el => {
    const from = el.dataset.from, to = el.dataset.to;
    if (connected.has(from) && connected.has(to)) {
      el.style.strokeOpacity = '0.55';
      el.style.strokeWidth = '3';
    } else {
      el.style.strokeOpacity = '0.05';
      el.style.strokeWidth = '1';
    }
  });
}

function sankeyClear() {
  const container = document.getElementById('matrixContainer');
  if (!container) return;
  container.querySelectorAll('.sk-node').forEach(el => { el.style.opacity = ''; });
  container.querySelectorAll('.sk-flow').forEach(el => { el.style.strokeOpacity = ''; el.style.strokeWidth = ''; });
}

function showAssertionDetail(skillId, unitCode) {
  const s = skillIndex.get(skillId); if (!s) return;
  const a = (s.assertions||[]).find(x => x.unit_code === unitCode); if (!a) return;
  const u = unitIndex.get(unitCode);
  const cls = CTX_CLS[a.teaching_context] || 'hybrid';
  document.getElementById('matrixDetail').innerHTML = `
    <div class="assertion-detail-card">
      <h4><i class="bi bi-link-45deg" style="color:var(--c-accent)"></i> Assertion Detail</h4>
      <div class="assertion-meta-row">
        <span class="assertion-meta-item"><b>Skill:</b> <span style="cursor:pointer;color:var(--c-accent)" onclick="openSkill('${skillId}')">${esc(s.preferred_label)}</span></span>
        <span class="assertion-meta-item"><b>Unit:</b> <span style="cursor:pointer;color:var(--c-accent)" onclick="openUnit('${unitCode}')">${esc(unitCode)}</span> ${esc(u?u.unit_title:'')}</span>
      </div>
      <div class="assertion-meta-row">
        <span class="assertion-meta-item"><b>Context:</b> <span class="a-ctx-dot ${cls}" style="display:inline-block"></span> ${a.teaching_context}</span>
        <span class="assertion-meta-item"><b>Level:</b> ${a.level_of_engagement}</span>
      </div>
      ${a.evidence ? `<div class="assertion-evidence">${esc(a.evidence)}</div>` : ''}
    </div>`;
}
"""
