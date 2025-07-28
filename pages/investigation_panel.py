import streamlit as st
import pandas as pd
from datetime import datetime, date
from auth import require_role, get_current_user
from models import get_cases_by_status, get_case_by_id, update_case_status, get_case_comments
from database import get_db_connection, log_audit
from utils import generate_case_id
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

@require_role(["Investigator", "Admin"])
def show():
    """Investigation Panel for detailed case investigation and PDF report generation"""
    st.title("🔍 Investigation Panel")
    st.markdown("**Complete investigation workflow with case management and detailed reporting**")
    
    # Tab structure
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Case Management", "🔍 Investigation Details", "📊 Investigation Analytics", "📄 Generate PDF Report"])
    
    with tab1:
        show_case_management()
    
    with tab2:
        show_investigation_details()
    
    with tab3:
        show_investigation_analytics()
    
    with tab4:
        show_pdf_generation()

def show_case_management():
    """Show case management interface combining case entry and review functionality"""
    st.subheader("📋 Case Management")
    
    # Get current user info
    current_user = get_current_user()
    if isinstance(current_user, str):
        current_user = {"username": current_user, "name": current_user, "team": "Investigation", "referred_by": current_user}
    elif current_user is None:
        current_user = {"username": "Unknown", "name": "Unknown", "team": "Investigation", "referred_by": "Unknown"}
    
    # Two columns for case entry and case review
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📝 Quick Case Entry")
        st.info("💡 **Auto-fill feature:** If you select an existing case ID, demographic details will auto-populate from the Case Entry system.")
        
        with st.form("quick_case_entry"):
            # Case ID input with auto-generation and auto-fetch functionality
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                # Auto-generate Case ID if creating new case
                if "investigation_case_id" not in st.session_state:
                    st.session_state.investigation_case_id = generate_case_id()
                case_id = st.text_input("Case ID *", value=st.session_state.investigation_case_id, help="Format: CASE20250728CE806A - Auto-generated or enter existing")
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                auto_fill = st.form_submit_button("🔍 Fetch Details")
            with col_c:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🔄 New ID"):
                    st.session_state.investigation_case_id = generate_case_id()
                    st.rerun()
            
            # Initialize default values
            default_values = {
                "lan": "",
                "customer_name": "",
                "customer_mobile": "",
                "customer_email": "",
                "customer_pan": "",
                "loan_amount": "",
                "branch_location": "",
                "case_description": "",
                "case_type": "",
                "product": "",
                "region": "",
                "referred_by": "",
                "case_date": "",
                "disbursement_date": "",
                "customer_dob": ""
            }
            
            # Check for auto-fill data or handle auto-fill button click
            if auto_fill and case_id.strip():
                # Fetch case details from database
                case_data = get_case_by_id(case_id.strip())
                if case_data:
                    st.success(f"✅ Case details fetched for {case_id}")
                    default_values.update({
                        "lan": case_data.get("lan", ""),
                        "customer_name": case_data.get("customer_name", ""),
                        "customer_mobile": case_data.get("customer_mobile", ""),
                        "customer_email": case_data.get("customer_email", ""),
                        "customer_pan": case_data.get("customer_pan", ""),
                        "loan_amount": str(case_data.get("loan_amount", "")),
                        "branch_location": case_data.get("branch_location", ""),
                        "case_description": case_data.get("case_description", ""),
                        "case_type": case_data.get("case_type", ""),
                        "product": case_data.get("product", ""),
                        "region": case_data.get("region", ""),
                        "referred_by": case_data.get("referred_by", ""),
                        "case_date": case_data.get("case_date", ""),
                        "disbursement_date": case_data.get("disbursement_date", ""),
                        "customer_dob": case_data.get("customer_dob", "")
                    })
                else:
                    st.warning(f"⚠️ Case ID '{case_id}' not found in system")
            elif "autofill_data" in st.session_state and st.session_state.autofill_case_id == case_id:
                # Use existing session data
                auto_data = st.session_state.autofill_data
                default_values.update(auto_data)
            
            # Display all fetched/auto-filled fields
            st.markdown("#### 📋 Case Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                lan = st.text_input("LAN *", value=default_values["lan"])
                case_type = st.text_input("Case Type", value=default_values["case_type"])
            with col2:
                product = st.text_input("Product", value=default_values["product"])
                region = st.text_input("Region", value=default_values["region"])
            with col3:
                referred_by = st.text_input("Referred By", value=default_values["referred_by"])
                case_date = st.text_input("Case Date", value=default_values["case_date"])
            
            st.markdown("#### 👤 Customer Demographics")
            col1, col2, col3 = st.columns(3)
            with col1:
                customer_name = st.text_input("Customer Name *", value=default_values["customer_name"])
                customer_pan = st.text_input("PAN", value=default_values["customer_pan"])
            with col2:
                customer_mobile = st.text_input("Mobile Number *", value=default_values["customer_mobile"])
                customer_dob = st.text_input("Date of Birth", value=default_values["customer_dob"])
            with col3:
                customer_email = st.text_input("Email ID", value=default_values["customer_email"])
            
            st.markdown("#### 🏦 Loan Details")
            col1, col2 = st.columns(2)
            with col1:
                loan_amount = st.text_input("Loan Amount", value=default_values["loan_amount"])
            with col2:
                branch_location = st.text_input("Branch/Location", value=default_values["branch_location"])
                disbursement_date = st.text_input("Disbursement Date", value=default_values["disbursement_date"])
            
            case_description = st.text_area("Case Description *", value=default_values["case_description"], height=100)
            
            case_type = st.selectbox("Case Type *", ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"], 
                                   index=0 if not default_values["case_type"] else ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"].index(default_values["case_type"]) if default_values["case_type"] in ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"] else 0)
            
            st.markdown("---")
            col_submit1, col_submit2 = st.columns(2)
            
            with col_submit1:
                if st.form_submit_button("💾 Save as Draft", use_container_width=True):
                    if case_id and lan and case_description:
                        # Create comprehensive case data with all demographic details
                        case_data = {
                            "case_id": case_id,
                            "lan": lan,
                            "case_type": case_type,
                            "product": product or "Investigation",
                            "region": region or current_user.get("team", "Investigation"),
                            "referred_by": referred_by or current_user.get("referred_by", current_user.get("name", "")),
                            "case_description": case_description,
                            "case_date": case_date or datetime.now().date().strftime("%Y-%m-%d"),
                            "status": "Draft",
                            "case_source": "Investigation Panel",
                            # Add all demographic details
                            "customer_name": customer_name,
                            "customer_mobile": customer_mobile,
                            "customer_email": customer_email,
                            "customer_pan": customer_pan,
                            "customer_dob": customer_dob,
                            "loan_amount": float(loan_amount) if loan_amount and str(loan_amount).replace('.', '').replace('-', '').isdigit() else None,
                            "branch_location": branch_location,
                            "disbursement_date": disbursement_date
                        }
                        
                        # Create case using the models function
                        from models import create_case
                        success, message = create_case(case_data, current_user.get("username", "Unknown"))
                        
                        if success:
                            log_audit(case_id, "Case Saved as Draft", f"Created by Investigator: {current_user.get('username')}", current_user.get("username"))
                            st.success(f"✅ Case {case_id} saved as draft!")
                        else:
                            st.error(f"❌ Error saving case: {message}")
                    else:
                        st.error("❌ Please fill all required fields (Case ID, LAN, Customer Name, Mobile, Description)")
            
            with col_submit2:
                if st.form_submit_button("🚀 Submit for Review", use_container_width=True):
                    if case_id and lan and customer_name and customer_mobile and case_description:
                        # Create comprehensive case data with all demographic details
                        case_data = {
                            "case_id": case_id,
                            "lan": lan,
                            "case_type": case_type,
                            "product": product or "Investigation",
                            "region": region or current_user.get("team", "Investigation"),
                            "referred_by": referred_by or current_user.get("referred_by", current_user.get("name", "")),
                            "case_description": case_description,
                            "case_date": case_date or datetime.now().date().strftime("%Y-%m-%d"),
                            "status": "Submitted",
                            "case_source": "Investigation Panel",
                            # Add all demographic details for reviewer workflow
                            "customer_name": customer_name,
                            "customer_mobile": customer_mobile,
                            "customer_email": customer_email,
                            "customer_pan": customer_pan,
                            "customer_dob": customer_dob,
                            "loan_amount": float(loan_amount) if loan_amount and str(loan_amount).replace('.', '').replace('-', '').isdigit() else None,
                            "branch_location": branch_location,
                            "disbursement_date": disbursement_date
                        }
                        
                        # Create case using the models function
                        from models import create_case
                        success, message = create_case(case_data, current_user.get("username", "Unknown"))
                        
                        if success:
                            log_audit(case_id, "Case Submitted for Review", f"Submitted by Investigator: {current_user.get('username')} with complete demographics", current_user.get("username"))
                            st.success(f"✅ Case {case_id} submitted for review with complete customer details!")
                            st.info("📋 Case is now available in the reviewer workflow with all demographic information.")
                        else:
                            st.error(f"❌ Error submitting case: {message}")
                    else:
                        st.error("❌ Please fill all required fields (Case ID, LAN, Customer Name, Mobile, Description)")
                else:
                    st.error("❌ Please fill all required fields")
    
    with col2:
        st.markdown("#### 📂 Cases for Investigation")
        
        # Get cases under investigation
        investigation_cases = []
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT case_id, lan, case_type, case_description, created_at, status
                FROM cases 
                WHERE status IN ('Submitted', 'Under Review', 'Under Investigation')
                ORDER BY created_at DESC
                LIMIT 10
            """)
            investigation_cases = cursor.fetchall()
        
        if investigation_cases:
            # Case selection via selectbox instead of buttons
            case_options = [f"{case['case_id']} - {case['case_type']}" for case in investigation_cases]
            selected_case_option = st.selectbox("Select a case to investigate:", [""] + case_options)
            
            if selected_case_option:
                selected_case_id = selected_case_option.split(" - ")[0]
                st.session_state.selected_case_for_investigation = selected_case_id
                
                # Show selected case details
                selected_case = next(case for case in investigation_cases if case['case_id'] == selected_case_id)
                with st.expander(f"📋 Selected Case Details", expanded=True):
                    st.markdown(f"**Case ID:** {selected_case['case_id']}")
                    st.markdown(f"**LAN:** {selected_case['lan']}")
                    st.markdown(f"**Type:** {selected_case['case_type']}")
                    st.markdown(f"**Status:** {selected_case['status']}")
                    st.markdown(f"**Description:** {selected_case['case_description']}")
                    
                    if st.button("🔍 Start Investigation", use_container_width=True):
                        st.info("✅ Case selected for investigation. Switch to 'Investigation Details' tab to continue.")
        else:
            st.info("📭 No cases available for investigation")

def show_investigation_details():
    """Show detailed investigation form"""
    st.subheader("🔍 Investigation Details")
    
    # Case selection
    selected_case = st.session_state.get("selected_case_for_investigation")
    
    if not selected_case:
        st.info("🔍 Please select a case from the Case Management tab to start investigation")
        return
    
    # Get case details
    case_details = get_case_by_id(selected_case)
    if not case_details:
        st.error("❌ Case not found")
        return
    
    st.markdown(f"### Investigating Case: {selected_case}")
    st.markdown(f"**LAN:** {case_details['lan']} | **Type:** {case_details['case_type']}")
    
    # Investigation form
    with st.form("investigation_details_form"):
        st.markdown("#### 📋 Investigation Findings")
        
        # Document Verification Section
        st.markdown("**Document Verification**")
        col1, col2 = st.columns(2)
        with col1:
            pan_verification = st.selectbox("PAN Verification", ["Pending", "Verified", "Failed", "Suspicious"])
            aadhaar_verification = st.selectbox("Aadhaar Verification", ["Pending", "Verified", "Failed", "Suspicious"])
        with col2:
            bank_statement_verification = st.selectbox("Bank Statement Verification", ["Pending", "Verified", "Failed", "Suspicious"])
            address_verification = st.selectbox("Address Verification", ["Pending", "Verified", "Failed", "Suspicious"])
        
        # Employment and Mobile Verification
        st.markdown("**Employment & Contact Verification**")
        col3, col4 = st.columns(2)
        with col3:
            employment_verification = st.selectbox("Employment Verification", ["Pending", "Verified", "Failed", "Suspicious"])
            mobile_verification = st.selectbox("Mobile Number Verification", ["Pending", "Verified", "Failed", "Suspicious"])
        with col4:
            cibil_review = st.selectbox("CIBIL Review", ["Pending", "Clear", "Concerns", "Red Flags"])
            form26as_review = st.selectbox("Form 26AS Review", ["Pending", "Clear", "Concerns", "Red Flags"])
        
        # Investigation Summary
        st.markdown("**Investigation Summary**")
        modus_operandi = st.text_area("Modus Operandi Summary", height=100, 
                                     placeholder="Describe the fraud technique/method used...")
        
        root_cause_analysis = st.text_area("Root Cause Analysis", height=100,
                                         placeholder="Identify key lapses or manipulation techniques...")
        
        # Recommended Actions
        st.markdown("**Recommended Actions**")
        col5, col6 = st.columns(2)
        with col5:
            business_action = st.text_input("Business Team Action")
            rcu_action = st.text_input("RCU/Credit Action")
            orm_action = st.text_input("ORM/Policy Action")
        with col6:
            compliance_action = st.text_input("Compliance Action")
            it_action = st.text_input("IT Action")
            legal_action = st.text_input("Legal Action")
        
        # Investigation Status
        investigation_status = st.selectbox("Investigation Status", 
                                          ["In Progress", "Completed", "Requires Review", "Escalated"])
        
        investigation_comments = st.text_area("Investigation Comments", height=100)
        
        # Submit investigation
        if st.form_submit_button("💾 Save Investigation Details", use_container_width=True):
            current_user = get_current_user() or {}
            
            # Save investigation details to database
            investigation_data = {
                'case_id': selected_case,
                'pan_verification': pan_verification,
                'aadhaar_verification': aadhaar_verification,
                'bank_statement_verification': bank_statement_verification,
                'address_verification': address_verification,
                'employment_verification': employment_verification,
                'mobile_verification': mobile_verification,
                'cibil_review': cibil_review,
                'form26as_review': form26as_review,
                'modus_operandi': modus_operandi,
                'root_cause_analysis': root_cause_analysis,
                'business_action': business_action,
                'rcu_action': rcu_action,
                'orm_action': orm_action,
                'compliance_action': compliance_action,
                'it_action': it_action,
                'legal_action': legal_action,
                'investigation_status': investigation_status,
                'investigation_comments': investigation_comments,
                'investigated_by': current_user.get('username'),
                'investigation_date': datetime.now()
            }
            
            # Create investigation details table if not exists and save data
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Create investigation table if not exists
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investigation_details (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_id TEXT NOT NULL,
                        pan_verification TEXT,
                        aadhaar_verification TEXT,
                        bank_statement_verification TEXT,
                        address_verification TEXT,
                        employment_verification TEXT,
                        mobile_verification TEXT,
                        cibil_review TEXT,
                        form26as_review TEXT,
                        modus_operandi TEXT,
                        root_cause_analysis TEXT,
                        business_action TEXT,
                        rcu_action TEXT,
                        orm_action TEXT,
                        compliance_action TEXT,
                        it_action TEXT,
                        legal_action TEXT,
                        investigation_status TEXT,
                        investigation_comments TEXT,
                        investigated_by TEXT,
                        investigation_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (case_id) REFERENCES cases (case_id)
                    )
                ''')
                
                # Insert or update investigation details
                cursor.execute('''
                    INSERT OR REPLACE INTO investigation_details (
                        case_id, pan_verification, aadhaar_verification, bank_statement_verification,
                        address_verification, employment_verification, mobile_verification, 
                        cibil_review, form26as_review, modus_operandi, root_cause_analysis,
                        business_action, rcu_action, orm_action, compliance_action, 
                        it_action, legal_action, investigation_status, investigation_comments,
                        investigated_by, investigation_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    investigation_data['case_id'],
                    investigation_data['pan_verification'],
                    investigation_data['aadhaar_verification'],
                    investigation_data['bank_statement_verification'],
                    investigation_data['address_verification'],
                    investigation_data['employment_verification'],
                    investigation_data['mobile_verification'],
                    investigation_data['cibil_review'],
                    investigation_data['form26as_review'],
                    investigation_data['modus_operandi'],
                    investigation_data['root_cause_analysis'],
                    investigation_data['business_action'],
                    investigation_data['rcu_action'],
                    investigation_data['orm_action'],
                    investigation_data['compliance_action'],
                    investigation_data['it_action'],
                    investigation_data['legal_action'],
                    investigation_data['investigation_status'],
                    investigation_data['investigation_comments'],
                    investigation_data['investigated_by'],
                    investigation_data['investigation_date']
                ))
                
                conn.commit()
                
                # Add investigation comment to case comments for reviewer workflow
                from models import add_case_comment
                investigation_summary = f"""Investigation Summary:
                
