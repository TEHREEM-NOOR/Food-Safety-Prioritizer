"""
ui_theme.py - Soft Editorial Analytics Design System (premium pass)
for the Food Safety Inspection Prioritiser.

Drop-in replacement: every name imported by app.py is still exported with the
same signature, and the CSS hooks the app relies on (fsp-card, fsp-badge,
fsp-badge-success/warning/info/danger/neutral) are unchanged.

Design notes
- Same indigo / mauve / parchment brand palette, Inter typography.
- One spacing rhythm: Streamlit's own block gap does the work; the ad-hoc
  <div style="height:Npx"> spacers in app.py are normalised in CSS.
- Cards, inputs, tabs, expanders, uploaders, alerts and charts share one
  radius scale, one border colour and one shadow recipe.
"""

import html as _html

# ---------------------------------------------------------------------------
# Palette tokens
# ---------------------------------------------------------------------------
# Brand palette
SPACE_INDIGO   = "#22223B"
DUSTY_GRAPE    = "#4A4E69"
LILAC_ASH      = "#9A8C98"
ALMOND_SILK    = "#C9ADA7"
PARCHMENT      = "#F2E9E4"

# Interface surfaces
APP_BG         = "#FAF8F6"
SURFACE        = "#FFFFFF"
SURFACE_SUBTLE = "#F6F2F0"
BORDER         = "#E7E0DD"
BORDER_STRONG  = "#D6CBC8"

# Text
TEXT_PRIMARY    = "#22223B"
TEXT_SECONDARY  = "#625E6A"
TEXT_MUTED      = "#77717B"
TEXT_ON_DARK    = "#FFFFFF"

# Semantic status
SUCCESS        = "#287A58"
SUCCESS_SOFT   = "#E7F3EC"
WARNING        = "#946200"
WARNING_SOFT   = "#FBF1D8"
DANGER         = "#B4233C"
DANGER_SOFT    = "#FBE9EC"
INFO           = "#365C87"
INFO_SOFT      = "#EAF0F7"

# Hairlines that pair with the soft status fills (also hard-coded in app.py)
SUCCESS_LINE   = "#C3DFD0"
WARNING_LINE   = "#EFE0B4"
DANGER_LINE    = "#F0C6CC"
INFO_LINE      = "#C8D9E8"

# Shape & depth
RADIUS_SM      = "10px"
RADIUS_MD      = "14px"
RADIUS_LG      = "18px"
SHADOW_CARD    = "0 1px 2px rgba(34, 34, 59, 0.04), 0 4px 14px rgba(34, 34, 59, 0.04)"
SHADOW_HOVER   = "0 2px 4px rgba(34, 34, 59, 0.06), 0 8px 24px rgba(34, 34, 59, 0.08)"

# --- Backward-compat aliases so app.py imports keep working ---
NAVY           = SPACE_INDIGO
PRIMARY_BLUE   = DUSTY_GRAPE
SOFT_LAVENDER  = INFO_SOFT
LAVENDER_ACCENT = DUSTY_GRAPE
SOFT_MINT      = SUCCESS_SOFT
SUCCESS_GREEN  = SUCCESS
SOFT_AMBER     = WARNING_SOFT
WARNING_AMBER  = WARNING
SOFT_ROSE      = DANGER_SOFT
DANGER_RED     = DANGER
BG_MAIN        = APP_BG
BG_CARD        = SURFACE
TEXT_MAIN      = TEXT_PRIMARY
BORDER_COLOR   = BORDER

_FONT_STACK = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

# ---------------------------------------------------------------------------
# Inline SVG icon library (line icons, 1.75 stroke for a lighter, finer look)
# ---------------------------------------------------------------------------
_ICON_STYLE = ('xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
               'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"')


def _s(body: str) -> str:
    return f'<svg {_ICON_STYLE}>{body}</svg>'


