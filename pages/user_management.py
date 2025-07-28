import streamlit as st
import re
from datetime import datetime
from database import get_db_connection, get_password_hash
from auth import get_current_user, require_role

@require_role(["Admin"])
def show():
    """Display user management page"""
    st.title("👥 User Management")
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Users List", "➕ Add User", "✏️ Edit User"])
    
    with tab1:
        show_users_list()
    
    with tab2:
        show_add_user()
    
    with tab3:
        show_edit_user()

def show_users_list():
    """Display list of all users"""
    st.subheader("All Users")
    
    # Get all users
    users = get_all_users()
    
    if users:
        # Display users in a table format
        user_data = []
        for user in users:
            user_data.append({
                "Username": user["username"],
                "Role": user["role"],
                "Email": user["email"] or "N/A",
                "Status": "Active" if user["is_active"] else "Inactive",
                "Created": user["created_at"][:10] if user["created_at"] else "N/A"
            })
        
        st.dataframe(user_data, use_container_width=True)
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(users))
        
        with col2:
            active_users = sum(1 for user in users if user["is_active"])
            st.metric("Active Users", active_users)
        
        with col3:
            role_counts = {}
            for user in users:
                role = user["role"]
                role_counts[role] = role_counts.get(role, 0) + 1
            most_common_role = max(role_counts.keys(), key=lambda x: role_counts[x]) if role_counts else "None"
            st.metric("Most Common Role", most_common_role)
        
        with col4:
            inactive_users = len(users) - active_users
            st.metric("Inactive Users", inactive_users)
    else:
        st.info("No users found in the system.")

def show_add_user():
    """Display add user form"""
    st.subheader("Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username *", placeholder="Enter unique username")
            password = st.text_input("Password *", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm password")
        
        with col2:
            role = st.selectbox("Role *", [
                "Initiator",
                "Reviewer", 
                "Approver",
                "Legal Reviewer",
                "Action Closure Authority",
                "Admin"
            ])
            email = st.text_input("Email", placeholder="Enter email address")
            is_active = st.checkbox("Active User", value=True)
        
        submit_button = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if submit_button:
            # Validation
            errors = []
            
            if not username or not username.strip():
                errors.append("Username is required")
            elif len(username.strip()) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if not password:
                errors.append("Password is required")
            elif len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if email and not is_valid_email(email):
                errors.append("Invalid email format")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create user
                success, message = create_user(username.strip(), password, role, email.strip() if email else None, is_active)
                
                if success:
                    st.success(f"✅ User '{username}' created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def show_edit_user():
    """Display edit user interface"""
    st.subheader("Edit User")
    
    # Get all users for selection
    users = get_all_users()
    
    if not users:
        st.info("No users available to edit.")
        return
    
    # User selection
    user_options = [f"{user['username']} ({user['role']})" for user in users]
    selected_user_index = st.selectbox("Select User to Edit", range(len(user_options)), format_func=lambda x: user_options[x])
    
    if selected_user_index is not None:
        selected_user = users[selected_user_index]
        
        with st.form("edit_user_form"):
            st.write(f"Editing user: **{selected_user['username']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_role = st.selectbox("Role", [
                    "Initiator",
                    "Reviewer", 
                    "Approver",
                    "Legal Reviewer",
                    "Action Closure Authority",
                    "Admin"
                ], index=["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Action Closure Authority", "Admin"].index(selected_user['role']))
                
                new_email = st.text_input("Email", value=selected_user['email'] or "", placeholder="Enter email address")
            
            with col2:
                new_is_active = st.checkbox("Active User", value=bool(selected_user['is_active']))
                
                # Password reset option
                reset_password = st.checkbox("Reset Password")
                new_password = ""
                confirm_new_password = ""
                if reset_password:
                    new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
                    confirm_new_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            col1, col2 = st.columns(2)
            
            with col1:
                update_button = st.form_submit_button("💾 Update User", use_container_width=True)
            
            with col2:
                if selected_user['username'] != get_current_user():  # Prevent self-deletion
                    delete_button = st.form_submit_button("🗑️ Delete User", use_container_width=True, type="secondary")
                else:
                    st.info("Cannot delete your own account")
                    delete_button = False
            
            if update_button:
                errors = []
                
                if new_email and not is_valid_email(new_email):
                    errors.append("Invalid email format")
                
                if reset_password:
                    if not new_password:
                        errors.append("New password is required")
                    elif len(new_password) < 6:
                        errors.append("Password must be at least 6 characters long")
                    elif new_password != confirm_new_password:
                        errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Update user
                    update_data = {
                        'role': new_role,
                        'email': new_email.strip() if new_email else None,
                        'is_active': new_is_active
                    }
                    
                    if reset_password:
                        update_data['password'] = new_password
                    
                    success, message = update_user(selected_user['username'], update_data)
                    
                    if success:
                        st.success(f"✅ User '{selected_user['username']}' updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            if delete_button:
                success, message = delete_user(selected_user['username'])
                if success:
                    st.success(f"✅ User '{selected_user['username']}' deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def get_all_users():
    """Get all users from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        return cursor.fetchall()

def create_user(username, password, role, email=None, is_active=True):
    """Create a new user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False, "Username already exists"
            
            # Hash password
            password_hash = get_password_hash(password)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, email, is_active))
            
            conn.commit()
            return True, "User created successfully"
            
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def update_user(username, update_data):
    """Update user information"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query
            set_clauses = []
            values = []
            
            if 'role' in update_data:
                set_clauses.append("role = ?")
                values.append(update_data['role'])
            
            if 'email' in update_data:
                set_clauses.append("email = ?")
                values.append(update_data['email'])
            
            if 'is_active' in update_data:
                set_clauses.append("is_active = ?")
                values.append(update_data['is_active'])
            
            if 'password' in update_data:
                set_clauses.append("password_hash = ?")
                values.append(get_password_hash(update_data['password']))
            
            if not set_clauses:
                return False, "No updates provided"
            
            values.append(username)
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE username = ?"
            
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                return False, "User not found"
            
            return True, "User updated successfully"
            
    except Exception as e:
        return False, f"Error updating user: {str(e)}"

def delete_user(username):
    """Delete a user (soft delete by setting is_active to False)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Soft delete - set is_active to False
            cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return False, "User not found"
            
            return True, "User deleted successfully"
            
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None