Document Verification:
- PAN: {pan_verification}
- Aadhaar: {aadhaar_verification}  
- Bank Statement: {bank_statement_verification}
- Address: {address_verification}

Contact & Employment:
- Employment: {employment_verification}
- Mobile: {mobile_verification}
- CIBIL: {cibil_review}
- Form 26AS: {form26as_review}

Analysis:
- Modus Operandi: {modus_operandi[:100]}{'...' if len(modus_operandi) > 100 else ''}
- Root Cause: {root_cause_analysis[:100]}{'...' if len(root_cause_analysis) > 100 else ''}

Status: {investigation_status}
Comments: {investigation_comments[:100]}{'...' if len(investigation_comments) > 100 else ''}
                """
                
                add_case_comment(
                    selected_case, 
                    investigation_summary, 
                    "Investigation Report", 
                    current_user.get('username', 'Investigator')
                )
                
                # Update case status based on investigation status
                if investigation_status == "Completed":
                    update_case_status(selected_case, "Under Review", current_user, "Investigation completed - ready for review")
                elif investigation_status == "Escalated":
                    update_case_status(selected_case, "Escalated", current_user, "Investigation escalated")
                
                st.success("✅ Investigation details saved successfully!")
                st.info("📋 Investigation findings have been added to case comments for reviewer workflow.")
                
                log_audit(
                    selected_case, 
                    "Investigation Details Saved", 
                    f"Investigation completed by {current_user.get('username')} - Status: {investigation_status}", 
                    current_user.get('username')
                )

def show_investigation_analytics():
    """Show investigation analytics and metrics"""
    st.subheader("📊 Investigation Analytics")
    
    # Get investigation statistics
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Investigation status distribution
        cursor.execute("""
            SELECT investigation_status, COUNT(*) as count
            FROM investigation_details
            GROUP BY investigation_status
        """)
        status_data = cursor.fetchall()
        
        # Verification results
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN field_verification_status = 'Verified' THEN 1 ELSE 0 END) as field_verified,
                SUM(CASE WHEN field_verification_status = 'Failed' THEN 1 ELSE 0 END) as field_failed,
                SUM(CASE WHEN document_verification_status = 'Verified' THEN 1 ELSE 0 END) as document_verified,
                SUM(CASE WHEN document_verification_status = 'Failed' THEN 1 ELSE 0 END) as document_failed,
                SUM(CASE WHEN reference_verification_status = 'Verified' THEN 1 ELSE 0 END) as reference_verified,
                SUM(CASE WHEN reference_verification_status = 'Failed' THEN 1 ELSE 0 END) as reference_failed
            FROM investigation_details
        """)
        verification_data = cursor.fetchone()
    
    if status_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Investigation Status Distribution")
            if status_data:
                # Convert to list of tuples and create DataFrame
                data_list = [(row[0], row[1]) for row in status_data]
                status_df = pd.DataFrame(data_list)
                status_df.columns = ['Status', 'Count']
                st.bar_chart(status_df.set_index('Status'))
        
        with col2:
            st.markdown("#### Verification Success Rates")
            if verification_data:
                metrics_data = {
                    'Field': [verification_data['field_verified'] or 0, verification_data['field_failed'] or 0],
                    'Document': [verification_data['document_verified'] or 0, verification_data['document_failed'] or 0],
                    'Reference': [verification_data['reference_verified'] or 0, verification_data['reference_failed'] or 0]
                }
                if any(sum(v) for v in metrics_data.values()):
                    # Create DataFrame with proper structure
                    metrics_df = pd.DataFrame.from_dict(metrics_data, orient='index')
                    metrics_df.columns = ['Verified', 'Failed']
                    st.bar_chart(metrics_df.T)
    else:
        st.info("📊 No investigation data available yet")

