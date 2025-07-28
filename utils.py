import random
import string
from datetime import datetime

def generate_case_id():
    """Generate auto case ID in format: CASE20250728CE806A"""
    # Get current date in YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Generate 2 random uppercase letters
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    
    # Generate 3 random digits
    digits = ''.join(random.choices(string.digits, k=3))
    
    # Generate 1 random uppercase letter
    final_letter = random.choice(string.ascii_uppercase)
    
    # Combine to create case ID
    case_id = f"CASE{date_str}{letters}{digits}{final_letter}"
    
    return case_id

def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return "N/A"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(str(dt_string).replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(dt_string)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if not size_bytes:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_status_color(status):
    """Get color emoji for case status"""
    status_colors = {
        "Draft": "⚪",
        "Submitted": "🔵", 
        "Under Review": "🟡",
        "Approved": "🟢",
        "Rejected": "🔴",
        "Legal Review": "🟣",
        "Closed": "⚫",
        "Under Investigation": "🟠",
        "Investigation Completed": "✅",
        "Escalated": "🚨"
    }
    return status_colors.get(status, "⚪")

def validate_case_data(case_data):
    """Validate case data before submission"""
    errors = []
    
    # Required fields validation
    required_fields = ["case_id", "lan", "customer_name", "customer_mobile", "case_description"]
    for field in required_fields:
        if not case_data.get(field) or str(case_data.get(field)).strip() == "":
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # PAN validation (10 characters alphanumeric)
    if case_data.get("customer_pan") and len(str(case_data["customer_pan"]).strip()) != 10:
        errors.append("PAN must be exactly 10 characters")
    
    # Mobile validation (10 digits)
    if case_data.get("customer_mobile"):
        mobile = str(case_data["customer_mobile"]).strip()
        if not mobile.isdigit() or len(mobile) != 10:
            errors.append("Mobile number must be exactly 10 digits")
    
    # Email validation
    if case_data.get("customer_email"):
        import re
        email = str(case_data["customer_email"]).strip()
        if email:  # Only validate if email is provided
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Please enter a valid email address")
    
    # Loan amount validation
    if case_data.get("loan_amount"):
        try:
            amount = float(case_data["loan_amount"])
            if amount <= 0:
                errors.append("Loan amount must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Loan amount must be a valid number")
    
    return errors


def save_uploaded_file(uploaded_file, case_id):
    """Save uploaded file to uploads directory"""
    import os
    import uuid
    
    if uploaded_file is None:
        return None, "No file uploaded"
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Generate unique filename
        file_extension = uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else ""
        unique_filename = f"{case_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return {
            "file_path": file_path,
            "original_filename": uploaded_file.name,
            "file_size": uploaded_file.size,
            "unique_filename": unique_filename
        }, None
        
    except Exception as e:
        return None, f"Error saving file: {str(e)}"

def get_dropdown_options():
    """Get dropdown options for form fields"""
    return {
        "case_types": [
            "Document Fraud",
            "Identity Fraud", 
            "Financial Fraud",
            "Compliance Violation",
            "Operational Risk",
            "Credit Risk",
            "Market Risk",
            "Cyber Security",
            "Money Laundering",
            "Other"
        ],
        "products": [
            "Personal Loan",
            "Home Loan", 
            "Car Loan",
            "Business Loan",
            "Credit Card",
            "Gold Loan",
            "Education Loan",
            "Two Wheeler Loan",
            "Loan Against Property",
            "Other"
        ],
        "regions": [
            "North",
            "South", 
            "East",
            "West",
            "Central",
            "North East"
        ],
        "referred_by": [
            "Business Unit",
            "Credit Unit",
            "Operation Unit", 
            "Legal Unit",
            "Compliance Team",
            "Investigation Unit",
            "Risk Management",
            "Customer Service",
            "External Auditor",
            "Regulatory Authority"
        ],
        "statuses": [
            "Draft",
            "Submitted",
            "Under Review",
            "Approved",
            "Rejected",
            "Legal Review",
            "Closed",
            "Under Investigation",
            "Investigation Completed"
        ]
    }

def export_cases_to_csv(cases_data):
    """Export cases data to CSV format"""
    import pandas as pd
    import io
    
    if not cases_data:
        return None
    
    # Convert cases data to DataFrame
    df = pd.DataFrame(cases_data)
    
    # Format datetime columns
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    if 'updated_at' in df.columns:
        df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Create CSV buffer
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()