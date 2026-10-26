"""
ui_theme.py - Soft Editorial Analytics Design System
for the Food Safety Inspection Prioritiser.

Implements the muted indigo–mauve palette defined in STYLE.md,
Inter typography, compact page headers with inline SVG icons,
KPI cards, consistent spacing, and restrained CSS animations.
"""

import html as _html

# ---------------------------------------------------------------------------
# Palette tokens (STYLE.md §2)
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

# Shape & depth
RADIUS_SM      = "8px"
RADIUS_MD      = "12px"
RADIUS_LG      = "16px"
SHADOW_CARD    = "0 2px 10px rgba(34, 34, 59, 0.045)"
SHADOW_HOVER   = "0 5px 16px rgba(34, 34, 59, 0.08)"

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

# ---------------------------------------------------------------------------
# Inline SVG icon library — consistent line-icon family (STYLE.md §4, §6)
# All icons are 18×18 stroke-based, inline-friendly, no external dependency.
# ---------------------------------------------------------------------------
_ICON_STYLE = 'xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

ICONS = {
    # Navigation / page headers
    "database":     f'<svg {_ICON_STYLE}><path d="M12 2C6.5 2 2 4.2 2 7v10c0 2.8 4.5 5 10 5s10-2.2 10-5V7c0-2.8-4.5-5-10-5z"/><path d="M2 12c0 2.8 4.5 5 10 5s10-2.2 10-5"/><path d="M2 7c0 2.8 4.5 5 10 5s10-2.2 10-5"/></svg>',
    "bar-chart":    f'<svg {_ICON_STYLE}><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>',
    "crosshair":    f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>',
    "layers":       f'<svg {_ICON_STYLE}><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "sliders":      f'<svg {_ICON_STYLE}><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "map-pin":      f'<svg {_ICON_STYLE}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    # KPI icons
    "file-text":    f'<svg {_ICON_STYLE}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "alert-triangle": f'<svg {_ICON_STYLE}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "calendar":     f'<svg {_ICON_STYLE}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "cpu":          f'<svg {_ICON_STYLE}><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "target":       f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "search":       f'<svg {_ICON_STYLE}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "zap":          f'<svg {_ICON_STYLE}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "dollar-sign":  f'<svg {_ICON_STYLE}><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "shield":       f'<svg {_ICON_STYLE}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "activity":     f'<svg {_ICON_STYLE}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "check-circle": f'<svg {_ICON_STYLE}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "upload":       f'<svg {_ICON_STYLE}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "settings":     f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "users":        f'<svg {_ICON_STYLE}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "clock":        f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "trending-up":  f'<svg {_ICON_STYLE}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "filter":       f'<svg {_ICON_STYLE}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
    "download":     f'<svg {_ICON_STYLE}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "book-open":    f'<svg {_ICON_STYLE}><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    "grid":         f'<svg {_ICON_STYLE}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "box":          f'<svg {_ICON_STYLE}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
    "pie-chart":    f'<svg {_ICON_STYLE}><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "award":        f'<svg {_ICON_STYLE}><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
    "truck":        f'<svg {_ICON_STYLE}><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    "clipboard":    f'<svg {_ICON_STYLE}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>',
    "printer":      f'<svg {_ICON_STYLE}><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>',
}


def icon(name: str, color: str = TEXT_MUTED, size: int = 18) -> str:
    """Return an inline SVG icon string. Falls back to empty string for unknown names."""
    svg = ICONS.get(name, "")
    if not svg:
        return ""
    # Patch color and size into the SVG
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    svg = svg.replace('width="18"', f'width="{size}"').replace('height="18"', f'height="{size}"')
    return svg


# ---------------------------------------------------------------------------
# Global CSS (STYLE.md §2-§9)
# ---------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* --- Base typography & background --- */
html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: {TEXT_PRIMARY};
    background-color: {APP_BG};
}}

