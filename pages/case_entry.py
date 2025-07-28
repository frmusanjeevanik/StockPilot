import streamlit as st
import uuid
import os
from datetime import datetime
from models import create_case
from utils import validate_case_data, save_uploaded_file, get_dropdown_options, generate_case_id
from auth import get_current_user, get_user_function, get_user_referred_by
from google import genai
from google.genai import types

def query_gemini(prompt, max_tokens=1000):
    """Query Gemini API for intelligent responses"""
    try:
        # Initialize Gemini client if not already done
        if not hasattr(st.session_state, 'gemini_client'):
            # Set API key
            api_key = 'AIzaSyAZCvpTcGq-ie_3Vnh2obVaAzrFTnFnDqc'
            os.environ['GEMINI_API_KEY'] = api_key
            st.session_state.gemini_client = genai.Client(api_key=api_key)
        
        client = st.session_state.gemini_client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.3
            )
        )
        
        if response and response.text:
            return response.text
        else:
            return "Unable to generate response - empty response received"
            
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return f"Error generating response: {str(e)}"

def show():
    """Display case entry page"""
    # Check role access - Investigators and Initiators can create cases
    from auth import require_role
    require_role(["Initiator", "Investigator", "Admin"])
    
    st.title("📄 Case Entry")
    
    current_user = get_current_user()
    options = get_dropdown_options()
    

    
    with st.form("case_entry_form"):
        # Apply light background styling to all form elements
        st.markdown("""
        <style>
        .stTextArea > div > div > textarea {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
        }
        .stTextInput > div > div > input {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
        }
        .stSelectbox > div > div > div {
            background-color: #f8f9fa !important;
        }
        .stNumberInput > div > div > input {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.subheader("📝 Enter New Case Details")
        
        # Auto-generate Case ID in format CASE20250728CE806A
        if "auto_case_id" not in st.session_state:
            st.session_state.auto_case_id = generate_case_id()
        
        case_id = st.text_input("Case ID", value=st.session_state.auto_case_id, disabled=True, help="Auto-generated unique case ID in format: CASE20250728CE806A")
        
        # Auto-fill "Referred By" based on current user's information
        current_user_id = get_current_user()
        user_referred_by = get_user_referred_by()
        referred_by_options = options["referred_by"]
        default_index = 0
        
        if user_referred_by and user_referred_by in referred_by_options:
            default_index = referred_by_options.index(user_referred_by)
        elif get_user_function():
            # Fallback to function mapping if no stored referred_by
            user_function = get_user_function()
            function_mapping = {
                "Initiator": "Business Unit",
                "Reviewer": "Operation Unit", 
                "Approver": "Credit Unit",
                "Legal Reviewer": "Legal Unit",
                "Admin": "Compliance Team",
                "Investigator": "Investigation Unit"
            }
            mapped_value = function_mapping.get(user_function, user_function) if user_function else None
            if mapped_value and mapped_value in referred_by_options:
                default_index = referred_by_options.index(mapped_value)
        
        referred_by = st.selectbox("Referred By *", referred_by_options, index=default_index, help=f"Auto-filled based on user: {current_user_id}")
        
        # Customer Demographics Section
        st.subheader("👤 Customer Demographics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_name = st.text_input("Customer Name *", placeholder="Enter full customer name")
        with col2:
            customer_dob = st.date_input("Date of Birth *", max_value=datetime.today())
        with col3:
            customer_pan = st.text_input("PAN *", placeholder="Enter PAN number", max_chars=10)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_mobile = st.text_input("Mobile Number *", placeholder="Enter 10-digit mobile", max_chars=10)
        with col2:
            customer_email = st.text_input("Email ID *", placeholder="Enter email address")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            branch_location = st.text_input("Branch / Location *", placeholder="Enter branch name")
        with col2:
            loan_amount = st.number_input("Loan Amount *", min_value=0.0, step=1000.0, format="%.2f")
        with col3:
            disbursement_date = st.date_input("Disbursement Date *", max_value=datetime.today())
        
        # Case Details Section
        st.subheader("📋 Case Details")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            lan = st.text_input("LAN *", placeholder="Enter LAN number")
        with col2:
            case_type = st.selectbox("Type of Case *", options["case_types"])
        with col3:
            product = st.selectbox("Product *", options["products"])
        
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox("Region *", options["regions"])
        with col2:
            case_date = st.date_input("Case Date *", datetime.today())
        
        # Case description
        st.subheader("📝 Case Description")
        
        case_description = st.text_area(
            "Case Description *",
            placeholder="Provide detailed description of the case",
            height=120,
            key="case_description_input"
        )
        
        # File upload
        st.subheader("📎 Supporting Documents")
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
                "customer_name": (customer_name or "").strip(),
                "customer_dob": customer_dob.strftime("%Y-%m-%d"),
                "customer_pan": (customer_pan or "").strip(),
                "customer_mobile": (customer_mobile or "").strip(),
                "customer_email": (customer_email or "").strip(),
                "branch_location": (branch_location or "").strip(),
                "loan_amount": loan_amount,
                "disbursement_date": disbursement_date.strftime("%Y-%m-%d"),
                "case_type": case_type,
                "product": product,
                "region": region,
                "referred_by": referred_by,
                "case_description": (case_description or "").strip(),
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
                                uploaded_file, case_data["case_id"]
                            )
                            if file_success:
                                upload_success_count += 1
                        
                        if upload_success_count > 0:
                            st.success(f"✅ {upload_success_count} file(s) uploaded successfully!")
                    
                    # Generate new case ID for next case
                    st.session_state.auto_case_id = generate_case_id()
                    
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
