import streamlit as st
import hashlib
from datetime import datetime, timedelta
from models import get_user_by_username
from database import get_password_hash

def authenticate_user(username, password, selected_role=None):
    """Authenticate user with username and password - restrict to assigned role only"""
    user = get_user_by_username(username)
    if user:
        password_hash = get_password_hash(password)
        if user["password_hash"] == password_hash:
            # Check if user can login with selected role
            user_assigned_role = user["role"]  # Get user's assigned role from database
            
            # Check role access permissions
            user_has_all_roles_access = user["all_roles_access"] if "all_roles_access" in user.keys() else False
            
            if selected_role and user_assigned_role != selected_role:
                # Admin users can access any role
                if user_assigned_role == "Admin":
                    pass  # Admin can access any role
                # Users with all_roles_access can access any role except Admin
                elif user_has_all_roles_access and selected_role != "Admin":
                    pass  # User has permission for all roles except Admin
                # Non-admin users cannot access Admin role
                elif selected_role == "Admin" and user_assigned_role != "Admin":
                    return False, "Access denied. You are not authorized for Admin role."
                # Users without all_roles_access are restricted to their assigned role
                elif not user_has_all_roles_access:
                    return False, f"Access denied. You can only login as '{user_assigned_role}' role."
            
            # Use selected role if provided and authorized, otherwise use user's default role
            if selected_role:
                # For users with all_roles_access, allow any role except Admin (unless they are Admin)
                if user_has_all_roles_access and selected_role != "Admin":
                    user_role = selected_role
                # For Admin users, allow any role
                elif user_assigned_role == "Admin":
                    user_role = selected_role
                # For normal users, only allow their assigned role
                elif user_assigned_role == selected_role:
                    user_role = selected_role
                else:
                    user_role = user_assigned_role
            else:
                user_role = user_assigned_role
            
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = user_role
            st.session_state.user_function = user["role"]  # Store original function for referral
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()
            return True, "Login successful"
    return False, "Invalid User ID or password"

def get_user_function():
    """Get current user's function name for referral purposes"""
    if is_authenticated():
        return st.session_state.get("user_function")
    return None

def get_user_referred_by():
    """Get current user's default referred by value"""
    if is_authenticated():
        user = get_user_by_username(st.session_state.username)
        if user and user["referred_by"]:
            return user["referred_by"]
    return None

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


def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.error("Please log in to access this page.")
            return None
        return func(*args, **kwargs)
    return wrapper

