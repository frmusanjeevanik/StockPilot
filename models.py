import sqlite3
from datetime import datetime
from database import get_db_connection, log_audit

def get_user_by_username(username):
    """Get user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        return cursor.fetchone()

def get_user_role(username):
    """Get user role"""
    user = get_user_by_username(username)
    return user["role"] if user else None

def create_case(case_data, created_by):
    """Create a new case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if case_id already exists
        cursor.execute("SELECT COUNT(*) FROM cases WHERE case_id = ?", (case_data["case_id"],))
        if cursor.fetchone()[0] > 0:
            return False, "Case ID already exists"
        
        cursor.execute('''
            INSERT INTO cases (case_id, lan, case_type, product, region, referred_by, 
                             case_description, case_date, created_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case_data["case_id"],
            case_data["lan"],
            case_data["case_type"],
            case_data["product"],
            case_data["region"],
            case_data["referred_by"],
            case_data["case_description"],
            case_data["case_date"],
            created_by,
            case_data.get("status", "Draft")
        ))
        
        conn.commit()
        
        # Log audit
        log_audit(case_data["case_id"], "Case Created", f"Case created with status: {case_data.get('status', 'Draft')}", created_by)
        
        return True, "Case created successfully"

def get_cases_by_status(status=None, created_by=None):
    """Get cases by status and/or creator"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM cases"
        params = []
        conditions = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()

def get_case_by_id(case_id):
    """Get case by case_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        return cursor.fetchone()

def update_case_status(case_id, new_status, updated_by, comments=None):
    """Update case status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update case status
        update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [new_status]
        
        # Add specific reviewer fields based on status
        if new_status == "Under Review":
            update_fields.append("reviewed_by = ?")
            update_fields.append("reviewed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Approved":
            update_fields.append("approved_by = ?")
            update_fields.append("approved_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Legal Review":
            update_fields.append("legal_reviewed_by = ?")
            update_fields.append("legal_reviewed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Closed":
            update_fields.append("closed_by = ?")
            update_fields.append("closed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        
        params.append(case_id)
        
        cursor.execute(f'''
            UPDATE cases 
            SET {", ".join(update_fields)}
            WHERE case_id = ?
        ''', params)
        
        # Add comment if provided
        if comments:
            cursor.execute('''
                INSERT INTO case_comments (case_id, comment, comment_type, created_by)
                VALUES (?, ?, ?, ?)
            ''', (case_id, comments, f"Status Change to {new_status}", updated_by))
        
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Status Update", f"Status changed to: {new_status}", updated_by)
        
        return True

def get_case_comments(case_id):
    """Get comments for a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM case_comments 
            WHERE case_id = ? 
            ORDER BY created_at DESC
        ''', (case_id,))
        return cursor.fetchall()

def add_case_comment(case_id, comment, comment_type, created_by):
    """Add comment to a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO case_comments (case_id, comment, comment_type, created_by)
            VALUES (?, ?, ?, ?)
        ''', (case_id, comment, comment_type, created_by))
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Comment Added", f"Comment type: {comment_type}", created_by)

def get_case_documents(case_id):
    """Get documents for a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM documents 
            WHERE case_id = ? 
            ORDER BY uploaded_at DESC
        ''', (case_id,))
        return cursor.fetchall()

def add_case_document(case_id, filename, original_filename, file_path, file_size, uploaded_by):
    """Add document to a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO documents (case_id, filename, original_filename, file_path, file_size, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (case_id, filename, original_filename, file_path, file_size, uploaded_by))
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Document Added", f"Document: {original_filename}", uploaded_by)

def get_case_statistics():
    """Get case statistics for dashboard"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        stats["total_cases"] = cursor.fetchone()[0]
        
        # Cases by status
        cursor.execute("SELECT status, COUNT(*) FROM cases GROUP BY status")
        stats["by_status"] = dict(cursor.fetchall())
        
        # Cases by region
        cursor.execute("SELECT region, COUNT(*) FROM cases GROUP BY region")
        stats["by_region"] = dict(cursor.fetchall())
        
        # Cases by product
        cursor.execute("SELECT product, COUNT(*) FROM cases GROUP BY product")
        stats["by_product"] = dict(cursor.fetchall())
        
        # Recent cases
        cursor.execute("SELECT * FROM cases ORDER BY created_at DESC LIMIT 10")
        stats["recent_cases"] = cursor.fetchall()
        
        return stats

def get_audit_logs(case_id=None, limit=100):
    """Get audit logs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if case_id:
            cursor.execute('''
                SELECT * FROM audit_logs 
                WHERE case_id = ? 
                ORDER BY performed_at DESC 
                LIMIT ?
            ''', (case_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM audit_logs 
                ORDER BY performed_at DESC 
                LIMIT ?
            ''', (limit,))
        
        return cursor.fetchall()

def search_cases(search_term, filters=None):
    """Search cases with optional filters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM cases 
            WHERE (case_id LIKE ? OR lan LIKE ? OR case_description LIKE ?)
        '''
        params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        
        if filters:
            if filters.get("status"):
                query += " AND status = ?"
                params.append(filters["status"])
            
            if filters.get("region"):
                query += " AND region = ?"
                params.append(filters["region"])
            
            if filters.get("product"):
                query += " AND product = ?"
                params.append(filters["product"])
            
            if filters.get("date_from"):
                query += " AND case_date >= ?"
                params.append(filters["date_from"])
            
            if filters.get("date_to"):
                query += " AND case_date <= ?"
                params.append(filters["date_to"])
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
