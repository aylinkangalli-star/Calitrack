"""
pages/admin.py – Admin panel: catalog management, calibration entry, alerts.
"""
import streamlit as st
from datetime import date
from database import (
    get_catalog, add_catalog_device, update_catalog_device, delete_catalog_device,
    add_calibration_record, get_overdue_devices,
)
from theme import status_badge


def show(user: dict):
    if user["role"] != "admin":
        st.error("Access denied.")
        return

    page_header("Admin Panel", "Catalog management & calibration entry")

    tab_alerts, tab_catalog, tab_calibration = st.tabs([
        "🔔 Alerts", "📦 Device Catalog", "✏️ Enter Calibration"
    ])

    # ── Alerts ────────────────────────────────────────────────────────────────
    with tab_alerts:
        st.subheader("Overdue / Due-Soon Devices")
        overdue = get_overdue_devices()
        if not overdue:
            st.success("All devices are up to date!")
        else:
            for d in overdue:
                next_date = d["next_calibration_date"]
                if next_date:
                    days = (date.fromisoformat(next_date) - date.today()).days
                    state = "bad" if days < 0 else "warn"
                    label = f"Overdue by {abs(days)} days" if days < 0 else f"Due in {days} days"
                else:
                    state, label = "bad", "No calibration record"

                c1, c2 = st.columns([3, 2])
                c1.markdown(f"**{d['name']}**  —  {d['brand'] or ''} {d['model'] or ''}")
                c2.markdown(status_badge(state, label), unsafe_allow_html=True)

    # ── Device catalog ────────────────────────────────────────────────────────
    with tab_catalog:
        st.subheader("Add New Device to Catalog")
        with st.form("add_device_form"):
            name = st.text_input("Device Name *")
            brand = st.text_input("Brand")
            model = st.text_input("Model")
            interval = st.number_input("Calibration Interval (days)", min_value=1, value=365)
            if st.form_submit_button("Add Device", use_container_width=True):
                if not name:
                    st.error("Device name is required.")
                else:
                    add_catalog_device(name, brand, model, int(interval))
                    st.success(f"'{name}' added to catalog.")
                    st.rerun()

        st.divider()
        st.subheader("Existing Devices")
        catalog = get_catalog()
        if not catalog:
            st.info("Catalog is empty.")
        else:
            for d in catalog:
                with st.expander(f"🔩 {d['name']}  —  {d['brand'] or ''} {d['model'] or ''}"):
                    with st.form(f"edit_{d['id']}"):
                        e_name = st.text_input("Name", value=d["name"])
                        e_brand = st.text_input("Brand", value=d["brand"] or "")
                        e_model = st.text_input("Model", value=d["model"] or "")
                        e_interval = st.number_input(
                            "Calibration Interval (days)",
                            min_value=1,
                            value=d["calibration_interval_days"]
                        )
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("💾 Save Changes", use_container_width=True):
                            update_catalog_device(d["id"], e_name, e_brand, e_model, int(e_interval))
                            st.success("Updated.")
                            st.rerun()
                        if c2.form_submit_button("🗑️ Delete", use_container_width=True):
                            delete_catalog_device(d["id"])
                            st.warning("Device deleted.")
                            st.rerun()

    # ── Enter calibration data ────────────────────────────────────────────────
    with tab_calibration:
        st.subheader("Enter Calibration Record")
        catalog = get_catalog()
        if not catalog:
            st.info("No devices in catalog yet.")
        else:
            options = {f"{c['name']} — {c['brand'] or ''} {c['model'] or ''}".strip(): c["id"]
                       for c in catalog}
            with st.form("cal_form"):
                selected = st.selectbox("Device", list(options.keys()))
                cal_date = st.date_input("Calibration Date", value=date.today())
                performed_by = st.text_input("Performed By")
                notes = st.text_area("Notes")
                if st.form_submit_button("Save Record", use_container_width=True):
                    add_calibration_record(
                        catalog_device_id=options[selected],
                        calibration_date=str(cal_date),
                        performed_by=performed_by,
                        notes=notes,
                        created_by=user["id"],
                    )
                    st.success("Calibration record saved.")
