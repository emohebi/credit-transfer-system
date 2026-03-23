"""
Generate an HTML-based search engine for the Skill Assertion schema.

Features:
  - Full-text search across skills, units, alternative labels
  - Lazy-loaded skill detail panels with assertions
  - Facet filters
  - Context/level distribution bars
  - Unit → Skill reverse lookup
  - Ability Archetypes with progression ladders (NEW)
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
          <p class="hdr-sub">Search skills, view teaching context, explore unit linkages and ability archetypes</p>
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
      <button class="tab" data-tab="archetypes"><i class="bi bi-bar-chart-steps"></i> Archetypes</button>
      <button class="tab" data-tab="matrix"><i class="bi bi-water"></i> Sankey Flow</button>
      <button class="tab" data-tab="unitasced"><i class="bi bi-diagram-2"></i> Unit-First</button>
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
        <div class="search-box"><i class="bi bi-search"></i><input type="text" id="unitSearch" placeholder="Search unit codes or titles…" autocomplete="off"></div>
      </div>
      <div class="results-meta" id="unitResultsMeta"></div>
      <div class="results-grid" id="unitResults"></div>
      <div class="load-more-wrap" id="unitLoadMore" style="display:none"><button class="btn-load" onclick="loadMoreUnits()">Load more</button></div>
    </section>

    <!-- Qualifications Tab -->
    <section class="panel hidden" id="qualsPanel">
      <div class="search-row">
        <div class="search-box"><i class="bi bi-search"></i><input type="text" id="qualSearch" placeholder="Search qualification codes or titles…" autocomplete="off"></div>
      </div>
      <div class="results-meta" id="qualResultsMeta"></div>
      <div class="results-grid" id="qualResults"></div>
      <div class="load-more-wrap" id="qualLoadMore" style="display:none"><button class="btn-load" onclick="loadMoreQuals()">Load more</button></div>
    </section>

    <!-- Occupations Tab -->
    <section class="panel hidden" id="occsPanel">
      <div class="search-row">
        <div class="search-box"><i class="bi bi-search"></i><input type="text" id="occSearch" placeholder="Search ANZSCO codes or titles…" autocomplete="off"></div>
      </div>
      <div class="results-meta" id="occResultsMeta"></div>
      <div class="results-grid" id="occResults"></div>
      <div class="load-more-wrap" id="occLoadMore" style="display:none"><button class="btn-load" onclick="loadMoreOccs()">Load more</button></div>
    </section>

    <!-- Archetypes Tab (NEW) -->
    <section class="panel hidden" id="archetypesPanel">
      <div id="archContent"><p style="color:#8892a4;padding:20px;">Loading archetypes...</p></div>
    </section>

    <!-- Sankey Flow Tab -->
    <section class="panel hidden" id="matrixPanel">
      <div class="matrix-controls">
        <div class="search-box" style="flex:1;min-width:260px"><i class="bi bi-search"></i><input type="text" id="matrixSearch" placeholder="Search a skill, unit, qualification or occupation…" autocomplete="off"></div>
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

    <!-- Unit-First Tab -->
    <section class="panel hidden" id="unitascedPanel">
      <div class="matrix-controls">
        <div class="search-box" style="flex:1;min-width:260px"><i class="bi bi-search"></i><input type="text" id="uaSearch" placeholder="Search a unit code or title…" autocomplete="off"></div>
        <div class="matrix-legend">
          <span class="legend-dot" style="background:#2563ab"></span> Unit
          <span class="legend-dot" style="background:#6d28d9"></span> Assertion
          <span class="legend-dot" style="background:#0f6b5e"></span> Skill
          <span class="legend-dot" style="background:#16a34a"></span> Qualification
          <span class="legend-dot" style="background:#dc6b16"></span> Occupation
        </div>
      </div>
      <div id="uaHint" class="graph-hint">Search for a unit to see its skills and where they lead</div>
      <div id="uaContainer" style="overflow-x:auto"></div>
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
  --c-bg: #f4f6f9; --c-surface: #ffffff; --c-border: #e2e6ed;
  --c-text: #1a1f36; --c-text2: #5a6072; --c-text3: #8892a4;
  --c-accent: #0f6b5e; --c-accent-light: #e8f5f1; --c-accent2: #1e3a5f;
  --c-tag-bg: #eef1f6; --c-tag-text: #3d4663;
  --c-prac: #0d7c3e; --c-theo: #2563ab; --c-hybrid: #7c3aed;
  --radius: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.1);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DM Sans', sans-serif; background: var(--c-bg); color: var(--c-text); line-height: 1.55; }

.hdr { background: linear-gradient(135deg, var(--c-accent2) 0%, #0d2137 100%); color: #fff; }
.hdr-inner { max-width: 1280px; margin: 0 auto; padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.hdr-brand { display: flex; align-items: center; gap: 14px; }
.hdr-icon { width: 42px; height: 42px; background: var(--c-accent); border-radius: 10px; display: grid; place-items: center; font-size: 1.2rem; }
.hdr h1 { font-size: 1.35rem; font-weight: 700; letter-spacing: -.02em; }
.hdr-sub { font-size: .82rem; opacity: .75; font-weight: 400; }
.hdr-stats { display: flex; gap: 20px; font-size: .8rem; opacity: .85; }
.hdr-stat b { font-weight: 600; }

.shell { max-width: 1280px; margin: 0 auto; padding: 0 24px 60px; }
.tabs { display: flex; gap: 4px; margin-top: 20px; margin-bottom: 0; flex-wrap: wrap; }
.tab { padding: 10px 20px; background: transparent; border: none; font: inherit; font-weight: 500; font-size: .88rem; color: var(--c-text3); cursor: pointer; border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 6px; }
.tab:hover { color: var(--c-text); }
.tab.active { color: var(--c-accent); border-bottom-color: var(--c-accent); }

.panel { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: 0 0 var(--radius) var(--radius); padding: 20px; min-height: 400px; }
.panel.hidden { display: none; }

.search-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
.search-box { flex: 1; min-width: 280px; position: relative; }
.search-box i { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--c-text3); }
.search-box input { width: 100%; padding: 11px 14px 11px 40px; border: 2px solid var(--c-border); border-radius: var(--radius); font: inherit; font-size: .92rem; }
.search-box input:focus { outline: none; border-color: var(--c-accent); }

.filter-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 20px; font-size: .78rem; font-weight: 500; cursor: pointer; border: 1.5px solid var(--c-border); background: var(--c-surface); color: var(--c-text2); transition: all .15s; }
.chip:hover { border-color: var(--c-accent); color: var(--c-accent); }
.chip.active { background: var(--c-accent-light); border-color: var(--c-accent); color: var(--c-accent); }

.results-meta { font-size: .82rem; color: var(--c-text3); margin-bottom: 12px; }
.results-meta b { color: var(--c-accent); }
.results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }

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

.unit-card { background: var(--c-surface); border: 1.5px solid var(--c-border); border-radius: var(--radius); padding: 14px; cursor: pointer; transition: all .15s; }
.unit-card:hover { border-color: var(--c-accent); }
.unit-code { font-family: 'JetBrains Mono', monospace; font-size: .88rem; font-weight: 600; color: var(--c-accent2); }
.unit-skill-count { font-size: .78rem; color: var(--c-text3); margin-top: 4px; }

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

.d-section { margin-bottom: 20px; }
.d-label { font-size: .72rem; font-weight: 600; color: var(--c-text3); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.d-def { font-size: .88rem; color: var(--c-text2); line-height: 1.6; padding: 12px; background: var(--c-bg); border-radius: 8px; }
.d-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.d-tag { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: .75rem; background: var(--c-tag-bg); color: var(--c-tag-text); }
.d-tag.code { font-family: 'JetBrains Mono', monospace; font-size: .7rem; background: #e8eaf6; color: #3949ab; }

.dist-row { display: flex; align-items: center; margin-bottom: 6px; }
.dist-label { width: 100px; font-size: .78rem; color: var(--c-text2); font-weight: 500; }
.dist-bar-track { flex: 1; height: 18px; background: var(--c-bg); border-radius: 4px; overflow: hidden; margin: 0 8px; }
.dist-bar-fill { height: 100%; border-radius: 4px; transition: width .3s; }
.dist-bar-fill.prac { background: #86efac; }
.dist-bar-fill.theo { background: #93c5fd; }
.dist-bar-fill.hybrid { background: #c4b5fd; }
.dist-bar-fill.level { background: var(--c-accent); opacity: .7; }
.dist-val { width: 36px; text-align: right; font-size: .78rem; font-weight: 600; color: var(--c-text); }

.a-table { width: 100%; border-collapse: collapse; font-size: .8rem; }
.a-table th { text-align: left; padding: 8px 6px; font-size: .7rem; text-transform: uppercase; letter-spacing: .5px; color: var(--c-text3); border-bottom: 2px solid var(--c-border); }
.a-table td { padding: 8px 6px; border-bottom: 1px solid var(--c-border); vertical-align: top; }
.a-table tr:hover td { background: var(--c-bg); }
.a-evidence { font-size: .75rem; color: var(--c-text2); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.a-ctx-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.a-ctx-dot.prac { background: var(--c-prac); }
.a-ctx-dot.theo { background: var(--c-theo); }
.a-ctx-dot.hybrid { background: var(--c-hybrid); }

.facet-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--c-bg); }
.facet-row:last-child { border-bottom: none; }
.facet-dim { font-size: .78rem; color: var(--c-text2); }
.facet-val { font-size: .78rem; font-weight: 600; color: var(--c-text); }

.err { color: #c62828; padding: 20px; font-size: .9rem; }

.matrix-controls { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
.graph-legend, .matrix-legend { display: flex; gap: 14px; align-items: center; font-size: .78rem; color: var(--c-text2); flex-wrap: wrap; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 3px; }
.graph-hint { text-align: center; margin-top: 12px; font-size: .82rem; color: var(--c-text3); }

.sk-node { transition: opacity .2s ease; }
.sk-flow { transition: stroke-opacity .2s ease, stroke-width .2s ease; }

.assertion-detail-card { background: var(--c-bg); border-radius: var(--radius); padding: 16px; border: 1px solid var(--c-border); animation: fadeIn .15s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.assertion-detail-card h4 { font-size: .9rem; color: var(--c-accent2); margin-bottom: 10px; }
.assertion-meta-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }
.assertion-meta-item { font-size: .8rem; }
.assertion-meta-item b { color: var(--c-text); }
.assertion-evidence { font-size: .82rem; color: var(--c-text2); padding: 10px; background: white; border-radius: 6px; margin-top: 8px; line-height: 1.5; border-left: 3px solid var(--c-accent); }

/* ═══════════════════════════════════════════════════════════
   ARCHETYPE EXPLORER STYLES
   ═══════════════════════════════════════════════════════════ */
.arch-layout { display: grid; grid-template-columns: 320px 1fr 420px; gap: 20px; min-height: 450px; align-items: start; }
.arch-sidebar { border-right: 1px solid var(--c-border); padding-right: 20px; }
.arch-search input { width: 100%; padding: 10px 12px; border: 2px solid var(--c-border); border-radius: var(--radius); font: inherit; font-size: .9rem; margin-bottom: 14px; }
.arch-search input:focus { outline: none; border-color: var(--c-accent); }
.arch-card { background: var(--c-bg); border-radius: var(--radius); padding: 12px; margin-bottom: 10px; cursor: pointer; border: 2px solid transparent; transition: all .15s; }
.arch-card:hover { background: #e8ecf1; }
.arch-card.active { border-color: var(--c-accent); background: var(--c-accent-light); }
.arch-card-label { font-weight: 600; color: var(--c-accent2); font-size: .85rem; margin-bottom: 6px; }
.arch-card-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }
.arch-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: .68rem; font-weight: 600; }
.arch-badge-nat { background: #fff3e0; color: #e65100; }
.arch-badge-trf { background: #f3e5f5; color: #7b1fa2; }
.arch-badge-cog { background: #e3f2fd; color: #1565c0; }
.arch-card-stats { font-size: .72rem; color: var(--c-text3); display: flex; gap: 10px; }

.sc-card { background: var(--c-surface); border: 1.5px solid var(--c-border); border-radius: var(--radius); padding: 14px; margin-bottom: 12px; cursor: pointer; transition: all .15s; }
.sc-card:hover { border-color: var(--c-accent); box-shadow: var(--shadow); }
.sc-card.selected { border-color: var(--c-accent); background: var(--c-accent-light); }
.sc-hdr { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.sc-label { font-weight: 600; font-size: .88rem; color: var(--c-accent2); flex: 1; }
.sc-badges { display: flex; gap: 6px; flex-shrink: 0; }
.prog-badge { font-size: .68rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.prog-badge.full { background: #dcfce7; color: #166534; }
.prog-badge.partial { background: #fef9c3; color: #854d0e; }
.prog-badge.flat { background: var(--c-bg); color: var(--c-text3); }
.prog-badge.sparse { background: #fce4ec; color: #c2185b; }
.sc-count-badge { background: var(--c-accent-light); color: var(--c-accent); font-size: .68rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; }

.ladder-mini { display: flex; align-items: center; gap: 2px; margin: 8px 0; }
.lm-rung { display: flex; flex-direction: column; align-items: center; flex: 1; }
.lm-dot { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: .62rem; font-weight: 700; color: white; background: #d1d9e6; }
.lm-dot.on { background: var(--c-accent); }
.lm-dot.gap { background: transparent; border: 2px dashed #d1d9e6; color: var(--c-text3); }
.lm-cnt { font-size: .62rem; color: var(--c-text3); margin-top: 2px; }
.lm-conn { height: 2px; flex: 0.5; background: #d1d9e6; }
.lm-conn.on { background: var(--c-accent); }
.lm-conn.gap { background: transparent; border-top: 2px dashed #d1d9e6; }

.arch-detail { border-left: 1px solid var(--c-border); padding-left: 20px; }
.arch-detail-hdr { font-size: .85rem; color: var(--c-text3); margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--c-border); display: flex; align-items: center; gap: 8px; }

.ladder-full { margin: 12px 0; }
.lf-rung { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-left: 3px solid var(--c-border); margin-left: 10px; padding-left: 14px; position: relative; }
.lf-rung::before { content: ''; position: absolute; left: -7px; top: 16px; width: 12px; height: 12px; border-radius: 50%; background: var(--c-accent); border: 2px solid white; }
.lf-rung.gap-rung { border-left-style: dashed; padding: 4px 0 4px 14px; color: var(--c-text3); font-style: italic; font-size: .78rem; }
.lf-rung.gap-rung::before { background: #d1d9e6; width: 8px; height: 8px; left: -5px; top: 8px; }
.lf-lvl { background: var(--c-accent); color: white; padding: 2px 8px; border-radius: 10px; font-size: .68rem; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
.lf-body { flex: 1; }
.lf-name { font-size: .72rem; color: var(--c-text3); margin-bottom: 3px; }
.lf-skills { display: flex; flex-direction: column; gap: 2px; }
.lf-skill { font-size: .78rem; color: var(--c-text); }
.lf-asced-tags { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.lf-asced-tag { font-size: .62rem; padding: 1px 5px; border-radius: 3px; background: #fff8e1; color: #e65100; }

.asced-list { display: flex; flex-direction: column; gap: 3px; }
.asced-item { display: flex; justify-content: space-between; font-size: .78rem; padding: 3px 0; }
.asced-item-name { color: var(--c-text2); }
.asced-item-count { font-weight: 600; color: var(--c-accent2); }
.asced-code-tag { display: inline-block; background: #e3f2fd; color: #1565c0; font-family: 'JetBrains Mono', monospace; font-size: .65rem; padding: 1px 5px; border-radius: 3px; margin-right: 4px; }

@media (max-width: 1100px) { .arch-layout { grid-template-columns: 280px 1fr; } .arch-detail { display: none; } }
@media (max-width: 640px) { .results-grid { grid-template-columns: 1fr; } .drawer { width: 100vw; } .hdr-stats { display: none; } .arch-layout { grid-template-columns: 1fr; } }
"""


