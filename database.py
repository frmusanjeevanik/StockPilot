import sqlite3
import os
import hashlib
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = "case_management.db"

def get_password_hash(password):
    """Generate password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with tables and default data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                name TEXT,
                team TEXT,
                functional_designation TEXT,
                referred_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                lan TEXT NOT NULL,
                case_type TEXT NOT NULL,
                product TEXT NOT NULL,
                region TEXT NOT NULL,
                referred_by TEXT NOT NULL,
                case_description TEXT NOT NULL,
                case_date DATE NOT NULL,
                status TEXT DEFAULT 'Draft',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by TEXT,
                reviewed_at TIMESTAMP,
                approved_by TEXT,
                approved_at TIMESTAMP,
                legal_reviewed_by TEXT,
                legal_reviewed_at TIMESTAMP,
                closed_by TEXT,
                closed_at TIMESTAMP,
                closure_reason TEXT,
                -- SLA tracking
                fmr1_due_date DATE,
                fmr1_submitted_date DATE,
                fmr3_due_date DATE,
                fmr3_submitted_date DATE,
                document_retention_date DATE,
                sla_status TEXT DEFAULT 'On Track',
                -- Demographics
                customer_name TEXT,
                customer_dob DATE,
                customer_pan TEXT,
                customer_address TEXT,
                customer_mobile TEXT,
                customer_email TEXT,
                branch_location TEXT,
                loan_amount DECIMAL(15,2),
                disbursement_date DATE,
                repayment_status TEXT,
                linked_loan_accounts TEXT,
                customer_type TEXT DEFAULT 'Individual',
                kyc_status TEXT DEFAULT 'Pending',
                risk_category TEXT,
                case_source TEXT,
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (uploaded_by) REFERENCES users (username)
            )
        ''')
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                performed_by TEXT NOT NULL,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (performed_by) REFERENCES users (username)
            )
        ''')
        
        # Case comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                comment TEXT NOT NULL,
                comment_type TEXT DEFAULT 'General',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Investigation details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investigation_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                investigation_type TEXT,
                investigation_status TEXT DEFAULT 'In Progress',
                field_verification_status TEXT DEFAULT 'Pending',
                document_verification_status TEXT DEFAULT 'Pending',
                reference_verification_status TEXT DEFAULT 'Pending',
                technical_verification_status TEXT DEFAULT 'Pending',
                investigation_findings TEXT,
                risk_assessment TEXT,
                fraud_indicators TEXT,
                recommendations TEXT,
                evidence_collected TEXT,
                investigation_date DATE,
                completed_date DATE,
                investigator_name TEXT,
                supervisor_name TEXT,
                final_conclusion TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        conn.commit()
        
        # Add new columns to existing users table if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN team TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN functional_designation TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN all_roles_access BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Achievement tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'bronze',
                points INTEGER NOT NULL DEFAULT 10,
                category TEXT NOT NULL DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id),
                UNIQUE(username, achievement_id)
            )
        ''')
        
        conn.commit()
        
        # Clean up old test users first
        test_users_to_remove = ["initiator", "reviewer", "approver", "legal", "closure", "actioner"]
        for user_id in test_users_to_remove:
            cursor.execute("DELETE FROM users WHERE username = ?", (user_id,))
        
        # Insert default users if they don't exist (all real users from the master list)
        default_users = [
            ("admin", "admin123", "Admin", "admin@abcl.com", "System Administrator", "IT", "System Admin", "Technical Team")
        ]
        
        for username, password, role, email, name, team, designation, referred_by in default_users:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] == 0:
                password_hash = get_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, email, name, team, 
                                     functional_designation, referred_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, role, email, name, team, designation, referred_by))
        
        # Initialize default achievements
        default_achievements = [
            ("first_case", "First Case", "Handle your first case", "🎯", "bronze", 10, "Getting Started"),
            ("cases_5", "Case Handler", "Successfully handle 5 cases", "📝", "bronze", 25, "Progress"),
            ("cases_10", "Case Expert", "Successfully handle 10 cases", "🏅", "silver", 50, "Progress"),
            ("cases_25", "Case Master", "Successfully handle 25 cases", "🎖️", "silver", 100, "Progress"),
            ("cases_50", "Case Champion", "Successfully handle 50 cases", "🏆", "gold", 250, "Progress"),
            ("cases_100", "Case Legend", "Successfully handle 100 cases", "👑", "gold", 500, "Progress"),
            ("speed_resolver", "Speed Demon", "Resolve cases quickly", "⚡", "silver", 75, "Performance"),
            ("quality_expert", "Quality Master", "Maintain high quality standards", "💎", "gold", 200, "Performance"),
            ("team_player", "Team Player", "Collaborate effectively", "🤝", "bronze", 30, "Collaboration"),
            ("mentor", "Mentor", "Help train new team members", "🎓", "gold", 150, "Leadership")
        ]
        
        for achievement_id, name, description, icon, tier, points, category in default_achievements:
            cursor.execute("SELECT COUNT(*) FROM achievements WHERE id = ?", (achievement_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO achievements (id, name, description, icon, tier, points, category) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (achievement_id, name, description, icon, tier, points, category))
        
        conn.commit()

def log_audit(case_id, action, details, performed_by):
    """Log audit trail"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (case_id, action, details, performed_by) VALUES (?, ?, ?, ?)",
            (case_id, action, details, performed_by)
        )
        conn.commit()
