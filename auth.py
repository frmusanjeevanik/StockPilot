import streamlit as st
import hashlib
from datetime import datetime, timedelta
from models import get_user_by_username
from database import get_password_hash

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if user:
        password_hash = get_password_hash(password)
        if user["password_hash"] == password_hash:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = user["role"]
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()
            return True
    return False

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)

def logout_user():
    """Logout user and clear session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False

def require_role(required_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_authenticated():
                st.error("Please login to access this page")
                return
            
            user_role = st.session_state.get("user_role")
            if user_role not in required_roles and "Admin" not in required_roles:
                st.error("You don't have permission to access this page")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """Get current authenticated user"""
    if is_authenticated():
        return st.session_state.username
    return None

def get_current_user_role():
    """Get current user role"""
    if is_authenticated():
        return st.session_state.get("user_role")
    return None

def update_last_activity():
    """Update last activity timestamp"""
    if is_authenticated():
        st.session_state.last_activity = datetime.now()

def check_session_timeout():
    """Check if session has timed out (15 minutes)"""
    if not is_authenticated():
        return False
    
    last_activity = st.session_state.get("last_activity")
    if last_activity:
        if datetime.now() - last_activity > timedelta(minutes=15):
            return True
    return False

def get_remaining_session_time():
    """Get remaining session time in minutes"""
    if not is_authenticated():
        return 0
    
    last_activity = st.session_state.get("last_activity")
    if last_activity:
        elapsed = datetime.now() - last_activity
        remaining = timedelta(minutes=15) - elapsed
        if remaining.total_seconds() > 0:
            return int(remaining.total_seconds() / 60)
    return 0
