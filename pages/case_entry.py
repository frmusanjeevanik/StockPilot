import streamlit as st
import uuid
from datetime import datetime
from models import create_case
from utils import validate_case_data, save_uploaded_file, get_dropdown_options
from auth import get_current_user

def show():
    """Display case entry page"""
    
    current_user = get_current_user()
    options = get_dropdown_options()
    
    with st.form("case_entry_form"):
        st.subheader("Enter New Case Details")
        
        # Auto-generate Case ID
        if "auto_case_id" not in st.session_state:
            st.session_state.auto_case_id = f"CASE{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # All fields in rows
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
        
        status = st.selectbox("Status", ["Draft", "Submitted"], index=0)
        
        # Case description
        case_description = st.text_area(
            "Case Description *",
            placeholder="Provide detailed description of the case",
            height=120
        )
        
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
            case_data = {
                "case_id": st.session_state.auto_case_id,
                "lan": lan.strip(),
                "case_type": case_type,
                "product": product,
                "region": region,
                "referred_by": referred_by,
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