/* --- Smooth page-load fade (§8) --- */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.main .block-container {{
    animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}

/* --- Sidebar: Space Indigo (§5) --- */
[data-testid="stSidebar"] {{
    background-color: {SPACE_INDIGO};
    border-right: none;
}}

[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0.8rem;
}}

/* Sidebar text defaults */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {{
    color: {TEXT_ON_DARK} !important;
}}

/* Sidebar radio navigation */
[data-testid="stSidebar"] .stRadio > div {{
    gap: 2px;
}}

[data-testid="stSidebar"] .stRadio label {{
    background: transparent;
    padding: 9px 14px;
    border-radius: {RADIUS_SM};
    transition: background 0.18s ease, color 0.18s ease;
    border: 1px solid transparent;
    cursor: pointer;
    font-size: 0.88rem;
    font-weight: 500;
    color: rgba(255,255,255,0.72) !important;
}}

[data-testid="stSidebar"] .stRadio label:hover {{
    background: {DUSTY_GRAPE};
    color: {TEXT_ON_DARK} !important;
}}

[data-testid="stSidebar"] .stRadio label[data-checked="true"],
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] {{
    background: {DUSTY_GRAPE};
    color: {TEXT_ON_DARK} !important;
    font-weight: 600;
}}

/* Sidebar heading override */
[data-testid="stSidebar"] .stRadio > label {{
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}}

/* --- Buttons (§6) --- */
.stButton > button {{
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    border-radius: {RADIUS_SM};
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: none;
    border: 1px solid {BORDER};
    font-size: 0.88rem;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: {SHADOW_HOVER};
    border-color: {BORDER_STRONG};
}}

.stButton > button[kind="primary"] {{
    background: {SPACE_INDIGO};
    border: none;
    color: {TEXT_ON_DARK};
}}

.stButton > button[kind="primary"]:hover {{
    background: {DUSTY_GRAPE};
    box-shadow: {SHADOW_HOVER};
}}

/* --- Metric cards (Streamlit native st.metric) --- */
[data-testid="stMetric"] {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 16px 20px;
    box-shadow: {SHADOW_CARD};
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}

[data-testid="stMetric"]:hover {{
    border-color: {BORDER_STRONG};
    box-shadow: {SHADOW_HOVER};
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: {TEXT_MUTED} !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

[data-testid="stMetricValue"] {{
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: {TEXT_PRIMARY} !important;
}}

/* --- Custom cards --- */
.fsp-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: {SHADOW_CARD};
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}

.fsp-card:hover {{
    box-shadow: {SHADOW_HOVER};
    border-color: {BORDER_STRONG};
}}

/* --- KPI grid & cards --- */
.fsp-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 16px 0 24px 0;
}}

.fsp-kpi-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 16px 20px;
    box-shadow: {SHADOW_CARD};
    transition: box-shadow 0.22s ease, border-color 0.22s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.fsp-kpi-card:hover {{
    box-shadow: {SHADOW_HOVER};
    border-color: {BORDER_STRONG};
}}

.fsp-kpi-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}}

