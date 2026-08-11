"""
theme.py – CaliTrack visual identity & design system.

Design direction: "precision instrument panel" — professional, technical look.
Colors: cool porcelain surface + graphite ink + calibration teal/orange/red.
Fonts: Space Grotesk (display) / Inter (body) / JetBrains Mono (data).
"""
import streamlit as st

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":        "#F4F7F6",      # Cool porcelain background
    "surface":   "#FFFFFF",      # White surface
    "ink":       "#16211F",      # Graphite text
    "muted":     "#5B6B6A",      # Muted gray
    "line":      "#D9E1DF",      # Light divider
    "teal":      "#0E6E68",      # Calibration teal (primary accent)
    "teal_dark": "#0A4F4B",      # Darker teal
    "ok":        "#1E8E5A",      # Green (OK)
    "warn":      "#B9820F",      # Orange (Due soon)
    "bad":       "#B23A34",      # Red (Overdue)
}

STATUS_COLOR = {
    "ok":   (COLORS["ok"], "#E4F4EA"),    # Green + light green background
    "warn": (COLORS["warn"], "#FBF1DD"),  # Orange + light orange background
    "bad":  (COLORS["bad"], "#FBE8E6"),   # Red + light red background
}


def inject_theme():
    """Apply CSS design system to Streamlit app."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp {{
        background-color: {COLORS['bg']};
        color: {COLORS['ink']};
        font-family: 'Inter', sans-serif;
    }}

    h1, h2, h3 {{
        font-family: 'Space Grotesk', sans-serif;
        color: {COLORS['ink']};
    }}

    code, .ct-mono {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Sidebar – dark bezel */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['ink']};
        border-right: 1px solid {COLORS['teal_dark']};
    }}
    
    section[data-testid="stSidebar"] * {{
        color: #E8EEEC !important;
    }}

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {{
        background-color: {COLORS['teal']};
        color: #FFFFFF;
        border: 1px solid {COLORS['teal_dark']};
        border-radius: 3px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['teal_dark']};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def status_badge(state: str, label: str) -> str:
    """Return HTML for colored status badge (● colored dot + label).
    
    state: 'ok' | 'warn' | 'bad'
    label: e.g. "OK (214d left)", "Due in 5d", "Overdue (3d)"
    
    Usage: st.markdown(status_badge("ok", "OK (214d left)"), unsafe_allow_html=True)
    """
    color, soft = STATUS_COLOR.get(state, (COLORS["muted"], "#EEF2F1"))
    dot = (
        f'<span style="display:inline-block;width:12px;height:12px;'
        f'border-radius:50%;background:{color};margin-right:6px;flex-shrink:0;"></span>'
    )
    return (
        f'<span style="display:inline-flex;align-items:center;'
        f'background:{soft};border:1px solid {color}33;border-radius:4px;'
        f'padding:5px 12px;font-family:\'JetBrains Mono\',monospace;'
        f'font-size:0.9rem;color:{color};">'
        f'{dot}<span>{label}</span></span>'
    )
