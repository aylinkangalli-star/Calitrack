"""
pages/calibration.py – Calibration history for user's devices.
"""
import streamlit as st
from database import get_user_devices, get_calibration_history


def show(user: dict):
    st.title("📋 Calibration History")
    st.subheader("Past calibration records by device")

    devices = get_user_devices(user["id"])

    if not devices:
        st.info("No devices in your list yet.")
        return

    device_options = {d["name"]: d["catalog_id"] for d in devices}
    selected = st.selectbox("Select a device", list(device_options.keys()))

    if selected:
        catalog_id = device_options[selected]
        records = get_calibration_history(catalog_id)

        if not records:
            st.info("No calibration records for this device yet.")
        else:
            st.subheader(f"History: {selected}")
            for r in records:
                with st.expander(f"📅 {r['calibration_date']}  →  next due: {r['next_calibration_date']}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Performed by:** {r['performed_by'] or '—'}")
                    c2.markdown(f"**Entered by:** {r['entered_by'] or '—'}")
                    if r["notes"]:
                        st.markdown(f"**Notes:** {r['notes']}")
