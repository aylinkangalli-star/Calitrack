"""
app.py – CaliTrack entry point.
Run with: streamlit run app.py
"""
import streamlit as st
from database import init_db, login_user, register_user

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CaliTrack",
    page_icon="🔬",
    layout="wide",
)

# ── Init DB on first run ──────────────────────────────────────────────────────
init_db()

# ── Session state helpers ─────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None


def do_logout():
    st.session_state.user = None
    st.rerun()


# ── If logged in → show main app ──────────────────────────────────────────────
if st.session_state.user:
    user = st.session_state.user

    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 {user['username']}")
        st.caption(f"Role: {user['role'].capitalize()}")
        st.divider()

        page = st.radio(
            "Navigation",
            ["Dashboard", "My Devices", "Calibration History"]
            + (["Admin Panel"] if user["role"] == "admin" else []),
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("Log Out", use_container_width=True):
            do_logout()

    # ── Page routing ──────────────────────────────────────────────────────────
    if page == "Dashboard":
        from app_pages.dashboard import show
        show(user)
    elif page == "My Devices":
        from app_pages.devices import show
        show(user)
    elif page == "Calibration History":
        from app_pages.calibration import show
        show(user)
    elif page == "Admin Panel":
        from app_pages.admin import show
        show(user)

# ── Not logged in → Login / Register ─────────────────────────────────────────
else:
    st.title("🔬 CaliTrack")
    st.subheader("Laboratory Device Calibration Tracker")
    st.divider()

    tab_login, tab_register = st.tabs(["Log In", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
        if submitted:
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            new_password2 = st.text_input("Confirm password", type="password")
            submitted2 = st.form_submit_button("Create Account", use_container_width=True)
        if submitted2:
            if new_password != new_password2:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(new_username, new_password)
                if ok:
                    st.success(msg + " You can now log in.")
                else:
                    st.error(msg)
