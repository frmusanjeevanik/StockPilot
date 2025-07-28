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
            access_level = "All Roles" if (user["all_roles_access"] if "all_roles_access" in user.keys() else False) else user["role"]
            user_data.append({
                "User ID": user["username"],
                "Name": user["name"] or "N/A",
                "Team": user["team"] or "N/A",
                "Functional Designation": user["functional_designation"] or "N/A",
                "Access Level": access_level,
                "Referred By": user["referred_by"] or "N/A",
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            username = st.text_input("User ID *", placeholder="e.g., bg390458")
            password = st.text_input("Password *", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm password")
        
        with col2:
            name = st.text_input("Name *", placeholder="Enter full name")
            team = st.text_input("Team *", placeholder="e.g., Investigation")
            functional_designation = st.text_input("Functional Designation *", placeholder="e.g., TL - FRMU Central Investigation")
        
        with col3:
            role = st.selectbox("System Role *", [
                "Initiator",
                "Reviewer", 
                "Approver",
                "Legal Reviewer",
                "Actioner",
                "Admin"
            ])
            referred_by = st.selectbox("Referred By *", [
                "Audit Team", "Business Unit", "Collection Unit", "Compliance Team", "Credit Unit",
                "Customer Service", "GRT", "HR", "Legal Unit", "MD / CEO Escalation",
                "Operation Risk Management", "Operation Unit", "Other Function", "Policy Team",
                "Risk Containment Unit", "Sales Unit", "Technical Team"
            ])
            email = st.text_input("Email", placeholder="Enter email address")
            is_active = st.checkbox("Active User", value=True)
            all_roles_access = st.checkbox("Grant All Roles Access", 
                                         help="Allow user to login as any role except Admin")
        
        submit_button = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if submit_button:
            # Validation
            errors = []
            
            if not username or not username.strip():
                errors.append("User ID is required")
            elif len(username.strip()) < 3:
                errors.append("User ID must be at least 3 characters long")
            
            if not name or not name.strip():
                errors.append("Name is required")
            
            if not team or not team.strip():
                errors.append("Team is required")
            
            if not functional_designation or not functional_designation.strip():
                errors.append("Functional Designation is required")
            
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
                user_data = {
                    'username': username.strip(),
                    'password': password,
                    'role': role,
                    'email': email.strip() if email else None,
                    'name': name.strip(),
                    'team': team.strip(),
                    'functional_designation': functional_designation.strip(),
                    'referred_by': referred_by,
                    'is_active': is_active,
                    'all_roles_access': all_roles_access
                }
                success, message = create_user(user_data)
                
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
            st.write(f"Editing user: **{selected_user['username']} - {selected_user['name']}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_name = st.text_input("Name", value=selected_user['name'] or "", placeholder="Enter full name")
                new_team = st.text_input("Team", value=selected_user['team'] or "", placeholder="Enter team")
                new_functional_designation = st.text_input("Functional Designation", value=selected_user['functional_designation'] or "", placeholder="Enter designation")
            
            with col2:
                new_role = st.selectbox("System Role", [
                    "Initiator",
                    "Reviewer", 
                    "Approver",
                    "Legal Reviewer",
                    "Actioner",
                    "Admin"
                ], index=["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Admin"].index(selected_user['role']))
                
                new_referred_by = st.selectbox("Referred By", [
                    "Audit Team", "Business Unit", "Collection Unit", "Compliance Team", "Credit Unit",
                    "Customer Service", "GRT", "HR", "Legal Unit", "MD / CEO Escalation",
                    "Operation Risk Management", "Operation Unit", "Other Function", "Policy Team",
                    "Risk Containment Unit", "Sales Unit", "Technical Team"
                ], index=[
                    "Audit Team", "Business Unit", "Collection Unit", "Compliance Team", "Credit Unit",
                    "Customer Service", "GRT", "HR", "Legal Unit", "MD / CEO Escalation",
                    "Operation Risk Management", "Operation Unit", "Other Function", "Policy Team",
                    "Risk Containment Unit", "Sales Unit", "Technical Team"
                ].index(selected_user['referred_by']) if selected_user['referred_by'] else 0)
                
                new_email = st.text_input("Email", value=selected_user['email'] or "", placeholder="Enter email address")
            
            with col3:
                new_is_active = st.checkbox("Active User", value=bool(selected_user['is_active']))
                
                # Password reset option
                reset_password = st.checkbox("Reset Password")
                
                # Role assignment option for admin
                st.markdown("**Role Assignment:**")
                all_roles_access = st.checkbox("Grant All Roles Access", 
                                             value=selected_user["all_roles_access"] if "all_roles_access" in selected_user.keys() else False,
                                             help="Allow user to login as any role except Admin")
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
                        'name': new_name.strip() if new_name else None,
                        'team': new_team.strip() if new_team else None,
                        'functional_designation': new_functional_designation.strip() if new_functional_designation else None,
                        'referred_by': new_referred_by,
                        'is_active': new_is_active,
                        'all_roles_access': all_roles_access
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

def create_user(user_data):
    """Create a new user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user_data['username'],))
            if cursor.fetchone()[0] > 0:
                return False, "User ID already exists"
            
            # Hash password
            password_hash = get_password_hash(user_data['password'])
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email, name, team, 
                                 functional_designation, referred_by, is_active, all_roles_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'], 
                password_hash, 
                user_data['role'], 
                user_data['email'],
                user_data['name'],
                user_data['team'],
                user_data['functional_designation'],
                user_data['referred_by'],
                user_data['is_active'],
                user_data['all_roles_access']
            ))
            
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
            
            if 'name' in update_data:
                set_clauses.append("name = ?")
                values.append(update_data['name'])
            
            if 'team' in update_data:
                set_clauses.append("team = ?")
                values.append(update_data['team'])
            
            if 'functional_designation' in update_data:
                set_clauses.append("functional_designation = ?")
                values.append(update_data['functional_designation'])
            
            if 'referred_by' in update_data:
                set_clauses.append("referred_by = ?")
                values.append(update_data['referred_by'])
            
            if 'is_active' in update_data:
                set_clauses.append("is_active = ?")
                values.append(update_data['is_active'])
            
            if 'all_roles_access' in update_data:
                set_clauses.append("all_roles_access = ?")
                values.append(update_data['all_roles_access'])
            
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