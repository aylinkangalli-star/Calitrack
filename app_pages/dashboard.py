"""
pages/dashboard.py – Summary view for logged-in users.
"""
import streamlit as st
from datetime import date
from database import get_user_devices
from theme import status_badge


def _status(next_cal: str | None) -> tuple[str, str]:
    """Return (state, label) for a calibration date.
    state: 'ok' | 'warn' | 'bad' | 'none'
    """
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
    st.title("📊 Dashboard")
    st.subheader("Fleet-wide calibration status")

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
    col1.metric("Total Devices", total)
    col2.metric("🟢 OK", ok)
    col3.metric("🟡 Due Soon", due_soon)
    col4.metric("🔴 Overdue", overdue)

    st.divider()

    # ── Device status table ───────────────────────────────────────────────────
    st.subheader("Device Status")
    for d in devices:
        state, label = _status(d["next_calibration_date"])
        icon = "🔴" if state == "bad" else "🟡" if state == "warn" else "🟢"
        
        with st.expander(f"{icon}  {d['name']}  —  {d['brand'] or ''} {d['model'] or ''}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Last calibration:** {d['calibration_date'] or '—'}")
            c2.markdown(f"**Next due:** {d['next_calibration_date'] or '—'}")
            
            # Show colored badge
            st.markdown(status_badge(state, label), unsafe_allow_html=True)
            
            if d["performed_by"]:
                st.caption(f"Performed by: {d['performed_by']}")
            if d["notes"]:
                st.caption(f"Notes: {d['notes']}")
