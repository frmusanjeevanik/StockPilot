import os
import uuid
import pandas as pd
from datetime import datetime
import streamlit as st
from models import add_case_document

def save_uploaded_file(uploaded_file, case_id, uploaded_by):
    """Save uploaded file and add to database"""
    if uploaded_file is not None:
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{case_id}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join("uploads", unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add to database
        add_case_document(
            case_id=case_id,
            filename=unique_filename,
            original_filename=uploaded_file.name,
            file_path=file_path,
            file_size=uploaded_file.size,
            uploaded_by=uploaded_by
        )
        
        return True, unique_filename
    
    return False, None

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def export_cases_to_csv(cases, filename=None):
    """Export cases to CSV file"""
    if not cases:
        return None, "No cases to export"
    
    # Convert to DataFrame
    df = pd.DataFrame([dict(case) for case in cases])
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cases_export_{timestamp}.csv"
    
    file_path = os.path.join("exports", filename)
    os.makedirs("exports", exist_ok=True)
    
    # Export to CSV
    df.to_csv(file_path, index=False)
    
    return file_path, "Export successful"

def validate_case_data(case_data):
    """Validate case data"""
    errors = []
    
    required_fields = ["lan", "case_description"]
    for field in required_fields:
        if not case_data.get(field, "").strip():
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    return errors

def get_status_color(status):
    """Get color for status display"""
    status_colors = {
        "Draft": "🟡",
        "Submitted": "🔵",
        "Under Review": "🟠",
        "Approved": "🟢",
        "Rejected": "🔴",
        "Legal Review": "🟣",
        "Closed": "⚫"
    }
    return status_colors.get(status, "⚪")

def format_datetime(dt_string):
    """Format datetime string for display"""
    if dt_string:
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return dt_string
    return "N/A"

def get_dropdown_options():
    """Get dropdown options for forms"""
    return {
        "case_types": ["Lending", "Non Lending"],
        "products": [
            "BL", "BTC PL", "DL", "Drop Line LOC", "Finagg", "INSTI - MORTGAGES", "LAP",
            "Line of Credit", "MLAP", "NA", "PL", "SEG", "SME", "STSL", "STSLP BT + Top - up",
            "STUL", "Term Loan", "Term Loan Infra", "Udyog Plus", "Unsecured BuyOut"
        ],
        "regions": ["East", "North", "South", "West"],
        "referred_by": [
            "Audit Team", "Business Unit", "Collection Unit", "Compliance Team", "Credit Unit",
            "Customer Service", "GRT", "HR", "Legal Unit", "MD / CEO Escalation",
            "Operation Risk Management", "Operation Unit", "Other Function", "Policy Team",
            "Risk Containment Unit", "Sales Unit", "Technical Team"
        ],
        "statuses": ["Draft", "Submitted", "Under Review", "Approved", "Rejected", "Legal Review", "Closed"],
        "customer_types": ["Individual", "Entity"],
        "kyc_status": ["Complete", "Incomplete", "Pending"],
        "risk_categories": ["Low", "Medium", "High"],
        "case_sources": ["Customer Complaint", "Internal Trigger", "Third-party Input"],
        "repayment_status": ["Regular", "Overdue", "NPA", "Closed", "Settled"]
    }