ICONS = {
    # Navigation / page headers
    "database":     _s('<path d="M12 2C6.5 2 2 4.2 2 7v10c0 2.8 4.5 5 10 5s10-2.2 10-5V7c0-2.8-4.5-5-10-5z"/><path d="M2 12c0 2.8 4.5 5 10 5s10-2.2 10-5"/><path d="M2 7c0 2.8 4.5 5 10 5s10-2.2 10-5"/>'),
    "bar-chart":    _s('<rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/>'),
    "crosshair":    _s('<circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/>'),
    "layers":       _s('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>'),
    "sliders":      _s('<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>'),
    "map-pin":      _s('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
    # KPI icons
    "file-text":    _s('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>'),
    "alert-triangle": _s('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    "calendar":     _s('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'),
    "cpu":          _s('<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>'),
    "target":       _s('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'),
    "search":       _s('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    "zap":          _s('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'),
    "dollar-sign":  _s('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
    "shield":       _s('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'),
    "activity":     _s('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'),
    "check-circle": _s('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'),
    "upload":       _s('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>'),
    "settings":     _s('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>'),
    "users":        _s('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "clock":        _s('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    "trending-up":  _s('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
    "filter":       _s('<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'),
    "download":     _s('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'),
    "book-open":    _s('<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'),
    "grid":         _s('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>'),
    "box":          _s('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'),
    "pie-chart":    _s('<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>'),
    "award":        _s('<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>'),
    "truck":        _s('<rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>'),
    "clipboard":    _s('<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'),
    "printer":      _s('<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>'),
}


def icon(name: str, color: str = TEXT_MUTED, size: int = 18) -> str:
    """Return an inline SVG icon string. Falls back to empty string for unknown names."""
    svg = ICONS.get(name, "")
    if not svg:
        return ""
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    svg = svg.replace('width="18"', f'width="{size}"').replace('height="18"', f'height="{size}"')
    return svg


# ---------------------------------------------------------------------------
# Global CSS
#
# Built in three parts so the large stylesheet can be written with plain
# braces (no f-string escaping): font import, :root tokens, component rules.
# ---------------------------------------------------------------------------
_FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..700&display=swap');\n"

_ROOT_VARS = f""":root {{
  --font: {_FONT_STACK};
  --ink: {SPACE_INDIGO};
  --grape: {DUSTY_GRAPE};
  --lilac: {LILAC_ASH};
  --almond: {ALMOND_SILK};
  --parchment: {PARCHMENT};
  --bg: {APP_BG};
  --surface: {SURFACE};
  --surface-2: {SURFACE_SUBTLE};
  --line: {BORDER};
  --line-strong: {BORDER_STRONG};
  --text: {TEXT_PRIMARY};
  --text-2: {TEXT_SECONDARY};
  --text-3: {TEXT_MUTED};
  --success: {SUCCESS};  --success-soft: {SUCCESS_SOFT};  --success-line: {SUCCESS_LINE};
  --warning: {WARNING};  --warning-soft: {WARNING_SOFT};  --warning-line: {WARNING_LINE};
  --danger: {DANGER};    --danger-soft: {DANGER_SOFT};    --danger-line: {DANGER_LINE};
  --info: {INFO};        --info-soft: {INFO_SOFT};        --info-line: {INFO_LINE};
  --r-sm: {RADIUS_SM};
  --r-md: {RADIUS_MD};
  --r-lg: {RADIUS_LG};
  --sh-card: {SHADOW_CARD};
  --sh-hover: {SHADOW_HOVER};
}}
"""

_BASE_CSS = """
/* ===================================================================
   1. Base typography and canvas
   =================================================================== */
html, body, .stApp {
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp select, .stApp button, .stApp summary,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp [data-baseweb] {
  font-family: var(--font);
}
* { scrollbar-width: thin; scrollbar-color: var(--line-strong) transparent; }
::selection { background: var(--almond); color: var(--ink); }
.stApp :focus-visible { outline: 2px solid var(--grape); outline-offset: 2px; }
.stApp input:focus-visible, .stApp textarea:focus-visible { outline: none; }

/* ===================================================================
   2. App chrome and page container
   =================================================================== */
[data-testid="stHeader"] {
  background: rgba(250, 248, 246, 0.82);
  -webkit-backdrop-filter: blur(10px) saturate(1.2);
  backdrop-filter: blur(10px) saturate(1.2);
}
[data-testid="stDecoration"] { display: none; }
footer { visibility: hidden; height: 0; }

@keyframes fsp-fade { from { opacity: 0; } to { opacity: 1; } }

.stApp .block-container,
.stApp [data-testid="stMainBlockContainer"] {
  max-width: 1280px;
  margin: 0 auto;
  padding: 4.5rem 3rem 4rem 3rem;
  animation: fsp-fade 0.35s ease-out;
}
@media (max-width: 900px) {
  .stApp .block-container,
  .stApp [data-testid="stMainBlockContainer"] { padding-left: 1.25rem; padding-right: 1.25rem; }
}

/* Vertical rhythm: Streamlit's block gap does the spacing. The fixed-height
   spacer divs in app.py are reduced so section breaks are one consistent size. */
.stApp [data-testid="stMarkdownContainer"] div[style^="height"]:empty {
  height: 8px !important;
  margin: 0 !important;
}

.stApp [data-testid="stMarkdownContainer"] p { line-height: 1.6; }
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p {
  color: var(--text-3);
  font-size: 0.84rem;
  line-height: 1.5;
}
.stApp [data-testid="stMarkdownContainer"] code {
  background: var(--surface-2);
  color: var(--grape);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.1em 0.4em;
  font-size: 0.86em;
}

/* ===================================================================
   3. Page header, section titles, cards
   =================================================================== */
.fsp-page-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin: 0 0 8px 0;
  padding: 0 0 22px 0;
  border-bottom: 1px solid var(--line);
}
.fsp-page-header-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: var(--r-md);
  background: var(--parchment);
  box-shadow: inset 0 0 0 1px rgba(201, 173, 167, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}
.fsp-page-header-text { flex: 1; min-width: 0; }
.fsp-page-header-aside { flex-shrink: 0; padding-top: 4px; }
.stApp .fsp-page-header h1.fsp-page-header-title {
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -0.022em;
  line-height: 1.2;
  color: var(--ink);
  margin: 0 0 6px 0;
  padding: 0;
}
.stApp .fsp-page-header p.fsp-page-header-subtitle {
  font-size: 0.94rem;
  line-height: 1.55;
  color: var(--text-2);
  margin: 0;
  padding: 0;
  max-width: 72ch;
}

.fsp-section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 -4px 0;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.3;
  color: var(--ink);
}
.fsp-section-title svg { flex-shrink: 0; }

.fsp-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  padding: 20px 24px;
  margin: 0 !important;
  box-shadow: var(--sh-card);
  font-size: 0.92rem;
  line-height: 1.6;
  color: var(--text);
}
.fsp-card strong { font-weight: 600; }

/* ===================================================================
   4. KPI cards
   =================================================================== */
.fsp-kpi-card {
  box-sizing: border-box;
  min-height: 140px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  padding: 18px 20px;
  box-shadow: var(--sh-card);
}
.fsp-kpi-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.fsp-kpi-title {
  font-size: 0.84rem;
  font-weight: 500;
  line-height: 1.35;
  color: var(--text-2);
}
.fsp-kpi-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.fsp-kpi-value {
  font-size: 1.7rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  line-height: 1.15;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
  text-wrap: balance;
}
.fsp-kpi-foot {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 10px;
  min-height: 24px;
}
.fsp-kpi-sub {
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--text-3);
}

/* Equal-height KPI rows (progressive enhancement; falls back to min-height) */
@supports selector(:has(*)) {
  .stApp [data-testid="stHorizontalBlock"]:has(.fsp-kpi-card) { align-items: stretch; }
  .stApp [data-testid="stColumn"]:has(.fsp-kpi-card) [data-testid="stVerticalBlock"],
  .stApp [data-testid="stColumn"]:has(.fsp-kpi-card) [data-testid="stElementContainer"],
  .stApp [data-testid="stColumn"]:has(.fsp-kpi-card) [data-testid="stMarkdown"],
  .stApp [data-testid="stColumn"]:has(.fsp-kpi-card) [data-testid="stMarkdownContainer"],
  .stApp [data-testid="column"]:has(.fsp-kpi-card) [data-testid="stVerticalBlock"],
  .stApp [data-testid="column"]:has(.fsp-kpi-card) .element-container,
  .stApp [data-testid="column"]:has(.fsp-kpi-card) .stMarkdown { height: 100%; }
}

/* ===================================================================
   5. Badges
   =================================================================== */
.fsp-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px 3px 8px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.3;
  white-space: nowrap;
}
.fsp-badge::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.7;
}
.fsp-badge-success { background: var(--success-soft); color: var(--success); border: 1px solid var(--success-line); }
.fsp-badge-danger  { background: var(--danger-soft);  color: var(--danger);  border: 1px solid var(--danger-line); }
.fsp-badge-warning { background: var(--warning-soft); color: var(--warning); border: 1px solid var(--warning-line); }
.fsp-badge-info    { background: var(--info-soft);    color: var(--info);    border: 1px solid var(--info-line); }
.fsp-badge-neutral { background: var(--surface-2);    color: var(--text-2);  border: 1px solid var(--line); }

/* ===================================================================
   6. Sidebar
   =================================================================== */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child { background: var(--ink); border-right: none; }
[data-testid="stSidebarUserContent"] { padding: 0.5rem 1rem 1.5rem 1rem; }
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] svg { color: rgba(255, 255, 255, 0.7); }
[data-testid="stSidebar"] :focus-visible { outline-color: rgba(255, 255, 255, 0.7); }

.fsp-brand { padding: 4px 4px 18px 4px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 8px; }
.fsp-brand-row { display: flex; align-items: center; gap: 12px; }
.fsp-brand-mark {
  width: 38px; height: 38px; flex-shrink: 0;
  border-radius: var(--r-sm);
  background: var(--grape);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
  display: flex; align-items: center; justify-content: center;
}
.fsp-brand-name { font-size: 1.02rem; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; color: #FFFFFF; }
.fsp-brand-sub { font-size: 0.76rem; font-weight: 500; line-height: 1.3; color: var(--lilac); margin-top: 2px; }
.fsp-brand-model {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: var(--r-sm);
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.09);
}
.fsp-brand-model-label { font-size: 0.74rem; font-weight: 500; color: var(--lilac); }
.fsp-brand-model-name { font-size: 0.88rem; font-weight: 600; line-height: 1.35; color: #FFFFFF; margin-top: 4px; }
.fsp-brand-tau {
  display: inline-block;
  margin-top: 8px;
  padding: 2px 9px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--almond);
  font-size: 0.72rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
  width: 100%;
  margin: 0;
  padding: 9px 12px;
  border-radius: var(--r-sm);
  cursor: pointer;
  transition: background 0.15s ease;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] p {
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.15s ease;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover { background: rgba(255, 255, 255, 0.07); }
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover p { color: #FFFFFF; }
@supports selector(:has(*)) {
  [data-testid="stSidebar"] label[data-baseweb="radio"] > div:not(:has([data-testid="stMarkdownContainer"])) { display: none; }
  [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(255, 255, 255, 0.12);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  }
  [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p { color: #FFFFFF; font-weight: 600; }
}

/* ===================================================================
   7. Buttons
   =================================================================== */
.stApp .stButton > button,
.stApp .stDownloadButton > button,
.stApp [data-testid^="stBaseButton"] {
  min-height: 40px;
  padding: 0.5rem 1.1rem;
  border-radius: var(--r-sm);
  font-size: 0.88rem;
  font-weight: 600;
  letter-spacing: -0.005em;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.stApp .stButton > button p,
.stApp .stDownloadButton > button p,
.stApp [data-testid^="stBaseButton"] p { color: inherit; font-weight: 600; font-size: 0.88rem; }

.stApp .stButton > button[kind="secondary"],
.stApp .stDownloadButton > button,
.stApp [data-testid="stBaseButton-secondary"] {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--line-strong);
  box-shadow: 0 1px 1px rgba(34, 34, 59, 0.04);
}
.stApp .stButton > button[kind="secondary"]:hover,
.stApp .stDownloadButton > button:hover,
.stApp [data-testid="stBaseButton-secondary"]:hover {
  background: var(--surface-2);
  border-color: var(--lilac);
  color: var(--ink);
  box-shadow: var(--sh-card);
}

.stApp .stButton > button[kind="primary"],
.stApp [data-testid="stBaseButton-primary"] {
  background: var(--ink);
  color: #FFFFFF;
  border: 1px solid var(--ink);
  box-shadow: 0 1px 2px rgba(34, 34, 59, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.stApp .stButton > button[kind="primary"]:hover,
.stApp [data-testid="stBaseButton-primary"]:hover {
  background: var(--grape);
  border-color: var(--grape);
  color: #FFFFFF;
  box-shadow: var(--sh-hover);
}
.stApp .stButton > button:active,
.stApp .stDownloadButton > button:active { transform: translateY(1px); }

/* ===================================================================
   8. Inputs, selects, sliders, checkboxes, uploader
   =================================================================== */
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label {
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--text-2);
}
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="input"],
.stApp [data-baseweb="textarea"] {
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: var(--r-sm);
  min-height: 42px;
  box-shadow: 0 1px 1px rgba(34, 34, 59, 0.03);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stApp [data-baseweb="base-input"] { background: transparent; border-radius: var(--r-sm); }
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="select"] input { font-size: 0.92rem; color: var(--text); }
.stApp [data-baseweb="select"] > div:hover,
.stApp [data-baseweb="input"]:hover { border-color: var(--lilac); }
.stApp [data-baseweb="select"] > div:focus-within,
.stApp [data-baseweb="input"]:focus-within,
.stApp [data-baseweb="textarea"]:focus-within {
  border-color: var(--grape);
  box-shadow: 0 0 0 3px rgba(74, 78, 105, 0.14);
}
.stApp [data-testid="stNumberInput"] button {
  background: transparent;
  color: var(--text-2);
  border-left: 1px solid var(--line);
}
.stApp [data-testid="stNumberInput"] button:hover { background: var(--surface-2); color: var(--ink); }

.stApp [data-baseweb="tag"] {
  background: var(--parchment);
  color: var(--ink);
  border-radius: 7px;
  font-weight: 500;
}
.stApp [data-baseweb="tag"] span { color: var(--ink); }

[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] [role="listbox"] {
  border-radius: var(--r-sm);
  border: 1px solid var(--line);
  box-shadow: var(--sh-hover);
}
[data-baseweb="popover"] [role="option"] { font-size: 0.9rem; }
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] { background: var(--surface-2); }

.stApp [data-testid="stCheckbox"] label p { font-size: 0.9rem; color: var(--text); }
.stApp [data-testid="stSlider"] [role="slider"] {
  background: var(--ink);
  box-shadow: 0 0 0 4px rgba(34, 34, 59, 0.12);
}
.stApp [data-testid="stSliderThumbValue"] { color: var(--ink); font-weight: 600; font-size: 0.8rem; }

.stApp [data-testid="stFileUploaderDropzone"] {
  background: var(--surface-2);
  border: 1px dashed var(--line-strong);
  border-radius: var(--r-md);
  padding: 20px 22px;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.stApp [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--grape); background: var(--surface); }

/* ===================================================================
   9. Tabs, expanders, alerts
   =================================================================== */
.stApp [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stApp button[data-baseweb="tab"] {
  padding: 10px 16px;
  margin: 0;
  background: transparent;
  border-radius: var(--r-sm) var(--r-sm) 0 0;
}
.stApp button[data-baseweb="tab"] p { font-size: 0.9rem; font-weight: 500; color: var(--text-2); }
.stApp button[data-baseweb="tab"]:hover p { color: var(--ink); }
.stApp button[data-baseweb="tab"][aria-selected="true"] p { color: var(--ink); font-weight: 600; }
.stApp [data-baseweb="tab-highlight"] { background: var(--ink); height: 2px; }
.stApp [data-baseweb="tab-border"] { background: transparent; }
.stApp [data-baseweb="tab-panel"] { padding-top: 1.1rem; }

.stApp [data-testid="stExpander"] details {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  box-shadow: var(--sh-card);
  overflow: hidden;
}
.stApp [data-testid="stExpander"] summary { padding: 0.85rem 1.1rem; }
.stApp [data-testid="stExpander"] summary:hover { background: var(--surface-2); }
.stApp [data-testid="stExpander"] summary p { font-size: 0.92rem; font-weight: 500; color: var(--ink); }
.stApp [data-testid="stExpander"] details[open] > summary { border-bottom: 1px solid var(--line); }
.stApp [data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 1rem 1.1rem 1.1rem 1.1rem; }

.stApp [data-testid="stAlert"] { border-radius: var(--r-md); }
.stApp [data-testid="stAlert"] > div {
  border-radius: var(--r-md);
  border: 1px solid rgba(34, 34, 59, 0.08);
  padding: 0.95rem 1.15rem;
}
.stApp [data-testid="stAlert"] p { font-size: 0.9rem; line-height: 1.6; }

/* ===================================================================
   10. Data surfaces: dataframes, charts, native metrics
   =================================================================== */
.stApp [data-testid="stDataFrame"] {
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  overflow: hidden;
  box-shadow: var(--sh-card);
}
.stApp [data-testid="stPlotlyChart"] {
  box-sizing: border-box;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  box-shadow: var(--sh-card);
  padding: 6px 6px 2px 6px;
  overflow: hidden;
}
.stApp [data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  padding: 16px 20px;
  box-shadow: var(--sh-card);
}
.stApp [data-testid="stMetricLabel"] p { font-size: 0.84rem; font-weight: 500; color: var(--text-2); }
.stApp [data-testid="stMetricValue"] { font-size: 1.7rem; font-weight: 600; letter-spacing: -0.025em; color: var(--ink); }

/* ===================================================================
   11. Footer
   =================================================================== */
.fsp-footer {
  margin-top: 32px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px 24px;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--text-3);
}
.fsp-footer strong { font-weight: 600; color: var(--text-2); }

/* ===================================================================
   12. Reduced motion
   =================================================================== */
@media (prefers-reduced-motion: reduce) {
  .stApp .block-container, .stApp [data-testid="stMainBlockContainer"] { animation: none !important; }
  .stApp *, .stApp *::before, .stApp *::after { transition: none !important; }
}
"""

# Blank lines are stripped so Streamlit's markdown parser never splits the <style> block.
CUSTOM_CSS = "\n".join(
    line for line in ("<style>\n" + _FONT_IMPORT + _ROOT_VARS + _BASE_CSS + "</style>").splitlines()
    if line.strip()
)


# ---------------------------------------------------------------------------
# Component helpers
# NOTE: each helper returns HTML with no blank lines. Streamlit's markdown
# parser ends an HTML block at the first blank line, so stray whitespace
# lines would leak raw tags into the page.
# ---------------------------------------------------------------------------
_BADGE_TYPES = ("success", "danger", "warning", "info", "neutral")


def kpi_card_html(title: str, value: str, subtitle: str = "",
                  icon_name: str = "bar-chart",
                  badge_text: str = "", badge_type: str = "neutral",
                  bg_tint: str = SURFACE) -> str:
    """KPI card: title + tinted icon, large value, then badge and caption."""
    safe_title = _html.escape(str(title))
    safe_value = _html.escape(str(value))
    safe_sub   = _html.escape(str(subtitle))
    safe_badge = _html.escape(str(badge_text))

    if badge_type not in _BADGE_TYPES:
        badge_type = "neutral"

    icon_tint_map = {"success": SUCCESS, "danger": DANGER, "warning": WARNING,
                     "info": INFO, "neutral": TEXT_MUTED}
    icon_bg_map = {"success": SUCCESS_SOFT, "danger": DANGER_SOFT, "warning": WARNING_SOFT,
                   "info": INFO_SOFT, "neutral": SURFACE_SUBTLE}
    ic_svg = icon(icon_name, color=icon_tint_map[badge_type], size=17)

    badge_html = f'<span class="fsp-badge fsp-badge-{badge_type}">{safe_badge}</span>' if badge_text else ""
    sub_html   = f'<span class="fsp-kpi-sub">{safe_sub}</span>' if subtitle else ""

    return "".join([
        f'<div class="fsp-kpi-card" style="background: {bg_tint};">',
        '<div class="fsp-kpi-top">',
        f'<span class="fsp-kpi-title">{safe_title}</span>',
        f'<span class="fsp-kpi-icon" style="background: {icon_bg_map[badge_type]};">{ic_svg}</span>',
        '</div>',
        f'<div class="fsp-kpi-value">{safe_value}</div>',
        f'<div class="fsp-kpi-foot">{badge_html}{sub_html}</div>',
        '</div>',
    ])


def header_banner_html(screen_num: str, title: str, subtitle: str,
                       badge: str = "", icon_name: str = "shield") -> str:
    """Compact page header: icon tile, title, subtitle, hairline underneath."""
    ic_svg = icon(icon_name, color=SPACE_INDIGO, size=22)
    aside = (f'<div class="fsp-page-header-aside"><span class="fsp-badge fsp-badge-neutral">'
             f'{_html.escape(str(badge))}</span></div>') if badge else ""
    return "".join([
        '<div class="fsp-page-header">',
        f'<div class="fsp-page-header-icon">{ic_svg}</div>',
        '<div class="fsp-page-header-text">',
        f'<h1 class="fsp-page-header-title">{_html.escape(title)}</h1>',
        f'<p class="fsp-page-header-subtitle">{_html.escape(subtitle)}</p>',
        '</div>',
        aside,
        '</div>',
    ])


def section_title_html(text: str, icon_name: str = "bar-chart") -> str:
    """Consistent section heading with inline SVG icon."""
    ic_svg = icon(icon_name, color=DUSTY_GRAPE, size=18)
    return f'<div class="fsp-section-title">{ic_svg}<span>{_html.escape(text)}</span></div>'


def sidebar_brand_html(model_name: str, threshold: float) -> str:
    """Sidebar brand block with the active model summarised underneath."""
    shield_svg = icon("shield", color=TEXT_ON_DARK, size=20)
    return "".join([
        '<div class="fsp-brand">',
        '<div class="fsp-brand-row">',
        f'<div class="fsp-brand-mark">{shield_svg}</div>',
        '<div>',
        '<div class="fsp-brand-name">Food Safety</div>',
        '<div class="fsp-brand-sub">Prioritiser v2.1</div>',
        '</div>',
        '</div>',
        '<div class="fsp-brand-model">',
        '<div class="fsp-brand-model-label">Active model</div>',
        f'<div class="fsp-brand-model-name">{_html.escape(model_name)}</div>',
        f'<span class="fsp-brand-tau">&tau; = {threshold:.2f}</span>',
        '</div>',
        '</div>',
    ])


def footer_html() -> str:
    """Minimal, accurate footer."""
    return "".join([
        '<div class="fsp-footer">',
        '<div><strong>Food Safety Inspection Prioritiser</strong> &middot; '
        'Chicago Department of Public Health Open Data (2010\u20132019)</div>',
        '<div>DSC306 Data Mining &middot; Production Ready ML</div>',
        '</div>',
    ])


def get_plotly_layout(height: int = 380, title: str = "") -> dict:
    """Plotly layout dict aligned to the design system."""
    font = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"
    grid = "#F1ECE9"
    axis = dict(
        gridcolor=grid,
        gridwidth=1,
        linecolor=BORDER,
        zeroline=False,
        ticks="outside",
        tickcolor=BORDER,
        ticklen=4,
        tickfont=dict(size=11, color=TEXT_SECONDARY),
        title=dict(font=dict(size=12, color=TEXT_SECONDARY), standoff=12),
        automargin=True,
    )
    layout = dict(
        height=height,
        margin=dict(l=56, r=28, t=68 if title else 28, b=52),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SURFACE,
        font=dict(family=font, color=TEXT_PRIMARY, size=12),
        colorway=[SPACE_INDIGO, DUSTY_GRAPE, LILAC_ASH, ALMOND_SILK, "#6B5B73"],
        xaxis=dict(axis),
        yaxis=dict(axis),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            font=dict(size=11, color=TEXT_SECONDARY),
            title=dict(text=""),
        ),
        hoverlabel=dict(
            bgcolor=SPACE_INDIGO,
            font=dict(family=font, size=12, color=TEXT_ON_DARK),
            bordercolor=DUSTY_GRAPE,
        ),
    )
    if title:
        layout["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(family=font, size=15, color=SPACE_INDIGO),
            x=0,
            xanchor="left",
            y=0.97,
            yanchor="top",
            pad=dict(l=10, t=10),
        )
    return layout

# """
# ui_theme.py - Soft Editorial Analytics Design System
# for the Food Safety Inspection Prioritiser.

# Implements the muted indigo–mauve palette defined in STYLE.md,
# Inter typography, compact page headers with inline SVG icons,
# KPI cards, consistent spacing, and restrained CSS animations.
# """

# import html as _html

# # ---------------------------------------------------------------------------
# # Palette tokens (STYLE.md §2)
# # ---------------------------------------------------------------------------
# # Brand palette
# SPACE_INDIGO   = "#22223B"
# DUSTY_GRAPE    = "#4A4E69"
# LILAC_ASH      = "#9A8C98"
# ALMOND_SILK    = "#C9ADA7"
# PARCHMENT      = "#F2E9E4"

# # Interface surfaces
# APP_BG         = "#FAF8F6"
# SURFACE        = "#FFFFFF"
# SURFACE_SUBTLE = "#F6F2F0"
# BORDER         = "#E7E0DD"
# BORDER_STRONG  = "#D6CBC8"

# # Text
# TEXT_PRIMARY    = "#22223B"
# TEXT_SECONDARY  = "#625E6A"
# TEXT_MUTED      = "#77717B"
# TEXT_ON_DARK    = "#FFFFFF"

# # Semantic status
# SUCCESS        = "#287A58"
# SUCCESS_SOFT   = "#E7F3EC"
# WARNING        = "#946200"
# WARNING_SOFT   = "#FBF1D8"
# DANGER         = "#B4233C"
# DANGER_SOFT    = "#FBE9EC"
# INFO           = "#365C87"
# INFO_SOFT      = "#EAF0F7"

# # Shape & depth
# RADIUS_SM      = "8px"
# RADIUS_MD      = "12px"
# RADIUS_LG      = "16px"
# SHADOW_CARD    = "0 2px 10px rgba(34, 34, 59, 0.045)"
# SHADOW_HOVER   = "0 5px 16px rgba(34, 34, 59, 0.08)"

# # --- Backward-compat aliases so app.py imports keep working ---
# NAVY           = SPACE_INDIGO
# PRIMARY_BLUE   = DUSTY_GRAPE
# SOFT_LAVENDER  = INFO_SOFT
# LAVENDER_ACCENT = DUSTY_GRAPE
# SOFT_MINT      = SUCCESS_SOFT
# SUCCESS_GREEN  = SUCCESS
# SOFT_AMBER     = WARNING_SOFT
# WARNING_AMBER  = WARNING
# SOFT_ROSE      = DANGER_SOFT
# DANGER_RED     = DANGER
# BG_MAIN        = APP_BG
# BG_CARD        = SURFACE
# TEXT_MAIN      = TEXT_PRIMARY
# BORDER_COLOR   = BORDER

# # ---------------------------------------------------------------------------
# # Inline SVG icon library — consistent line-icon family (STYLE.md §4, §6)
# # All icons are 18×18 stroke-based, inline-friendly, no external dependency.
# # ---------------------------------------------------------------------------
# _ICON_STYLE = 'xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

# ICONS = {
#     # Navigation / page headers
#     "database":     f'<svg {_ICON_STYLE}><path d="M12 2C6.5 2 2 4.2 2 7v10c0 2.8 4.5 5 10 5s10-2.2 10-5V7c0-2.8-4.5-5-10-5z"/><path d="M2 12c0 2.8 4.5 5 10 5s10-2.2 10-5"/><path d="M2 7c0 2.8 4.5 5 10 5s10-2.2 10-5"/></svg>',
#     "bar-chart":    f'<svg {_ICON_STYLE}><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>',
#     "crosshair":    f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>',
#     "layers":       f'<svg {_ICON_STYLE}><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
#     "sliders":      f'<svg {_ICON_STYLE}><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
#     "map-pin":      f'<svg {_ICON_STYLE}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
#     # KPI icons
#     "file-text":    f'<svg {_ICON_STYLE}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
#     "alert-triangle": f'<svg {_ICON_STYLE}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
#     "calendar":     f'<svg {_ICON_STYLE}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
#     "cpu":          f'<svg {_ICON_STYLE}><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
#     "target":       f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
#     "search":       f'<svg {_ICON_STYLE}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
#     "zap":          f'<svg {_ICON_STYLE}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
#     "dollar-sign":  f'<svg {_ICON_STYLE}><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
#     "shield":       f'<svg {_ICON_STYLE}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
#     "activity":     f'<svg {_ICON_STYLE}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
#     "check-circle": f'<svg {_ICON_STYLE}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
#     "upload":       f'<svg {_ICON_STYLE}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
#     "settings":     f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
#     "users":        f'<svg {_ICON_STYLE}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
#     "clock":        f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
#     "trending-up":  f'<svg {_ICON_STYLE}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
#     "filter":       f'<svg {_ICON_STYLE}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
#     "download":     f'<svg {_ICON_STYLE}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
#     "book-open":    f'<svg {_ICON_STYLE}><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
#     "grid":         f'<svg {_ICON_STYLE}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
#     "box":          f'<svg {_ICON_STYLE}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
#     "pie-chart":    f'<svg {_ICON_STYLE}><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
#     "award":        f'<svg {_ICON_STYLE}><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
#     "truck":        f'<svg {_ICON_STYLE}><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
#     "clipboard":    f'<svg {_ICON_STYLE}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>',
#     "printer":      f'<svg {_ICON_STYLE}><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>',
# }


# def icon(name: str, color: str = TEXT_MUTED, size: int = 18) -> str:
#     """Return an inline SVG icon string. Falls back to empty string for unknown names."""
#     svg = ICONS.get(name, "")
#     if not svg:
#         return ""
#     # Patch color and size into the SVG
#     svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
#     svg = svg.replace('width="18"', f'width="{size}"').replace('height="18"', f'height="{size}"')
#     return svg


# # ---------------------------------------------------------------------------
# # Global CSS (STYLE.md §2-§9)
# # ---------------------------------------------------------------------------
# CUSTOM_CSS = f"""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

# /* --- Base typography & background --- */
# html, body, [class*="css"], .stApp {{
#     font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
#     color: {TEXT_PRIMARY};
#     background-color: {APP_BG};
# }}

# /* --- Smooth page-load fade (§8) --- */
# @keyframes fadeIn {{
#     from {{ opacity: 0; transform: translateY(4px); }}
#     to   {{ opacity: 1; transform: translateY(0); }}
# }}

# .main .block-container {{
#     animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
#     padding-top: 1.6rem;
#     padding-bottom: 3rem;
#     max-width: 1200px;
# }}

# /* --- Sidebar: Space Indigo (§5) --- */
# [data-testid="stSidebar"] {{
#     background-color: {SPACE_INDIGO};
#     border-right: none;
# }}

# [data-testid="stSidebar"] > div:first-child {{
#     padding-top: 0.8rem;
# }}

# /* Sidebar text defaults */
# [data-testid="stSidebar"],
# [data-testid="stSidebar"] * {{
#     color: {TEXT_ON_DARK} !important;
# }}

# /* Sidebar radio navigation */
# [data-testid="stSidebar"] .stRadio > div {{
#     gap: 2px;
# }}

# [data-testid="stSidebar"] .stRadio label {{
#     background: transparent;
#     padding: 9px 14px;
#     border-radius: {RADIUS_SM};
#     transition: background 0.18s ease, color 0.18s ease;
#     border: 1px solid transparent;
#     cursor: pointer;
#     font-size: 0.88rem;
#     font-weight: 500;
#     color: rgba(255,255,255,0.72) !important;
# }}

# [data-testid="stSidebar"] .stRadio label:hover {{
#     background: {DUSTY_GRAPE};
#     color: {TEXT_ON_DARK} !important;
# }}

# [data-testid="stSidebar"] .stRadio label[data-checked="true"],
# [data-testid="stSidebar"] .stRadio label[aria-checked="true"] {{
#     background: {DUSTY_GRAPE};
#     color: {TEXT_ON_DARK} !important;
#     font-weight: 600;
# }}

# /* Sidebar heading override */
# [data-testid="stSidebar"] .stRadio > label {{
#     color: rgba(255,255,255,0.5) !important;
#     font-size: 0.72rem;
#     text-transform: uppercase;
#     letter-spacing: 0.06em;
#     font-weight: 600;
# }}

# /* --- Buttons (§6) --- */
# .stButton > button {{
#     font-family: 'Inter', sans-serif;
#     font-weight: 600;
#     border-radius: {RADIUS_SM};
#     transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
#     box-shadow: none;
#     border: 1px solid {BORDER};
#     font-size: 0.88rem;
# }}

# .stButton > button:hover {{
#     transform: translateY(-1px);
#     box-shadow: {SHADOW_HOVER};
#     border-color: {BORDER_STRONG};
# }}

# .stButton > button[kind="primary"] {{
#     background: {SPACE_INDIGO};
#     border: none;
#     color: {TEXT_ON_DARK};
# }}

# .stButton > button[kind="primary"]:hover {{
#     background: {DUSTY_GRAPE};
#     box-shadow: {SHADOW_HOVER};
# }}

# /* --- Metric cards (Streamlit native st.metric) --- */
# [data-testid="stMetric"] {{
#     background-color: {SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: {RADIUS_MD};
#     padding: 16px 20px;
#     box-shadow: {SHADOW_CARD};
#     transition: box-shadow 0.2s ease, border-color 0.2s ease;
# }}

# [data-testid="stMetric"]:hover {{
#     border-color: {BORDER_STRONG};
#     box-shadow: {SHADOW_HOVER};
# }}

# [data-testid="stMetricLabel"] {{
#     font-size: 0.78rem !important;
#     font-weight: 600 !important;
#     color: {TEXT_MUTED} !important;
#     text-transform: uppercase;
#     letter-spacing: 0.04em;
# }}

# [data-testid="stMetricValue"] {{
#     font-size: 1.7rem !important;
#     font-weight: 700 !important;
#     color: {TEXT_PRIMARY} !important;
# }}

# /* --- Custom cards --- */
# .fsp-card {{
#     background: {SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: {RADIUS_MD};
#     padding: 20px 24px;
#     margin-bottom: 16px;
#     box-shadow: {SHADOW_CARD};
#     transition: box-shadow 0.2s ease, border-color 0.2s ease;
# }}

# .fsp-card:hover {{
#     box-shadow: {SHADOW_HOVER};
#     border-color: {BORDER_STRONG};
# }}

# /* --- KPI grid & cards --- */
# .fsp-kpi-grid {{
#     display: grid;
#     grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
#     gap: 16px;
#     margin: 16px 0 24px 0;
# }}

# .fsp-kpi-card {{
#     background: {SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: {RADIUS_MD};
#     padding: 16px 20px;
#     box-shadow: {SHADOW_CARD};
#     transition: box-shadow 0.22s ease, border-color 0.22s ease;
#     display: flex;
#     flex-direction: column;
#     justify-content: space-between;
# }}

# .fsp-kpi-card:hover {{
#     box-shadow: {SHADOW_HOVER};
#     border-color: {BORDER_STRONG};
# }}

# .fsp-kpi-top {{
#     display: flex;
#     justify-content: space-between;
#     align-items: center;
#     margin-bottom: 8px;
# }}

# .fsp-kpi-title {{
#     font-size: 0.76rem;
#     font-weight: 600;
#     color: {TEXT_MUTED};
#     text-transform: uppercase;
#     letter-spacing: 0.04em;
# }}

# .fsp-kpi-icon {{
#     width: 34px;
#     height: 34px;
#     border-radius: {RADIUS_SM};
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     flex-shrink: 0;
# }}

# .fsp-kpi-value {{
#     font-size: 1.7rem;
#     font-weight: 700;
#     color: {SPACE_INDIGO};
#     line-height: 1.2;
#     margin-bottom: 4px;
# }}

# .fsp-kpi-sub {{
#     font-size: 0.8rem;
#     color: {TEXT_MUTED};
#     display: flex;
#     align-items: center;
#     gap: 6px;
# }}

# /* --- Badges --- */
# .fsp-badge {{
#     display: inline-flex;
#     align-items: center;
#     gap: 4px;
#     padding: 3px 10px;
#     border-radius: 9999px;
#     font-size: 0.72rem;
#     font-weight: 600;
#     letter-spacing: 0.02em;
#     line-height: 1.3;
# }}

# .fsp-badge-success {{
#     background: {SUCCESS_SOFT};
#     color: {SUCCESS};
#     border: 1px solid #C3DFD0;
# }}

# .fsp-badge-danger {{
#     background: {DANGER_SOFT};
#     color: {DANGER};
#     border: 1px solid #F0C6CC;
# }}

# .fsp-badge-warning {{
#     background: {WARNING_SOFT};
#     color: {WARNING};
#     border: 1px solid #EFE0B4;
# }}

# .fsp-badge-info {{
#     background: {INFO_SOFT};
#     color: {INFO};
#     border: 1px solid #C8D9E8;
# }}

# .fsp-badge-neutral {{
#     background: {SURFACE_SUBTLE};
#     color: {TEXT_SECONDARY};
#     border: 1px solid {BORDER};
# }}

# /* --- Compact page header (§4, §6) --- */
# .fsp-page-header {{
#     display: flex;
#     align-items: flex-start;
#     gap: 14px;
#     margin-bottom: 24px;
#     padding-bottom: 20px;
#     border-bottom: 1px solid {BORDER};
# }}

# .fsp-page-header-icon {{
#     flex-shrink: 0;
#     width: 38px;
#     height: 38px;
#     border-radius: {RADIUS_SM};
#     background: {PARCHMENT};
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     margin-top: 2px;
# }}

# .fsp-page-header-text {{
#     flex: 1;
#     min-width: 0;
# }}

# .fsp-page-header-title {{
#     font-size: 1.8rem;
#     font-weight: 600;
#     color: {SPACE_INDIGO};
#     letter-spacing: -0.01em;
#     margin: 0 0 4px 0;
#     line-height: 1.25;
# }}

# .fsp-page-header-subtitle {{
#     font-size: 0.92rem;
#     color: {TEXT_SECONDARY};
#     margin: 0;
#     line-height: 1.5;
#     max-width: 800px;
# }}

# /* --- Section titles --- */
# .fsp-section-title {{
#     font-size: 1.2rem;
#     font-weight: 600;
#     color: {SPACE_INDIGO};
#     margin: 28px 0 12px 0;
#     display: flex;
#     align-items: center;
#     gap: 8px;
# }}

# /* --- DataFrames --- */
# [data-testid="stDataFrame"] {{
#     border: 1px solid {BORDER};
#     border-radius: {RADIUS_MD};
#     overflow: hidden;
#     box-shadow: 0 1px 4px rgba(34, 34, 59, 0.02);
# }}

# /* --- Footer --- */
# .fsp-footer {{
#     margin-top: 48px;
#     padding-top: 16px;
#     border-top: 1px solid {BORDER};
#     display: flex;
#     justify-content: space-between;
#     align-items: center;
#     font-size: 0.78rem;
#     color: {TEXT_MUTED};
# }}

# /* --- Reduced motion (§8) --- */
# @media (prefers-reduced-motion: reduce) {{
#     *, .main .block-container, .fsp-card, .fsp-kpi-card, .stButton > button {{
#         animation: none !important;
#         transition: none !important;
#         transform: none !important;
#     }}
# }}
# </style>
# """


# # ---------------------------------------------------------------------------
# # Component helpers
# # ---------------------------------------------------------------------------

# def kpi_card_html(title: str, value: str, subtitle: str = "",
#                   icon_name: str = "bar-chart",
#                   badge_text: str = "", badge_type: str = "neutral",
#                   bg_tint: str = SURFACE) -> str:
#     """Generate HTML for a KPI card using inline SVG icons (no emojis)."""
#     safe_title = _html.escape(str(title))
#     safe_value = _html.escape(str(value))
#     safe_sub   = _html.escape(str(subtitle))
#     safe_badge = _html.escape(str(badge_text))

#     # Determine icon tint color based on badge type
#     icon_tint_map = {
#         "success": SUCCESS,
#         "danger": DANGER,
#         "warning": WARNING,
#         "info": INFO,
#         "neutral": TEXT_MUTED,
#     }
#     icon_bg_map = {
#         "success": SUCCESS_SOFT,
#         "danger":  DANGER_SOFT,
#         "warning": WARNING_SOFT,
#         "info":    INFO_SOFT,
#         "neutral": SURFACE_SUBTLE,
#     }
#     ic_color = icon_tint_map.get(badge_type, TEXT_MUTED)
#     ic_bg    = icon_bg_map.get(badge_type, SURFACE_SUBTLE)
#     ic_svg   = icon(icon_name, color=ic_color, size=18)

#     badge_html = f'<span class="fsp-badge fsp-badge-{badge_type}">{safe_badge}</span>' if badge_text else ''
#     sub_html   = f'<div class="fsp-kpi-sub">{safe_sub}</div>' if subtitle else ''

#     return f"""
#     <div class="fsp-kpi-card" style="background: {bg_tint};">
#         <div class="fsp-kpi-top">
#             <span class="fsp-kpi-title">{safe_title}</span>
#             <span class="fsp-kpi-icon" style="background: {ic_bg};">{ic_svg}</span>
#         </div>
#         <div class="fsp-kpi-value">{safe_value}</div>
#         <div style="display: flex; justify-content: space-between; align-items: center;">
#             {sub_html}
#             {badge_html}
#         </div>
#     </div>
#     """


# def header_banner_html(screen_num: str, title: str, subtitle: str,
#                        badge: str = "", icon_name: str = "shield") -> str:
#     """Compact, consistent page header (§4, §6). No gradient banner."""
#     ic_svg = icon(icon_name, color=SPACE_INDIGO, size=22)
#     return f"""
#     <div class="fsp-page-header">
#         <div class="fsp-page-header-icon">{ic_svg}</div>
#         <div class="fsp-page-header-text">
#             <h1 class="fsp-page-header-title">{_html.escape(title)}</h1>
#             <p class="fsp-page-header-subtitle">{_html.escape(subtitle)}</p>
#         </div>
#     </div>
#     """


# def section_title_html(text: str, icon_name: str = "bar-chart") -> str:
#     """Consistent section heading with inline SVG icon."""
#     ic_svg = icon(icon_name, color=DUSTY_GRAPE, size=18)
#     return f'<div class="fsp-section-title">{ic_svg} {_html.escape(text)}</div>'


# def sidebar_brand_html(model_name: str, threshold: float) -> str:
#     """Sidebar brand block: Space Indigo background with white text."""
#     shield_svg = icon("shield", color=TEXT_ON_DARK, size=20)
#     return f"""
#     <div style="padding: 12px 8px 16px 8px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px;">
#         <div style="display: flex; align-items: center; gap: 10px;">
#             <div style="width: 36px; height: 36px; border-radius: {RADIUS_SM}; background: {DUSTY_GRAPE};
#                         display: flex; align-items: center; justify-content: center;">
#                 {shield_svg}
#             </div>
#             <div>
#                 <div style="font-size: 1rem; font-weight: 700; color: {TEXT_ON_DARK}; line-height: 1.2;">
#                     Food Safety
#                 </div>
#                 <div style="font-size: 0.7rem; font-weight: 500; color: {LILAC_ASH}; text-transform: uppercase; letter-spacing: 0.05em;">
#                     Prioritiser v2.1
#                 </div>
#             </div>
#         </div>
#         <div style="margin-top: 12px; padding: 8px 10px; border-radius: {RADIUS_SM};
#                     background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1);">
#             <div style="font-size: 0.68rem; color: {LILAC_ASH}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">
#                 Active Model
#             </div>
#             <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3px;">
#                 <span style="font-size: 0.8rem; font-weight: 600; color: {TEXT_ON_DARK};">
#                     {_html.escape(model_name)}
#                 </span>
#                 <span style="font-size: 0.68rem; font-weight: 600; color: {ALMOND_SILK};
#                              padding: 2px 7px; border-radius: 9999px; background: rgba(255,255,255,0.1);">
#                     &tau; = {threshold:.2f}
#                 </span>
#             </div>
#         </div>
#     </div>
#     """


# def footer_html() -> str:
#     """Minimal, accurate footer."""
#     return f"""
#     <div class="fsp-footer">
#         <div>
#             <strong>Food Safety Inspection Prioritiser</strong> · Chicago Department of Public Health Open Data (2010–2019)
#         </div>
#         <div>
#             DSC306 Data Mining · Production Ready ML
#         </div>
#     </div>
#     """


# def get_plotly_layout(height: int = 380, title: str = "") -> dict:
#     """Plotly layout dict aligned to design system colors (§6)."""
#     layout = dict(
#         height=height,
#         margin=dict(l=48, r=30, t=50 if title else 25, b=44),
#         paper_bgcolor="rgba(0,0,0,0)",
#         plot_bgcolor=SURFACE,
#         font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12),
#         xaxis=dict(
#             gridcolor=SURFACE_SUBTLE,
#             linecolor=BORDER,
#             zerolinecolor=BORDER,
#             tickfont=dict(size=11, color=TEXT_SECONDARY)
#         ),
#         yaxis=dict(
#             gridcolor=SURFACE_SUBTLE,
#             linecolor=BORDER,
#             zerolinecolor=BORDER,
#             tickfont=dict(size=11, color=TEXT_SECONDARY)
#         ),
#         legend=dict(
#             bgcolor="rgba(255,255,255,0.92)",
#             bordercolor=BORDER,
#             borderwidth=1,
#             font=dict(size=11, color=TEXT_PRIMARY)
#         ),
#         hoverlabel=dict(
#             bgcolor=SPACE_INDIGO,
#             font=dict(family="Inter, sans-serif", size=12, color=TEXT_ON_DARK),
#             bordercolor=DUSTY_GRAPE
#         )
#     )
#     if title:
#         layout["title"] = dict(
#             text=f"<b>{title}</b>",
#             font=dict(family="Inter, sans-serif", size=14, color=SPACE_INDIGO),
#             x=0.01,
#             y=0.96
#         )
#     return layout