.fsp-kpi-title {{
    font-size: 0.76rem;
    font-weight: 600;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

.fsp-kpi-icon {{
    width: 34px;
    height: 34px;
    border-radius: {RADIUS_SM};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.fsp-kpi-value {{
    font-size: 1.7rem;
    font-weight: 700;
    color: {SPACE_INDIGO};
    line-height: 1.2;
    margin-bottom: 4px;
}}

.fsp-kpi-sub {{
    font-size: 0.8rem;
    color: {TEXT_MUTED};
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* --- Badges --- */
.fsp-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.3;
}}

.fsp-badge-success {{
    background: {SUCCESS_SOFT};
    color: {SUCCESS};
    border: 1px solid #C3DFD0;
}}

.fsp-badge-danger {{
    background: {DANGER_SOFT};
    color: {DANGER};
    border: 1px solid #F0C6CC;
}}

.fsp-badge-warning {{
    background: {WARNING_SOFT};
    color: {WARNING};
    border: 1px solid #EFE0B4;
}}

.fsp-badge-info {{
    background: {INFO_SOFT};
    color: {INFO};
    border: 1px solid #C8D9E8;
}}

.fsp-badge-neutral {{
    background: {SURFACE_SUBTLE};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
}}

/* --- Compact page header (§4, §6) --- */
.fsp-page-header {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid {BORDER};
}}

.fsp-page-header-icon {{
    flex-shrink: 0;
    width: 38px;
    height: 38px;
    border-radius: {RADIUS_SM};
    background: {PARCHMENT};
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
}}

.fsp-page-header-text {{
    flex: 1;
    min-width: 0;
}}

.fsp-page-header-title {{
    font-size: 1.8rem;
    font-weight: 600;
    color: {SPACE_INDIGO};
    letter-spacing: -0.01em;
    margin: 0 0 4px 0;
    line-height: 1.25;
}}

.fsp-page-header-subtitle {{
    font-size: 0.92rem;
    color: {TEXT_SECONDARY};
    margin: 0;
    line-height: 1.5;
    max-width: 800px;
}}

/* --- Section titles --- */
.fsp-section-title {{
    font-size: 1.2rem;
    font-weight: 600;
    color: {SPACE_INDIGO};
    margin: 28px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* --- DataFrames --- */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD};
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(34, 34, 59, 0.02);
}}

/* --- Footer --- */
.fsp-footer {{
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid {BORDER};
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.78rem;
    color: {TEXT_MUTED};
}}

/* --- Reduced motion (§8) --- */
@media (prefers-reduced-motion: reduce) {{
    *, .main .block-container, .fsp-card, .fsp-kpi-card, .stButton > button {{
        animation: none !important;
        transition: none !important;
        transform: none !important;
    }}
}}
</style>
"""


# ---------------------------------------------------------------------------
# Component helpers
# ---------------------------------------------------------------------------

def kpi_card_html(title: str, value: str, subtitle: str = "",
                  icon_name: str = "bar-chart",
                  badge_text: str = "", badge_type: str = "neutral",
                  bg_tint: str = SURFACE) -> str:
    """Generate HTML for a KPI card using inline SVG icons (no emojis)."""
    safe_title = _html.escape(str(title))
    safe_value = _html.escape(str(value))
    safe_sub   = _html.escape(str(subtitle))
    safe_badge = _html.escape(str(badge_text))

    # Determine icon tint color based on badge type
    icon_tint_map = {
        "success": SUCCESS,
        "danger": DANGER,
        "warning": WARNING,
        "info": INFO,
        "neutral": TEXT_MUTED,
    }
    icon_bg_map = {
        "success": SUCCESS_SOFT,
        "danger":  DANGER_SOFT,
        "warning": WARNING_SOFT,
        "info":    INFO_SOFT,
        "neutral": SURFACE_SUBTLE,
    }
    ic_color = icon_tint_map.get(badge_type, TEXT_MUTED)
    ic_bg    = icon_bg_map.get(badge_type, SURFACE_SUBTLE)
    ic_svg   = icon(icon_name, color=ic_color, size=18)

    badge_html = f'<span class="fsp-badge fsp-badge-{badge_type}">{safe_badge}</span>' if badge_text else ''
    sub_html   = f'<div class="fsp-kpi-sub">{safe_sub}</div>' if subtitle else ''

    return f"""
    <div class="fsp-kpi-card" style="background: {bg_tint};">
        <div class="fsp-kpi-top">
            <span class="fsp-kpi-title">{safe_title}</span>
            <span class="fsp-kpi-icon" style="background: {ic_bg};">{ic_svg}</span>
        </div>
        <div class="fsp-kpi-value">{safe_value}</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            {sub_html}
            {badge_html}
        </div>
    </div>
    """


def header_banner_html(screen_num: str, title: str, subtitle: str,
                       badge: str = "", icon_name: str = "shield") -> str:
    """Compact, consistent page header (§4, §6). No gradient banner."""
    ic_svg = icon(icon_name, color=SPACE_INDIGO, size=22)
    return f"""
    <div class="fsp-page-header">
        <div class="fsp-page-header-icon">{ic_svg}</div>
        <div class="fsp-page-header-text">
            <h1 class="fsp-page-header-title">{_html.escape(title)}</h1>
            <p class="fsp-page-header-subtitle">{_html.escape(subtitle)}</p>
        </div>
    </div>
    """


def section_title_html(text: str, icon_name: str = "bar-chart") -> str:
    """Consistent section heading with inline SVG icon."""
    ic_svg = icon(icon_name, color=DUSTY_GRAPE, size=18)
    return f'<div class="fsp-section-title">{ic_svg} {_html.escape(text)}</div>'


def sidebar_brand_html(model_name: str, threshold: float) -> str:
    """Sidebar brand block: Space Indigo background with white text."""
    shield_svg = icon("shield", color=TEXT_ON_DARK, size=20)
    return f"""
    <div style="padding: 12px 8px 16px 8px; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 36px; height: 36px; border-radius: {RADIUS_SM}; background: {DUSTY_GRAPE};
                        display: flex; align-items: center; justify-content: center;">
                {shield_svg}
            </div>
            <div>
                <div style="font-size: 1rem; font-weight: 700; color: {TEXT_ON_DARK}; line-height: 1.2;">
                    Food Safety
                </div>
                <div style="font-size: 0.7rem; font-weight: 500; color: {LILAC_ASH}; text-transform: uppercase; letter-spacing: 0.05em;">
                    Prioritiser v2.1
                </div>
            </div>
        </div>
        <div style="margin-top: 12px; padding: 8px 10px; border-radius: {RADIUS_SM};
                    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 0.68rem; color: {LILAC_ASH}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">
                Active Model
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3px;">
                <span style="font-size: 0.8rem; font-weight: 600; color: {TEXT_ON_DARK};">
                    {_html.escape(model_name)}
                </span>
                <span style="font-size: 0.68rem; font-weight: 600; color: {ALMOND_SILK};
                             padding: 2px 7px; border-radius: 9999px; background: rgba(255,255,255,0.1);">
                    &tau; = {threshold:.2f}
                </span>
            </div>
        </div>
    </div>
    """


def footer_html() -> str:
    """Minimal, accurate footer."""
    return f"""
    <div class="fsp-footer">
        <div>
            <strong>Food Safety Inspection Prioritiser</strong> · Chicago Department of Public Health Open Data (2010–2019)
        </div>
        <div>
            DSC306 Data Mining · Production Ready ML
        </div>
    </div>
    """


def get_plotly_layout(height: int = 380, title: str = "") -> dict:
    """Plotly layout dict aligned to design system colors (§6)."""
    layout = dict(
        height=height,
        margin=dict(l=48, r=30, t=50 if title else 25, b=44),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SURFACE,
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12),
        xaxis=dict(
            gridcolor=SURFACE_SUBTLE,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(size=11, color=TEXT_SECONDARY)
        ),
        yaxis=dict(
            gridcolor=SURFACE_SUBTLE,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(size=11, color=TEXT_SECONDARY)
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(size=11, color=TEXT_PRIMARY)
        ),
        hoverlabel=dict(
            bgcolor=SPACE_INDIGO,
            font=dict(family="Inter, sans-serif", size=12, color=TEXT_ON_DARK),
            bordercolor=DUSTY_GRAPE
        )
    )
    if title:
        layout["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(family="Inter, sans-serif", size=14, color=SPACE_INDIGO),
            x=0.01,
            y=0.96
        )
    return layout
