"""
theme.py – CaliTrack status badge styling.
"""

# Status colors
STATUS_COLOR = {
    "ok":   ("#1E8E5A", "#E4F4EA"),    # Green
    "warn": ("#B9820F", "#FBF1DD"),    # Orange
    "bad":  ("#B23A34", "#FBE8E6"),    # Red
}


def status_badge(state: str, label: str) -> str:
    """Return HTML for colored status badge (● colored dot + label).
    
    state: 'ok' | 'warn' | 'bad'
    label: e.g. "OK (214d left)", "Due in 5d", "Overdue (3d)"
    
    Usage: st.markdown(status_badge("ok", "OK (214d left)"), unsafe_allow_html=True)
    """
    color, soft = STATUS_COLOR.get(state, ("#5B6B6A", "#EEF2F1"))
    dot = (
        f'<span style="display:inline-block;width:12px;height:12px;'
        f'border-radius:50%;background:{color};margin-right:6px;flex-shrink:0;"></span>'
    )
    return (
        f'<span style="display:inline-flex;align-items:center;'
        f'background:{soft};border:1px solid {color}33;border-radius:4px;'
        f'padding:5px 12px;font-family:\'Courier New\',monospace;'
        f'font-size:0.9rem;color:{color};">'
        f'{dot}<span>{label}</span></span>'
    )