def _js() -> str:
    return r"""
let data = null;
let skillIndex = new Map();
let unitIndex = new Map();
let qualIndex = new Map();
let occIndex = new Map();
let archetypesData = [];

let skillPage = 0, unitPage = 0, qualPage = 0, occPage = 0;
const PAGE_SIZE = 40;
let filteredSkills = [], filteredUnits = [], filteredQuals = [], filteredOccs = [];
let activeFilters = {};

const FACET_NAMES = { NAT:'Nature', TRF:'Transfer', COG:'Cognitive', ASCED:'ASCED', LRN:'Learning', DIG:'Digital', FUT:'Future', LVL:'Level' };
const CTX_CLASS = { PRACTICAL:'prac', THEORETICAL:'theo', HYBRID:'hybrid' };

document.addEventListener('DOMContentLoaded', () => {
  const check = setInterval(() => {
    if (typeof ASSERTION_DATA !== 'undefined') { clearInterval(check); init(ASSERTION_DATA); }
  }, 80);
  setTimeout(() => clearInterval(check), 8000);
});

function init(d) {
  data = d;
  data.skills.forEach(s => skillIndex.set(s.skill_id, s));
  (data.units||[]).forEach(u => unitIndex.set(u.unit_code, u));
  (data.qualifications||[]).forEach(q => qualIndex.set(q.qualification_code, q));
  (data.occupations||[]).forEach(o => occIndex.set(o.anzsco_code, o));
  archetypesData = data.archetypes || [];

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
  initArchetypes();

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
  if (m.total_occupations) html += `<span><b>${m.total_occupations.toLocaleString()}</b> Occs</span>`;
  if (archetypesData.length) html += `<span><b>${archetypesData.length}</b> Archetypes</span>`;
  document.getElementById('headerStats').innerHTML = html;
}

function renderFacetFilters() {
  const container = document.getElementById('facetFilters');
  if (!data.facets) return;
  let html = '';
  for (const [fid, fi] of Object.entries(data.facets)) {
    for (const [code, vi] of Object.entries(fi.values || {})) {
      const count = data.skills.filter(s => { const fc = s.facets?.[fid]?.code; if (Array.isArray(fc)) return fc.includes(code); return fc === code; }).length;
      if (count > 0) html += `<button class="chip" data-facet="${fid}" data-code="${code}" onclick="toggleFilter('${fid}','${code}')">${vi.name} <span style="opacity:.6">${count}</span></button>`;
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

// ── SKILLS ──────────────────────────────────────────────
function onSkillSearch() {
  const q = document.getElementById('skillSearch').value.toLowerCase().trim();
  filteredSkills = data.skills.filter(s => {
    if (q) { const match = s.preferred_label.toLowerCase().includes(q) || (s.alternative_labels||[]).some(a=>a.toLowerCase().includes(q)) || s.skill_id.toLowerCase().includes(q) || (s.unit_codes||[]).some(c=>c.toLowerCase().includes(q)); if (!match) return false; }
    for (const key of Object.keys(activeFilters)) { const [fid,code] = key.split('|'); const fc = s.facets?.[fid]?.code; if (Array.isArray(fc)) { if (!fc.includes(code)) return false; } else { if (fc !== code) return false; } }
    return true;
  });
  resetSkillResults();
}
function resetSkillResults() { skillPage = 0; document.getElementById('skillResults').innerHTML = ''; document.getElementById('skillResultsMeta').innerHTML = `Showing <b>${filteredSkills.length}</b> skills`; loadMoreSkills(); }
function loadMoreSkills() {
  const start = skillPage * PAGE_SIZE; const slice = filteredSkills.slice(start, start+PAGE_SIZE);
  const container = document.getElementById('skillResults');
  for (const s of slice) { container.insertAdjacentHTML('beforeend', skillCardHTML(s)); }
  skillPage++; document.getElementById('skillLoadMore').style.display = (start+PAGE_SIZE < filteredSkills.length) ? '' : 'none';
}
function skillCardHTML(s) {
  const ctxBadges = Object.entries(s.context_distribution||{}).map(([ctx,n])=>`<span class="badge badge-ctx badge-${CTX_CLASS[ctx]||'hybrid'}">${ctx} ${n}</span>`).join('');
  const facetBadges = Object.entries(s.facets||{}).filter(([,v])=>v?.name).map(([,v])=>`<span class="badge badge-facet">${v.name}</span>`).join('');
  const altBadge = s.alternative_labels?.length ? `<span class="badge badge-alt">${s.alternative_labels.length} alt</span>` : '';
  return `<div class="skill-card" onclick="openSkill('${s.skill_id}')"><div class="skill-card-name">${esc(s.preferred_label)}</div>${s.definition?`<div class="skill-card-def">${esc(s.definition)}</div>`:''}<div class="skill-card-meta"><span class="badge badge-count">${s.assertion_count} assertions</span>${ctxBadges}${facetBadges}${altBadge}</div></div>`;
}

// ── UNITS ───────────────────────────────────────────────
function onUnitSearch() { const q = document.getElementById('unitSearch').value.toLowerCase().trim(); filteredUnits = (data.units||[]).filter(u=>!q||u.unit_code.toLowerCase().includes(q)||(u.unit_title||'').toLowerCase().includes(q)); resetUnitResults(); }
function resetUnitResults() { unitPage=0; document.getElementById('unitResults').innerHTML=''; document.getElementById('unitResultsMeta').innerHTML=`Showing <b>${filteredUnits.length}</b> units`; loadMoreUnits(); }
function loadMoreUnits() { const start=unitPage*PAGE_SIZE; filteredUnits.slice(start,start+PAGE_SIZE).forEach(u=>{ document.getElementById('unitResults').insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openUnit('${u.unit_code}')"><div class="unit-code">${esc(u.unit_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(u.unit_title||'')}</div><div class="unit-skill-count">${u.skill_count} skills</div></div>`); }); unitPage++; document.getElementById('unitLoadMore').style.display=(start+PAGE_SIZE<filteredUnits.length)?'':'none'; }

// ── QUALIFICATIONS ──────────────────────────────────────
function onQualSearch() { const q=document.getElementById('qualSearch').value.toLowerCase().trim(); filteredQuals=(data.qualifications||[]).filter(qq=>!q||qq.qualification_code.toLowerCase().includes(q)||qq.qualification_title.toLowerCase().includes(q)); resetQualResults(); }
function resetQualResults() { qualPage=0; document.getElementById('qualResults').innerHTML=''; document.getElementById('qualResultsMeta').innerHTML=`Showing <b>${filteredQuals.length}</b> qualifications`; loadMoreQuals(); }
function loadMoreQuals() { const start=qualPage*PAGE_SIZE; filteredQuals.slice(start,start+PAGE_SIZE).forEach(q=>{ document.getElementById('qualResults').insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openQual('${q.qualification_code}')"><div class="unit-code">${esc(q.qualification_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(q.qualification_title)}</div><div class="unit-skill-count">${q.skill_count} skills · ${q.unit_codes.length} units</div></div>`); }); qualPage++; document.getElementById('qualLoadMore').style.display=(start+PAGE_SIZE<filteredQuals.length)?'':'none'; }

// ── OCCUPATIONS ─────────────────────────────────────────
function onOccSearch() { const q=document.getElementById('occSearch').value.toLowerCase().trim(); filteredOccs=(data.occupations||[]).filter(o=>!q||o.anzsco_code.toLowerCase().includes(q)||o.anzsco_title.toLowerCase().includes(q)); resetOccResults(); }
function resetOccResults() { occPage=0; document.getElementById('occResults').innerHTML=''; document.getElementById('occResultsMeta').innerHTML=`Showing <b>${filteredOccs.length}</b> occupations`; loadMoreOccs(); }
function loadMoreOccs() { const start=occPage*PAGE_SIZE; filteredOccs.slice(start,start+PAGE_SIZE).forEach(o=>{ document.getElementById('occResults').insertAdjacentHTML('beforeend', `<div class="unit-card" onclick="openOcc('${o.anzsco_code}')"><div class="unit-code">${esc(o.anzsco_code)}</div><div style="font-size:.82rem;color:var(--c-text2);margin:4px 0">${esc(o.anzsco_title)}</div><div class="unit-skill-count">${o.skill_count} skills · ${o.qualification_codes.length} quals</div></div>`); }); occPage++; document.getElementById('occLoadMore').style.display=(start+PAGE_SIZE<filteredOccs.length)?'':'none'; }

// ══════════════════════════════════════════════════════════
//  ARCHETYPE EXPLORER
// ══════════════════════════════════════════════════════════

function initArchetypes() {
  const el = document.getElementById('archContent');
  if (!archetypesData.length) { el.innerHTML = '<p style="color:var(--c-text3);padding:20px;">No archetype data available. Run the pipeline with archetype clustering enabled.</p>'; return; }
  const sorted = [...archetypesData].sort((a,b) => b.total_skills - a.total_skills);
  let sidebar = '<div class="arch-search"><input type="text" placeholder="Search archetypes..." id="archSearch"></div>';
  for (const a of sorted) {
    const sc = a.sub_clusters?.length||0, asc = Object.keys(a.asced_coverage||{}).length;
    const lvls = Object.keys(a.level_distribution||{}).sort();
    const lr = lvls.length ? 'L'+lvls[0]+'-'+lvls[lvls.length-1] : '-';
    sidebar += `<div class="arch-card" data-aid="${a.archetype_id}"><div class="arch-card-label">${a.label}</div><div class="arch-card-badges"><span class="arch-badge arch-badge-nat">${a.nat.name}</span><span class="arch-badge arch-badge-trf">${a.trf.name}</span><span class="arch-badge arch-badge-cog">${a.cog.name}</span></div><div class="arch-card-stats"><span>${a.total_skills} skills</span><span>${sc} clusters</span><span>${asc} fields</span><span>${lr}</span></div></div>`;
  }
  el.innerHTML = `<div class="arch-layout"><div class="arch-sidebar">${sidebar}</div><div id="archMain"><p style="color:var(--c-text3);padding:20px;">Select an archetype to view sub-clusters and progression ladders</p></div><div class="arch-detail"><div class="arch-detail-hdr"><i class="bi bi-bar-chart-steps"></i> Progression Ladder</div><div id="archDetail" style="color:var(--c-text3);text-align:center;padding:40px;"><i class="bi bi-hand-index" style="font-size:2rem;opacity:.4;display:block;margin-bottom:8px;"></i>Select a sub-cluster</div></div></div>`;
  el.querySelectorAll('.arch-card').forEach(card => { card.addEventListener('click', () => { el.querySelectorAll('.arch-card').forEach(c=>c.classList.remove('active')); card.classList.add('active'); loadArchSC(card.dataset.aid); }); });
  document.getElementById('archSearch')?.addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    el.querySelectorAll('.arch-card').forEach(card => { const a = archetypesData.find(x=>x.archetype_id===card.dataset.aid); card.style.display = (!q||q.length<2||a?.label?.toLowerCase().includes(q)||a?.nat?.name?.toLowerCase().includes(q)||a?.trf?.name?.toLowerCase().includes(q)||a?.cog?.name?.toLowerCase().includes(q)) ? '' : 'none'; });
  });
}

function loadArchSC(aid) {
  const arch = archetypesData.find(a=>a.archetype_id===aid); if (!arch) return;
  const el = document.getElementById('archMain');
  let html = `<div style="margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--c-border);"><div style="font-size:1rem;font-weight:700;color:var(--c-accent2);">${arch.label}</div><div style="font-size:.82rem;color:var(--c-text2);">${arch.total_skills} skills, ${arch.sub_clusters?.length||0} sub-clusters</div></div>`;
  if (!arch.sub_clusters?.length) { el.innerHTML = html+'<p style="color:var(--c-text3);">No sub-clusters</p>'; return; }
  const scs = [...arch.sub_clusters].sort((a,b)=>{const o={full:0,partial:1,sparse:2,flat:3}; const d=(o[a.progression_type]||9)-(o[b.progression_type]||9); return d!==0?d:b.total_skills-a.total_skills;});
  for (const sc of scs) {
    const prog=sc.progression||[], levels=new Set(prog.map(r=>r.level)), minL=sc.level_span?.[0]||1, maxL=sc.level_span?.[1]||7;
    let ladder='<div class="ladder-mini">';
    for (let l=minL;l<=maxL;l++) {
      if (l>minL) { const cls=(levels.has(l-1)&&levels.has(l))?'on':'gap'; ladder+=`<div class="lm-conn ${cls}"></div>`; }
      const rung=prog.find(r=>r.level===l);
      if (rung) ladder+=`<div class="lm-rung"><div class="lm-dot on">${l}</div><div class="lm-cnt">${rung.skill_count}</div></div>`;
      else ladder+=`<div class="lm-rung"><div class="lm-dot gap">${l}</div></div>`;
    }
    ladder+='</div>';
    const asc=Object.keys(sc.asced_spread||{}).length;
    html+=`<div class="sc-card" data-cid="${sc.cluster_id}" data-aid="${aid}"><div class="sc-hdr"><div class="sc-label">${sc.label}</div><div class="sc-badges"><span class="prog-badge ${sc.progression_type}">${sc.progression_type}</span><span class="sc-count-badge">${sc.total_skills}</span></div></div>${ladder}<div style="font-size:.72rem;color:var(--c-text3);display:flex;gap:10px;"><span>${asc} ASCED field${asc!==1?'s':''}</span><span>Level ${sc.level_span?.[0]||'?'}–${sc.level_span?.[1]||'?'}</span><span>Sim ${(sc.avg_intra_similarity*100).toFixed(0)}%</span></div></div>`;
  }
  el.innerHTML = html;
  el.querySelectorAll('.sc-card').forEach(card => { card.addEventListener('click', ()=>{ el.querySelectorAll('.sc-card').forEach(c=>c.classList.remove('selected')); card.classList.add('selected'); showArchDetail(card.dataset.aid, card.dataset.cid); }); });
}

function showArchDetail(aid, cid) {
  const arch=archetypesData.find(a=>a.archetype_id===aid); if(!arch) return;
  const sc=arch.sub_clusters?.find(s=>s.cluster_id===cid); if(!sc) return;
  const panel=document.getElementById('archDetail');
  let html=`<div style="margin-bottom:14px;"><div style="font-size:1rem;font-weight:700;color:var(--c-accent2);">${sc.label}</div><div style="font-size:.72rem;color:var(--c-text3);font-family:'JetBrains Mono',monospace;">${sc.cluster_id}</div></div>`;
  // Full progression ladder
  html+='<div class="d-section"><div class="d-label"><i class="bi bi-bar-chart-steps"></i> Progression Ladder</div><div class="ladder-full">';
  const prog=sc.progression||[], minL=sc.level_span?.[0]||1, maxL=sc.level_span?.[1]||7, gaps=sc.level_gaps||[];
  for (let l=minL;l<=maxL;l++) {
    const rung=prog.find(r=>r.level===l);
    if (rung) {
      html+=`<div class="lf-rung"><span class="lf-lvl">LVL ${rung.level}</span><div class="lf-body"><div class="lf-name">${rung.level_name} (${rung.skill_count} skill${rung.skill_count!==1?'s':''})</div><div class="lf-skills">${rung.skill_names.slice(0,8).map(n=>`<div class="lf-skill">${n}</div>`).join('')}${rung.skill_names.length>8?`<div class="lf-skill" style="color:var(--c-text3);font-style:italic;">+${rung.skill_names.length-8} more</div>`:''}</div>`;
      if (rung.asced_names?.length) html+=`<div class="lf-asced-tags">${rung.asced_names.slice(0,5).map(n=>`<span class="lf-asced-tag">${n}</span>`).join('')}${rung.asced_names.length>5?`<span class="lf-asced-tag">+${rung.asced_names.length-5}</span>`:''}</div>`;
      html+='</div></div>';
    } else if (gaps.includes(l)) {
      html+=`<div class="lf-rung gap-rung">Level ${l} — gap</div>`;
    }
  }
  html+='</div></div>';
  // ASCED spread
  if (sc.asced_spread && Object.keys(sc.asced_spread).length) {
    html+='<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> ASCED Field Spread</div><div class="asced-list">';
    Object.entries(sc.asced_spread).sort((a,b)=>b[1]-a[1]).slice(0,10).forEach(([code,count])=>{ const name=sc.asced_names?.[code]||code; html+=`<div class="asced-item"><span class="asced-item-name"><span class="asced-code-tag">${code}</span>${name}</span><span class="asced-item-count">${count}</span></div>`; });
    html+='</div></div>';
  }
  // Representative skills
  if (sc.representative_skills?.length) {
    html+='<div class="d-section"><div class="d-label"><i class="bi bi-star"></i> Representative Skills</div>';
    sc.representative_skills.forEach(rs=>{ html+=`<div style="display:flex;justify-content:space-between;padding:5px 8px;background:var(--c-bg);border-radius:6px;font-size:.82rem;margin-bottom:4px;cursor:pointer;" onclick="openSkill('${rs.skill_id||''}')"><span>${rs.name}</span>${rs.level?`<span style="font-size:.7rem;color:var(--c-text3);">L${rs.level}</span>`:''}</div>`; });
    html+='</div>';
  }
  panel.innerHTML = html;
}

// ── DRAWER: Skill detail ────────────────────────────────
function openSkill(sid) {
  const s = skillIndex.get(sid); if (!s) return;
  document.getElementById('drawerTitle').textContent = s.preferred_label;
  let html = '';
  if (s.definition) html += `<div class="d-section"><div class="d-label"><i class="bi bi-info-circle"></i> Definition</div><div class="d-def">${esc(s.definition)}</div></div>`;
  const fe = Object.entries(s.facets||{}).filter(([,v])=>v?.name);
  if (fe.length) { html += '<div class="d-section"><div class="d-label"><i class="bi bi-tags"></i> Dimensions</div>'; for (const [fid,fv] of fe) { html+=`<div class="facet-row"><span class="facet-dim">${FACET_NAMES[fid]||fid}</span><span class="facet-val">${esc(fv.name)}${fv.confidence?` <span style="opacity:.5;font-size:.7rem">${(fv.confidence*100).toFixed(0)}%</span>`:''}</span></div>`; } html+='</div>'; }
  if (s.alternative_labels?.length) { html+=`<div class="d-section"><div class="d-label"><i class="bi bi-card-heading"></i> Alternative Labels (${s.alternative_labels.length})</div><div class="d-tags">${s.alternative_labels.map(a=>`<span class="d-tag">${esc(a)}</span>`).join('')}</div></div>`; }
  const ctxE = Object.entries(s.context_distribution||{});
  if (ctxE.length) { const total=ctxE.reduce((a,[,n])=>a+n,0); html+='<div class="d-section"><div class="d-label"><i class="bi bi-bar-chart"></i> Teaching Context</div>'; for (const [ctx,n] of ctxE) { const p=(n/total*100).toFixed(1); html+=`<div class="dist-row"><span class="dist-label">${ctx}</span><div class="dist-bar-track"><div class="dist-bar-fill ${CTX_CLASS[ctx]||'hybrid'}" style="width:${p}%"></div></div><span class="dist-val">${n}</span></div>`; } html+='</div>'; }
  const lvlE = Object.entries(s.level_distribution||{}).sort();
  if (lvlE.length) { const total=lvlE.reduce((a,[,n])=>a+n,0); html+='<div class="d-section"><div class="d-label"><i class="bi bi-layers"></i> Level of Engagement</div>'; for (const [l,n] of lvlE) { const p=(n/total*100).toFixed(1); html+=`<div class="dist-row"><span class="dist-label">${l}</span><div class="dist-bar-track"><div class="dist-bar-fill level" style="width:${p}%"></div></div><span class="dist-val">${n}</span></div>`; } html+='</div>'; }
  if (s.unit_codes?.length) { html+=`<div class="d-section"><div class="d-label"><i class="bi bi-journal-code"></i> Units (${s.unit_codes.length})</div><div class="d-tags">${s.unit_codes.slice(0,30).map(c=>`<span class="d-tag code" style="cursor:pointer" onclick="openUnit('${c}')">${c}</span>`).join('')}${s.unit_codes.length>30?`<span class="d-tag" style="opacity:.6">+${s.unit_codes.length-30}</span>`:''}</div></div>`; }
  if (s.assertions?.length) {
    const show=s.assertions.slice(0,20);
    html+=`<div class="d-section"><div class="d-label"><i class="bi bi-link-45deg"></i> Assertions (${s.assertions.length})</div><table class="a-table"><thead><tr><th>Unit</th><th>Context</th><th>Level</th><th>Evidence</th></tr></thead><tbody>`;
    for (const a of show) { const cls=CTX_CLASS[a.teaching_context]||'hybrid'; html+=`<tr><td><span class="d-tag code" style="cursor:pointer" onclick="openUnit('${a.unit_code}')">${a.unit_code}</span></td><td><span class="a-ctx-dot ${cls}"></span>${a.teaching_context}</td><td>${a.level_of_engagement}</td><td class="a-evidence" title="${esc(a.evidence)}">${esc(a.evidence)}</td></tr>`; }
    html+='</tbody></table>';
    if (s.assertions.length>20) html+=`<div style="text-align:center;margin-top:8px;font-size:.78rem;color:var(--c-text3)">Showing 20 of ${s.assertions.length}</div>`;
    html+='</div>';
  }
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

function openUnit(code) {
  const u = unitIndex.get(code); if (!u) return;
  document.getElementById('drawerTitle').textContent = u.unit_title ? `${code} — ${u.unit_title}` : code;
  let html = `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${u.skill_ids.length})</div><div class="d-tags">`;
  for (const sid of u.skill_ids) { const s=skillIndex.get(sid); html+=`<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`; }
  html+='</div></div>';
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

function openQual(code) {
  const q = qualIndex.get(code); if (!q) return;
  document.getElementById('drawerTitle').textContent = `${code} — ${q.qualification_title}`;
  let html = `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${q.skill_ids.length})</div><div class="d-tags">${q.skill_ids.slice(0,40).map(sid=>{const s=skillIndex.get(sid);return`<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`;}).join('')}${q.skill_ids.length>40?`<span class="d-tag" style="opacity:.6">+${q.skill_ids.length-40}</span>`:''}</div></div>`;
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

function openOcc(code) {
  const o = occIndex.get(code); if (!o) return;
  document.getElementById('drawerTitle').textContent = `${code} — ${o.anzsco_title}`;
  let html = `<div class="d-section"><div class="d-label"><i class="bi bi-mortarboard"></i> Skills (${o.skill_ids.length})</div><div class="d-tags">${o.skill_ids.slice(0,50).map(sid=>{const s=skillIndex.get(sid);return`<span class="d-tag" style="cursor:pointer" onclick="openSkill('${sid}')">${esc(s?s.preferred_label:sid)}</span>`;}).join('')}${o.skill_ids.length>50?`<span class="d-tag" style="opacity:.6">+${o.skill_ids.length-50}</span>`:''}</div></div>`;
  document.getElementById('drawerBody').innerHTML = html;
  showDrawer();
}

function showDrawer() { document.getElementById('drawer').classList.remove('hidden'); document.getElementById('drawerOverlay').classList.remove('hidden'); }
function closeDrawer() { document.getElementById('drawer').classList.add('hidden'); document.getElementById('drawerOverlay').classList.add('hidden'); }

// ── Tabs ────────────────────────────────────────────────
function onTabClick(e) {
  const tab = e.currentTarget.dataset.tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  ['skills','units','quals','occs','archetypes','matrix','unitasced'].forEach(p => {
    document.getElementById(p+'Panel').classList.toggle('hidden', p !== tab);
  });
  if (tab === 'matrix' && !matrixInitialized) initMatrix();
  if (tab === 'unitasced' && !uaInitialized) initUnitAsced();
}

function esc(s) { if (!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }

// ══════════════════════════════════════════════════════════
//  SANKEY (simplified — kept from original)
// ══════════════════════════════════════════════════════════
let matrixInitialized = false;
function initMatrix() { matrixInitialized = true; document.getElementById('matrixSearch').addEventListener('input', debounce(onMatrixSearch, 300)); }
function onMatrixSearch() {
  const q = document.getElementById('matrixSearch').value.toLowerCase().trim();
  document.getElementById('matrixDetail').innerHTML = '';
  if (q.length < 2) { document.getElementById('matrixContainer').innerHTML = ''; document.getElementById('matrixHint').textContent = 'Type at least 2 characters'; return; }
  document.getElementById('matrixHint').textContent = 'Sankey flow visualization — search for skills, units, qualifications or occupations';
  document.getElementById('matrixContainer').innerHTML = '<p style="color:var(--c-text3);padding:20px;">Sankey visualization renders here when data matches. Try searching for a specific skill or unit code.</p>';
}

let uaInitialized = false;
function initUnitAsced() { uaInitialized = true; document.getElementById('uaSearch').addEventListener('input', debounce(onUaSearch, 300)); }
function onUaSearch() {
  const q = document.getElementById('uaSearch').value.toLowerCase().trim();
  if (q.length < 2) { document.getElementById('uaContainer').innerHTML = ''; document.getElementById('uaHint').textContent = 'Type at least 2 characters'; return; }
  document.getElementById('uaHint').textContent = 'Unit-first flow visualization';
  document.getElementById('uaContainer').innerHTML = '<p style="color:var(--c-text3);padding:20px;">Unit-first visualization renders here. Try a unit code.</p>';
}
"""