import streamlit as st
import uuid
from datetime import datetime, timedelta
from models import create_case
from utils import validate_case_data, save_uploaded_file, get_dropdown_options
from auth import get_current_user

def show():
    """Display case entry page"""
    st.title("📄 Case Entry")
    
    current_user = get_current_user()
    options = get_dropdown_options()
    
    with st.form("case_entry_form"):
        st.subheader("Enter New Case Details")
        
        # Auto-generate Case ID
        if "auto_case_id" not in st.session_state:
            st.session_state.auto_case_id = f"CASE{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Basic Case Information
        case_id = st.text_input("Case ID *", value=st.session_state.auto_case_id, disabled=True, help="Auto-generated unique case ID")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            lan = st.text_input("LAN *", placeholder="Enter LAN number")
        with col2:
            case_type = st.selectbox("Type of Case *", options["case_types"])
        with col3:
            product = st.selectbox("Product *", options["products"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            region = st.selectbox("Region *", options["regions"])
        with col2:
            referred_by = st.selectbox("Referred By *", options["referred_by"])
        with col3:
            case_date = st.date_input("Case Date *", datetime.today())
        
        col1, col2 = st.columns(2)
        with col1:
            case_source = st.selectbox("Source of Case *", options["case_sources"])
        with col2:
            status = st.selectbox("Status", ["Draft", "Submitted"], index=0)
        
        # Case description
        case_description = st.text_area(
            "Case Description *",
            placeholder="Provide detailed description of the case",
            height=120
        )
        
        # Demographic Details Section
        st.subheader("Customer Demographics")
        st.info("ℹ️ Auto-fetch functionality will be available in future releases")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_name = st.text_input("Customer Name", placeholder="Auto-fetch available in future")
            customer_dob = st.date_input("Date of Birth", value=None, help="Auto-fetch available in future")
            customer_pan = st.text_input("PAN", placeholder="Auto-fetch available in future")
        with col2:
            customer_mobile = st.text_input("Mobile Number", placeholder="Auto-fetch available in future")
            customer_email = st.text_input("Email ID", placeholder="Auto-fetch available in future")
            branch_location = st.text_input("Branch / Location", placeholder="Auto-fetch available in future")
        with col3:
            customer_type = st.selectbox("Customer Type", options["customer_types"])
            kyc_status = st.selectbox("KYC Status", options["kyc_status"])
            risk_category = st.selectbox("Risk Category", options["risk_categories"], help="Applicable for risk assessment")
        
        # Address
        customer_address = st.text_area("Customer Address", placeholder="Auto-fetch available in future", height=80)
        
        # Loan Details Section
        st.subheader("Loan Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            loan_amount = st.number_input("Loan Amount (₹)", min_value=0.0, format="%.2f", help="Auto-fetch available in future")
            disbursement_date = st.date_input("Disbursement Date", value=None, help="Auto-fetch available in future")
        with col2:
            repayment_status = st.selectbox("Repayment Status", [""] + options["repayment_status"], help="Auto-fetch available in future")
            linked_accounts = st.text_input("Linked Loan Accounts", placeholder="Auto-fetch available in future")
        
        # SLA Information (Auto-calculated)
        st.subheader("SLA Tracking")
        col1, col2 = st.columns(2)
        with col1:
            fmr1_due = case_date + timedelta(days=14) if case_date else datetime.now().date() + timedelta(days=14)
            st.text_input("FMR-1 Due Date", value=fmr1_due.strftime("%Y-%m-%d"), disabled=True, help="Auto-calculated: Case Date + 14 days")
        with col2:
            document_retention = case_date + timedelta(days=1825) if case_date else datetime.now().date() + timedelta(days=1825) # 5 years
            st.text_input("Document Retention Until", value=document_retention.strftime("%Y-%m-%d"), disabled=True, help="Auto-calculated: Case Date + 5 years")
        
        # File upload
        st.subheader("Supporting Documents")
        uploaded_files = st.file_uploader(
            "Upload supporting documents",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
        )
        
        # Form submission
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            save_draft = st.form_submit_button("💾 Save as Draft", use_container_width=True)
        
        with col2:
            submit_final = st.form_submit_button("📤 Submit Final", use_container_width=True)
        
        # Handle form submission
        if save_draft or submit_final:
            # Calculate SLA dates
            fmr1_due = case_date + timedelta(days=14) if case_date else None
            document_retention = case_date + timedelta(days=1825) if case_date else None  # 5 years
            
            case_data = {
                "case_id": st.session_state.auto_case_id,
                "lan": lan.strip(),
                "case_type": case_type,
                "product": product,
                "region": region,
                "referred_by": referred_by,
                "case_source": case_source,
                # Demographics
                "customer_name": customer_name.strip() if customer_name else "",
                "customer_dob": customer_dob,
                "customer_pan": customer_pan.strip() if customer_pan else "",
                "customer_address": customer_address.strip() if customer_address else "",
                "customer_mobile": customer_mobile.strip() if customer_mobile else "",
                "customer_email": customer_email.strip() if customer_email else "",
                "branch_location": branch_location.strip() if branch_location else "",
                "loan_amount": loan_amount if loan_amount > 0 else None,
                "disbursement_date": disbursement_date,
                "repayment_status": repayment_status if repayment_status else "",
                "linked_loan_accounts": linked_accounts.strip() if linked_accounts else "",
                "customer_type": customer_type,
                "kyc_status": kyc_status,
                "risk_category": risk_category,
                # SLA tracking
                "fmr1_due_date": fmr1_due,
                "document_retention_date": document_retention,
                "case_description": case_description.strip(),
                "case_date": case_date.strftime("%Y-%m-%d"),
                "status": "Submitted" if submit_final else "Draft"
            }
            
            # Validate data
            errors = validate_case_data(case_data)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create case
                success, message = create_case(case_data, current_user)
                
                if success:
                    st.success(f"✅ Case {case_data['status'].lower()} successfully!")
                    
                    # Handle file uploads
                    if uploaded_files:
                        st.info("Uploading files...")
                        upload_success_count = 0
                        
                        for uploaded_file in uploaded_files:
                            file_success, filename = save_uploaded_file(
                                uploaded_file, case_data["case_id"], current_user
                            )
                            if file_success:
                                upload_success_count += 1
                        
                        if upload_success_count > 0:
                            st.success(f"✅ {upload_success_count} file(s) uploaded successfully!")
                    
                    # Generate new case ID for next case
                    st.session_state.auto_case_id = f"CASE{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
                    
                    st.balloons()
                    
                else:
                    st.error(f"❌ {message}")
    
    # Display help information
    with st.expander("ℹ️ Help & Guidelines"):
        st.markdown("""
        ### Case Entry Guidelines:
        
        **Required Fields (marked with *):**
        - Case ID: Must be unique across the system
        - LAN: Loan Account Number
        - Case Description: Detailed explanation of the case
        
        **File Upload:**
        - Supported formats: PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG
        - Maximum file size: 10MB per file
        - Multiple files can be uploaded
        
        **Status Options:**
        - **Draft**: Save case for later completion
        - **Submitted**: Submit case for review process
        
        **Important Notes:**
        - Case ID cannot be changed after creation
        - All uploaded files are securely stored
        - Audit trail is maintained for all actions
        """)
