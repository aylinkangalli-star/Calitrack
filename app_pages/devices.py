"""
pages/devices.py – User's personal device list (add / remove).
"""
import streamlit as st
from database import get_user_devices, get_catalog, add_user_device, remove_user_device
from theme import status_badge


def show(user: dict):
    page_header("My Devices", "Your personal instrument list")

    devices = get_user_devices(user["id"])
    catalog = get_catalog()

    # ── Add device from catalog ───────────────────────────────────────────────
    st.subheader("Add a Device")
    if not catalog:
        st.info("The device catalog is empty. Ask an admin to add devices.")
    else:
        already_ids = {d["catalog_id"] for d in devices}
        available = [c for c in catalog if c["id"] not in already_ids]

        if not available:
            st.info("You already have all catalog devices in your list.")
        else:
            options = {f"{c['name']} — {c['brand'] or ''} {c['model'] or ''}".strip(): c["id"]
                       for c in available}
            selected_label = st.selectbox("Select a device to add", list(options.keys()))
            if st.button("➕ Add to My List"):
                ok, msg = add_user_device(user["id"], options[selected_label])
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)

    st.divider()

    # ── Current device list ───────────────────────────────────────────────────
    st.subheader("My Device List")
    if not devices:
        st.info("Your list is empty.")
    else:
        for d in devices:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"**{d['name']}**  "
                    f"{'— ' + d['brand'] if d['brand'] else ''}  "
                    f"{d['model'] or ''}"
                )
                st.caption(
                    f"Calibration interval: every {d['calibration_interval_days']} days  |  "
                    f"Next due: {d['next_calibration_date'] or 'No record'}"
                )
            with col2:
                if st.button("🗑️ Remove", key=f"del_{d['user_device_id']}"):
                    remove_user_device(d["user_device_id"])
                    st.rerun()
            st.divider()
