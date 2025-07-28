import streamlit as st
import uuid
import os
from datetime import datetime
from models import create_case
from utils import validate_case_data, save_uploaded_file, get_dropdown_options
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
        st.subheader("Enter New Case Details")
        
        # Auto-generate Case ID
        if "auto_case_id" not in st.session_state:
            st.session_state.auto_case_id = f"CASE{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Auto-generated Case ID
        case_id = st.text_input("Case ID *", value=st.session_state.auto_case_id, disabled=True, help="Auto-generated unique case ID")
        
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            region = st.selectbox("Region *", options["regions"])
        with col2:
            # Auto-fill "Referred By" based on user's stored referred_by value
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
                    "Admin": "Compliance Team"
                }
                mapped_value = function_mapping.get(user_function, user_function) if user_function else None
                if mapped_value and mapped_value in referred_by_options:
                    default_index = referred_by_options.index(mapped_value)
            
            referred_by = st.selectbox("Referred By *", referred_by_options, index=default_index)
        with col3:
            case_date = st.date_input("Case Date *", datetime.today())
        
        status = st.selectbox("Status", ["Draft", "Submitted"], index=0)
        
        # Case description with AI enhancement
        st.markdown("**Case Description ***")
        
        # Container for text area with positioned button
        st.markdown("""
        <style>
        .enhance-container {
            position: relative;
        }
        .enhance-button {
            position: absolute;
            bottom: 5px;
            right: 5px;
            z-index: 1000;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Text area with relative positioning for button overlay
        case_description = st.text_area(
            "Case Description",
            placeholder="Provide detailed description of the case",
            height=120,
            key="case_description_input",
            label_visibility="collapsed"
        )
        
        # Small enhance button positioned at bottom-right  
        col1, col2 = st.columns([5, 1])
        with col2:
            st.markdown("<div style='text-align: right; margin-top: -25px;'>", unsafe_allow_html=True)
            enhance_desc = st.form_submit_button(
                "✨ Enhance", 
                help="Use AI to improve case description",
                use_container_width=False
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Show enhanced description if available
        if "enhanced_case_description" in st.session_state:
            case_description = st.text_area(
                "Enhanced Case Description",
                value=st.session_state.enhanced_case_description,
                height=120,
                key="enhanced_description_display"
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
        
        # Handle description enhancement
        if enhance_desc and st.session_state.get("case_description_input"):
            with st.spinner("Enhancing description with AI..."):
                enhanced_prompt = f"""
                Please enhance and improve the following case description for a fraud investigation report. 
                Make it more professional, detailed, and comprehensive while maintaining accuracy:
                
                Original description: {st.session_state.case_description_input}
                
                Please provide an enhanced version that:
                1. Uses professional fraud investigation terminology
                2. Structures information clearly
                3. Highlights key risk factors
                4. Maintains factual accuracy
                5. Follows banking industry standards
                
                Do not use any bold formatting with asterisks in the output.
                """
                
                enhanced_description = query_gemini(enhanced_prompt, max_tokens=800)
                st.session_state.enhanced_case_description = enhanced_description
                st.rerun()
        
        # Handle form submission
        if save_draft or submit_final:
            case_data = {
                "case_id": st.session_state.auto_case_id,
                "lan": lan.strip(),
                "case_type": case_type,
                "product": product,
                "region": region,
                "referred_by": referred_by,
                "case_description": (case_description or "").strip(),
                "case_date": case_date.strftime("%Y-%m-%d"),
                "status": "Submitted" if submit_final else "Draft",
                "case_source": "Case Entry Form",
                # Demographics
                "customer_name": customer_name.strip(),
                "customer_dob": customer_dob.strftime("%Y-%m-%d"),
                "customer_pan": customer_pan.strip().upper(),
                "customer_mobile": customer_mobile.strip(),
                "customer_email": customer_email.strip().lower(),
                "branch_location": branch_location.strip(),
                "loan_amount": loan_amount,
                "disbursement_date": disbursement_date.strftime("%Y-%m-%d")
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
