import sqlite3
from database import get_password_hash, get_db_connection

def bulk_import_users():
    """Import all users from the provided master list"""
    
    # User data from the provided file
    user_data = [
        ("bg390458", "Password", "Rohit Vinayak Shirwadkar", "Investigation", "TL - FRMU Central Investigation", "Initiator", "GRT"),
        ("bg407629", "Password", "Suneel Kumar Ramdeen Vishwakarma", "Process & Analytics", "TL - FRMU Initiatives", "Initiator", "GRT"),
        ("bg429291", "Password", "Suhas Vijay Bhalerao", "Investigation", "Lead - FRMU Investigation", "Initiator", "GRT"),
        ("bg430234", "Password", "Goutam Barman", "Investigation", "Regional Investigation Manager", "Initiator", "Credit Unit"),
        ("bg430299", "Password", "Alphanso Nathaniel Nagalapurkar", "Investigation", "Regional Investigation Manager", "Initiator", "Credit Unit"),
        ("bg435597", "Password", "Ansuya Rajesh Pogula", "Process & Analytics", "Product & Process Manager", "Initiator", "Credit Unit"),
        ("bg450935", "Password", "Narasingh Nath Patnaik", "Investigation", "Location Investigation Manager", "Initiator", "Credit Unit"),
        ("bg451782", "Password", "Aniket .", "Process & Analytics", "Team Member - MIS", "Initiator", "Credit Unit"),
        ("bg453173", "Password", "Suraj Laxman Patil", "Investigation", "FRMU Manager - Investigation", "Initiator", "HR"),
        ("bg457666", "Password", "Thiyagarajan Shanmugasundaram", "Investigation", "Regional Investigation Manager", "Initiator", "HR"),
        ("bg457850", "Password", "Sethuraman G", "Investigation", "Location Investigation Manager", "Initiator", "Policy Team"),
        ("bg457851", "Password", "Soumyajit Dey", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("bg458548", "Password", "Ayushi Mishra", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("bg462182", "Password", "Atul Bharti", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("bg463878", "Password", "Jagruti Anil Bane", "Investigation", "FRMU Manager - Investigation", "Initiator", "GRT"),
        ("bg468635", "Password", "Disha Bipin Mehta", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("bg473039", "Password", "Ajay Omprakash Pardeshi", "Process & Analytics", "Team Member - FRMU", "Initiator", "GRT"),
        ("bg475121", "Password", "Manan Jasmin Bhatt", "Process & Analytics", "Product & Process Manager", "Initiator", "Operation Unit"),
        ("bg486324", "Password", "Ankit Lakra", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("bg488164", "Password", "SURUTHISRI B", "Investigation", "Location Investigation Manager", "Initiator", "GRT"),
        ("VEN95932", "Password", "Subhodip Pandit", "Investigation", "EXECUTIVE", "Initiator", "GRT"),
        ("VEN96228", "Password", "Thiyaneshwaran Arivazagan", "Investigation", "EXECUTIVE", "Initiator", "GRT"),
        ("VEN96943", "Password", "Reeya Amit Kumar Chauhan", "Investigation", "EXECUTIVE", "Initiator", "GRT"),
        ("VEN97271", "Password", "Ashok Kumar Barik", "Investigation", "EXECUTIVE", "Initiator", "GRT"),
        ("BG455072", "Password", "Dhiren Anil Valecha", "Process & Analytics", "Team Member - FRMU", "Initiator", "Legal Unit"),
        ("BG481149", "Password", "Pooja Dinesh Sawant", "Process & Analytics", "Product & Process Manager", "Initiator", "GRT"),
        ("VEN95122", "Password", "Pranali Dharma Diwadkar", "Process & Analytics", "EXECUTIVE", "Initiator", "GRT"),
        ("VEN95761", "Password", "Sagar Nagesh Jali", "Investigation", "EXECUTIVE", "Initiator", "GRT"),
        ("VEN96731", "Password", "Mohd Sharifulhaq Shahabuddin Qadri", "Process & Analytics", "EXECUTIVE", "Initiator", "GRT")
    ]
    
    # Convert "Referred By" abbreviations to full names
    referred_by_mapping = {
        "GRT": "GRT",
        "Credit": "Credit Unit", 
        "HR": "HR",
        "Policy": "Policy Team",
        "Ops": "Operation Unit",
        "Legal": "Legal Unit"
    }
    
    success_count = 0
    error_count = 0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for user_id, password, name, team, designation, role, referred_by in user_data:
            try:
                # Check if user already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user_id,))
                if cursor.fetchone()[0] > 0:
                    print(f"User {user_id} already exists, skipping...")
                    continue
                
                # Map referred_by to full name
                full_referred_by = referred_by_mapping.get(referred_by, referred_by)
                
                # Hash password
                password_hash = get_password_hash(password)
                
                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, email, name, team, 
                                     functional_designation, referred_by, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, password_hash, role, None, name, team, designation, full_referred_by, 1))
                
                success_count += 1
                print(f"Created user: {user_id} - {name}")
                
            except Exception as e:
                error_count += 1
                print(f"Error creating user {user_id}: {str(e)}")
        
        conn.commit()
    
    print(f"\nBulk import completed:")
    print(f"Successfully created: {success_count} users")
    print(f"Errors: {error_count}")
    
    return success_count, error_count

if __name__ == "__main__":
    bulk_import_users()