"""
pages/dashboard.py – Summary view for logged-in users.
"""
import streamlit as st
from datetime import date
from database import get_user_devices, get_overdue_devices
from theme import page_header, status_badge, metric_card


def _status(next_cal: str | None) -> tuple[str, str]:
    """Return (state_key, label) for a calibration date.
    state_key is one of 'ok' | 'warn' | 'bad' | 'none', used by theme.status_badge."""
    if not next_cal:
        return "none", "No Record"
    days_left = (date.fromisoformat(next_cal) - date.today()).days
    if days_left < 0:
        return "bad", f"Overdue ({abs(days_left)}d)"
    elif days_left <= 30:
        return "warn", f"Due in {days_left}d"
    else:
        return "ok", f"OK ({days_left}d left)"


def show(user: dict):
    page_header("Dashboard", "Fleet-wide calibration status")

    devices = get_user_devices(user["id"])

    if not devices:
        st.info("You have no devices yet. Go to **My Devices** to add some.")
        return

    # ── Summary metrics ───────────────────────────────────────────────────────
    total = len(devices)
    overdue = sum(1 for d in devices if _status(d["next_calibration_date"])[0] == "bad")
    due_soon = sum(1 for d in devices if _status(d["next_calibration_date"])[0] == "warn")
    ok = total - overdue - due_soon

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("Total Devices", str(total)), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("OK", str(ok), "ok"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("Due Soon", str(due_soon), "warn"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("Overdue", str(overdue), "bad"), unsafe_allow_html=True)

    st.divider()

    # ── Device status table ───────────────────────────────────────────────────
    st.markdown(
        "<span style=\"font-family:'Space Grotesk',sans-serif;font-weight:600;"
        "font-size:1.1rem;\">Device Status</span>",
        unsafe_allow_html=True,
    )
    for d in devices:
        state, label = _status(d["next_calibration_date"])
        badge_html = status_badge(state, label)
        with st.expander(f"{d['name']}  —  {d['brand'] or ''} {d['model'] or ''}"):
            st.markdown(badge_html, unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Last calibration:** {d['calibration_date'] or '—'}")
            c2.markdown(f"**Next due:** {d['next_calibration_date'] or '—'}")
            c3.markdown("")
            if d["performed_by"]:
                st.caption(f"Performed by: {d['performed_by']}")
            if d["notes"]:
                st.caption(f"Notes: {d['notes']}")
