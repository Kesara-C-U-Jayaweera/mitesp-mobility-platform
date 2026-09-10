"""
Enterprise Authentication & Role-Based Access Control (RBAC)
MillenniumIT ESP Mobility Dispatch Platform
"""

import hashlib
import streamlit as st

# Pre-configured Enterprise User Directory for CEO Presentation & Fleet Operations
USERS = {
    "ceo@mitesp.com": {
        "name": "Sanath Fernando",
        "title": "Chief Executive Officer",
        "role": "Executive",
        "password_hash": hashlib.sha256("ceo123".encode()).hexdigest(),
        "avatar": "👔",
        "department": "Executive Leadership",
        "badge_color": "#428AFF"
    },
    "dispatch@mitesp.com": {
        "name": "Kavinda Perera",
        "title": "Head of Corporate Mobility",
        "role": "Dispatcher",
        "password_hash": hashlib.sha256("dispatch123".encode()).hexdigest(),
        "avatar": "🚦",
        "department": "Logistics & Corporate Fleet",
        "badge_color": "#EF4123"
    },
    "employee@mitesp.com": {
        "name": "Amara Silva",
        "title": "Senior Solutions Architect",
        "role": "Employee",
        "password_hash": hashlib.sha256("emp123".encode()).hexdigest(),
        "avatar": "👤",
        "department": "Enterprise Cloud Architecture",
        "badge_color": "#10B981"
    }
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_state():
    if "authenticated" not in st.session_state:
        # Default to False; can be set by login or quick-switch
        st.session_state["authenticated"] = False
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None


def login(email: str, password: str) -> bool:
    email_clean = email.strip().lower()
    # Support short aliases for frictionless presentation
    if email_clean == "ceo":
        email_clean = "ceo@mitesp.com"
    elif email_clean in ("dispatch", "dispatcher"):
        email_clean = "dispatch@mitesp.com"
    elif email_clean in ("employee", "emp"):
        email_clean = "employee@mitesp.com"

    user = USERS.get(email_clean)
    if user and user["password_hash"] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = {
            "email": email_clean,
            **user
        }
        st.session_state["user_role"] = user["role"]
        return True
    return False


def quick_login(role: str):
    """Instant login switcher for presentations."""
    for email, u in USERS.items():
        if u["role"] == role:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = {
                "email": email,
                **u
            }
            st.session_state["user_role"] = u["role"]
            return


def logout():
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.session_state["user_role"] = None


def render_login_screen():
    """Renders a sleek, branded MillenniumIT ESP login portal."""
    st.markdown("""
    <style>
    .login-container {
        max-width: 480px;
        margin: 1.5rem auto 1rem auto;
        padding: 2rem 1.8rem;
        background: linear-gradient(180deg, rgba(15, 22, 38, 0.98) 0%, rgba(7, 9, 14, 0.99) 100%);
        border: 1px solid #24334C;
        border-radius: 16px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6);
        text-align: center;
    }
    .login-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-top: 0.5rem;
    }
    .login-subtitle {
        color: #94A3B8;
        font-size: 0.88rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        try:
            from brand import get_logo_b64
            logo_b64 = get_logo_b64("horizontal")
            logo_html = f'<div style="text-align: center; margin-bottom: 14px;"><img src="data:image/png;base64,{logo_b64}" style="max-width: 240px; height: auto; object-fit: contain; filter: drop-shadow(0 4px 14px rgba(239, 65, 35, 0.3));" alt="MillenniumIT ESP"></div>'
        except Exception:
            logo_html = '<span style="background: #EF4123; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 800; font-size: 11px; letter-spacing: 1px;">MIT ESP</span>'

        login_card_html = f"""<div class="login-container">
{logo_html}
<span style="background: #162032; color: #428AFF; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 11px; border: 1px solid #24334C; margin-left: 6px;">ENTERPRISE ACCESS</span>
<div class="login-title">Corporate Mobility Dispatch</div>
<div class="login-subtitle">Sign in with enterprise SSO credentials to access transit governance</div>
</div>"""
        st.markdown(login_card_html, unsafe_allow_html=True)

        with st.form("enterprise_login_form"):
            email = st.text_input("Corporate Email / Username", placeholder="e.g. ceo@mitesp.com, dispatch@mitesp.com")
            password = st.text_input("Password", type="password", placeholder="Enter your corporate password")
            submit_btn = st.form_submit_button("🔐 Sign In with Corporate SSO", use_container_width=True)

            if submit_btn:
                if login(email, password):
                    st.success(f"Welcome, {st.session_state['current_user']['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use the presentation demo personas below.")

        st.markdown("---")
        st.markdown("##### ⚡ Quick Presentation Demo Switcher")
        st.caption("Click any persona below to simulate different organizational views during executive meetings:")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("👔 CEO Persona\n(Executive ROI)", use_container_width=True):
                quick_login("Executive")
                st.rerun()
        with col_p2:
            if st.button("🚦 Dispatcher\n(Mission Control)", use_container_width=True):
                quick_login("Dispatcher")
                st.rerun()
        with col_p3:
            if st.button("👤 Employee\n(Self-Service)", use_container_width=True):
                quick_login("Employee")
                st.rerun()

        st.markdown("""
        <div style="background: #0B101B; border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px; margin-top: 14px; font-size: 11px; color: #94A3B8;">
            <b>Default Credentials:</b><br>
            • <b>CEO</b>: <code>ceo@mitesp.com</code> / <code>ceo123</code><br>
            • <b>Dispatcher</b>: <code>dispatch@mitesp.com</code> / <code>dispatch123</code><br>
            • <b>Employee</b>: <code>employee@mitesp.com</code> / <code>emp123</code>
        </div>
        """, unsafe_allow_html=True)


def render_user_sidebar():
    """Renders active user session badge, persona switcher, and logout in the sidebar."""
    if not st.session_state.get("authenticated"):
        return

    user = st.session_state.get("current_user", {})
    role = user.get("role", "Dispatcher")
    badge_col = user.get("badge_color", "#428AFF")
    avatar = user.get("avatar", "👤")

    st.sidebar.markdown(f"""
    <div style="background: #111724; border: 1px solid #24334C; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 22px;">{avatar}</span>
                <div>
                    <div style="font-weight: 700; font-size: 13px; color: #FFFFFF;">{user.get('name', 'User')}</div>
                    <div style="font-size: 11px; color: #94A3B8;">{user.get('title', 'Corporate Member')}</div>
                </div>
            </div>
            <span style="background: {badge_col}22; color: {badge_col}; border: 1px solid {badge_col}66; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800;">
                {role.upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_u1, col_u2 = st.sidebar.columns([1, 1])
    with col_u1:
        # Fast toggle for presentation
        next_role = "Executive" if role == "Dispatcher" else ("Dispatcher" if role == "Employee" else "Dispatcher")
        if st.sidebar.button(f"🔄 Switch: {next_role}", use_container_width=True, help="Toggle persona for presentation"):
            quick_login(next_role)
            st.rerun()
    with col_u2:
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            logout()
            st.rerun()
