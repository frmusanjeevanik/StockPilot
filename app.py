import streamlit as st
import os
import uuid
import os  
import json
from datetime import datetime
print("Current working directory:", os.getcwd())  # 👈 Add this line here
from database import init_database
from auth import authenticate_user, logout_user, is_authenticated, check_session_timeout, update_last_activity, get_remaining_session_time
from models import get_user_role
import pages.dashboard as dashboard
import pages.case_entry as case_entry
import pages.analytics as analytics
import pages.reviewer_panel as reviewer_panel
import pages.approver_panel as approver_panel
import pages.legal_panel as legal_panel
import pages.closure_panel as closure_panel
import pages.admin_panel as admin_panel
import pages.user_management as user_management

# Page configuration
st.set_page_config(
    page_title="Tathya - Case Management System",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_database()

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("exports", exist_ok=True)

def main():
    # Authentication check
    if not is_authenticated():
        show_login()
        return
    
    # Header with ABCL logo for authenticated users
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        try:
            st.image("static/images/abcl_logo.jpg", width=200)
        except:
            st.markdown("### 🏢 ABCL")
    
    st.divider()
    
    # Get user role
    username = st.session_state.username
    role = get_user_role(username)
    
    # Sidebar navigation
    show_sidebar(role)
    
    # Main content
    show_main_content()

def show_login():
    """Display login form"""
    # Header with ABCL logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        try:
            st.image("static/images/abcl_logo.jpg", width=200)
        except:
            st.markdown("### 🏢 ABCL")
    
    # Main login layout with Tathya logo on left and login form on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Tathya logo section
        st.markdown("<div style='margin-left: 0px; margin-top: 80px;'>", unsafe_allow_html=True)
        try:
            st.image("static/images/tathya.png", width=250)
        except:
            st.markdown("# 🔎 Tathya")
            st.markdown("### Every Clue Counts")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Login form section
        st.markdown("<div style='margin-left: 50px;'margin-top: 80px;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### UAT Mode")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        st.markdown("</div>", unsafe_allow_html=True)

def show_sidebar(role):
    """Display sidebar navigation based on user role"""
    # Check session timeout - only logout, no message display
    if check_session_timeout():
        logout_user()
        st.rerun()
    
    # Update last activity
    update_last_activity()
    
    # Navigation menu
    st.sidebar.markdown("### 📁 Navigation")
    
    # Base menu items - only Dashboard for all users
    menu_items = ["Dashboard"]
    
    # Role-specific menu items
    if role == "Initiator":
        menu_items.append("Case Entry")
    elif role == "Reviewer":
        menu_items.append("Reviewer Panel")
    elif role == "Approver":
        menu_items.append("Approver Panel")
    elif role == "Legal Reviewer":
        menu_items.append("Legal Panel")
    elif role == "Action Closure Authority":
        menu_items.append("🔒 Action Closure Panel")
    elif role == "Admin":
           menu_items.extend(["Case Entry", "Analytics", "Reviewer Panel", "Approver Panel", "Legal Panel", "🔒 Action Closure Panel", "Admin Panel", "User Management"])

    
    # Initialize selected page
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Dashboard"
    
    # Navigation buttons
    for item in menu_items:
        if st.sidebar.button(item, key=f"nav_{item}", use_container_width=True):
            # Handle special naming for closure panel
            if item == "🔒 Action Closure Panel":
                st.session_state.selected_page = "Closure Panel"
            else:
                st.session_state.selected_page = item
            st.rerun()
    
    st.sidebar.divider()
    
    # User information in smaller font
    st.sidebar.markdown("<small><strong>👤 User Information</strong></small>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<small><strong>User:</strong> {st.session_state.username}</small>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<small><strong>Role:</strong> {role}</small>", unsafe_allow_html=True)
    
    # Session information without expiry message - just show remaining time
    remaining_time = get_remaining_session_time()
    if remaining_time > 0:
        st.sidebar.markdown(f"<small><strong>Session:</strong> {remaining_time} min remaining</small>", unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()

def show_main_content():
    """Display main content based on selected page"""
    page = st.session_state.selected_page
    
    if page == "Dashboard":
        dashboard.show()
    elif page == "Case Entry":
        case_entry.show()
    elif page == "Analytics":
        analytics.show()
    elif page == "Reviewer Panel":
        reviewer_panel.show()
    elif page == "Approver Panel":
        approver_panel.show()
    elif page == "Legal Panel":
        legal_panel.show()
    elif page == "Closure Panel":
        closure_panel.show()
    elif page == "Admin Panel":
        admin_panel.show()
    elif page == "User Management":
        user_management.show()
    else:
        st.error("Page not found")

if __name__ == "__main__":
    main()