def show_pdf_generation():
    """Generate detailed PDF investigation report"""
    st.subheader("📄 Generate PDF Investigation Report")
    
    # Case selection for PDF generation
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT case_id, lan, case_type FROM cases ORDER BY created_at DESC")
        cases = cursor.fetchall()
    
    if not cases:
        st.info("📭 No cases available for report generation")
        return
    
    case_options = [f"{case['case_id']} - {case['lan']} ({case['case_type']})" for case in cases]
    selected_case_option = st.selectbox("Select Case for PDF Report", case_options)
    
    if selected_case_option:
        selected_case_id = selected_case_option.split(" - ")[0]
        
        # Get case and investigation details
        case_details = get_case_by_id(selected_case_id)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM investigation_details WHERE case_id = ?", (selected_case_id,))
            investigation_details = cursor.fetchone()
        
        if st.button("📄 Generate PDF Report", use_container_width=True):
            if case_details:
                pdf_buffer = generate_investigation_pdf_report(case_details, investigation_details)
                
                st.download_button(
                    label="📥 Download Investigation Report PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Investigation_Report_{selected_case_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                
                st.success("✅ PDF report generated successfully!")
            else:
                st.error("❌ Case details not found")

def generate_investigation_pdf_report(case_details, investigation_details):
    """Generate PDF report using ReportLab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Convert sqlite3.Row to dict for easier access
    if case_details:
        case_dict = dict(case_details)
    else:
        case_dict = {}
    
    if investigation_details:
        investigation_dict = dict(investigation_details)
    else:
        investigation_dict = {}
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph("Investigation Report on Actual or Suspected Frauds", title_style))
    story.append(Paragraph("(Vide Chapter IV)", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # PART A: FRAUD REPORT
    story.append(Paragraph("PART A: FRAUD REPORT", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # NBFC Details
    nbfc_data = [
        ["Name of NBFC", "Aditya Birch Capital Limited"],
        ["Fraud Number", case_dict.get('case_id', 'N/A')],
    ]
    
    # Branch Details
    branch_data = [
        ["Name of the Branch", case_dict.get('branch_location', 'N/A')],
        ["Branch Type", "Branch Office"],
        ["Place", case_dict.get('branch_location', 'N/A')],
        ["District", "N/A"],
        ["State", "N/A"]
    ]
    
    # Create tables
    for title, data in [("NBFC Information", nbfc_data), ("Branch Details", branch_data)]:
        story.append(Paragraph(title, styles['Heading3']))
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
    
    # Case Details
    case_data = [
        ["Name of Principal Party/Account", "[Redacted for Privacy]"],
        ["Area of Operations", case_dict.get('case_type', 'N/A')],
        ["Nature of Fraud", case_dict.get('case_type', 'N/A')],
        ["Total Amount Involved", f"₹{case_dict.get('loan_amount', 'N/A')}"],
        ["Date of Occurrence", str(case_dict.get('case_date', 'N/A'))],
        ["Date of Detection", str(case_dict.get('created_at', 'N/A'))[:10]],
    ]
    
    story.append(Paragraph("Case Information", styles['Heading3']))
    case_table = Table(case_data, colWidths=[2*inch, 4*inch])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(case_table)
    story.append(Spacer(1, 12))
    
    # Brief History
    story.append(Paragraph("Brief History", styles['Heading3']))
    story.append(Paragraph(case_details.get('case_description', 'N/A'), styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Loan Account Details
    loan_data = [
        ["LAN No.", case_details.get('lan', 'N/A')],
        ["Product", case_details.get('product', 'N/A')],
        ["Sanction Amount", f"₹{case_details.get('loan_amount', 'N/A')}"],
        ["Sanction Date", str(case_details.get('disbursement_date', 'N/A'))],
        ["Loan Status", case_details.get('status', 'N/A')]
    ]
    
    story.append(Paragraph("Loan Account Details", styles['Heading3']))
    loan_table = Table(loan_data, colWidths=[2*inch, 4*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(loan_table)
    story.append(Spacer(1, 12))
    
    # Investigation Findings (if available)
    if investigation_details:
        story.append(Paragraph("Investigation Findings", styles['Heading3']))
        
        findings_data = [
            ["PAN Verification", investigation_details.get('pan_verification', 'N/A')],
            ["Aadhaar Verification", investigation_details.get('aadhaar_verification', 'N/A')],
            ["Bank Statement Verification", investigation_details.get('bank_statement_verification', 'N/A')],
            ["Address Verification", investigation_details.get('address_verification', 'N/A')],
            ["Employment Verification", investigation_details.get('employment_verification', 'N/A')],
            ["Mobile Verification", investigation_details.get('mobile_verification', 'N/A')],
            ["CIBIL Review", investigation_details.get('cibil_review', 'N/A')],
            ["Form 26AS Review", investigation_details.get('form26as_review', 'N/A')]
        ]
        
        findings_table = Table(findings_data, colWidths=[2*inch, 4*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(findings_table)
        story.append(Spacer(1, 12))
        
        # Modus Operandi
        if investigation_details.get('modus_operandi'):
            story.append(Paragraph("Modus Operandi Summary", styles['Heading3']))
            story.append(Paragraph(investigation_details.get('modus_operandi'), styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Root Cause Analysis
        if investigation_details.get('root_cause_analysis'):
            story.append(Paragraph("Root Cause Analysis", styles['Heading3']))
            story.append(Paragraph(investigation_details.get('root_cause_analysis'), styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Recommended Actions
        actions_data = [
            ["Business Team", investigation_details.get('business_action', 'N/A')],
            ["RCU or Credit", investigation_details.get('rcu_action', 'N/A')],
            ["ORM or Policy", investigation_details.get('orm_action', 'N/A')],
            ["Compliance", investigation_details.get('compliance_action', 'N/A')],
            ["IT", investigation_details.get('it_action', 'N/A')],
            ["Legal", investigation_details.get('legal_action', 'N/A')]
        ]
        
        story.append(Paragraph("Recommended Actions", styles['Heading3']))
        actions_table = Table(actions_data, colWidths=[2*inch, 4*inch])
        actions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(actions_table)
        story.append(Spacer(1, 12))
    
    # Annexures
    story.append(Paragraph("Annexures", styles['Heading3']))
    annexures = [
        "Annexure 1: Fabricated Documents",
        "Annexure 2: Site Visit Reports", 
        "Annexure 3: Statement of Account"
    ]
    for annexure in annexures:
        story.append(Paragraph(f"• {annexure}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%d-%b-%Y %H:%M')}", styles['Normal']))
    story.append(Paragraph("Generated by: Tathya Case Management System", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer