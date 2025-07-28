import streamlit as st
import requests
import json
from auth import require_role

@require_role(["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Admin"])
def show():
    """AI Assistant using Hugging Face Inference API"""
    st.title("🤖 AI Assistant")
    st.markdown("**AI assistant for case analysis and document drafting using free Hugging Face models**")
    
    # Model selection
    st.subheader("AI Model Selection")
    model_options = {
        "Llama 3.2 (3B)": "meta-llama/Llama-3.2-3B-Instruct",
        "Phi-3 Mini": "microsoft/Phi-3-mini-4k-instruct",
        "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.3",
        "CodeLlama": "codellama/CodeLlama-7b-Instruct-hf"
    }
    
    selected_model_name = st.selectbox("Choose AI Model", list(model_options.keys()), index=0)
    selected_model = model_options[selected_model_name]
    
    st.info(f"Using {selected_model_name} - Free model via Hugging Face Inference API")
    
    # Quick Action Buttons
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Case Analysis", use_container_width=True):
            st.session_state.free_ai_template = "case_analysis"
    
    with col2:
        if st.button("📝 Draft Notice", use_container_width=True):
            st.session_state.free_ai_template = "draft_notice"
    
    with col3:
        if st.button("🔍 Investigation Guide", use_container_width=True):
            st.session_state.free_ai_template = "investigation_guide"
    
    with col4:
        if st.button("💬 Chat Assistant", use_container_width=True):
            st.session_state.free_ai_template = "free_chat"
    
    st.divider()
    
    # Template-based interface
    if "free_ai_template" in st.session_state:
        template = st.session_state.free_ai_template
        
        if template == "case_analysis":
            case_analysis_tool(selected_model)
        elif template == "draft_notice":
            draft_notice_tool(selected_model)
        elif template == "investigation_guide":
            investigation_guide_tool(selected_model)
        elif template == "free_chat":
            free_chat_assistant(selected_model)
    else:
        # Default view
        st.subheader("Free AI Assistant Features")
        st.markdown("""
        **Available Tools:**
        
        1. **Case Analysis**: Analyze case details and suggest next steps
        2. **Draft Notice**: Create basic notices and communications
        3. **Investigation Guide**: Get guidance on investigation procedures
        4. **Chat Assistant**: Interactive assistance for general queries
        
        **Note**: This AI assistant provides comprehensive functionality using free models without API costs.
        """)

def query_huggingface_model(model_id, prompt, max_tokens=500):
    """Query Hugging Face Inference API"""
    try:
        # Hugging Face Inference API endpoint
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Format prompt for instruction-following models
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.3,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            else:
                return "No response generated"
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error querying model: {str(e)}"

def case_analysis_tool(model_id):
    """Case Analysis Tool"""
    st.subheader("📋 Intelligent Case Analysis")
    
    with st.form("case_analysis_form"):
        case_type = st.selectbox(
            "Case Type",
            ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk", "Other"]
        )
        
        case_details = st.text_area(
            "Case Details",
            placeholder="Describe the case details, allegations, evidence found, and current status",
            height=150
        )
        
        customer_info = st.text_input("Customer Information", placeholder="Customer name, loan amount, branch (optional)")
        
        evidence_available = st.multiselect(
            "Evidence Available",
            ["Bank Statements", "Identity Documents", "Income Proof", "Property Documents", "Employment Records", "Reference Checks", "Field Investigation Report", "Other"]
        )
        
        risk_level = st.selectbox("Preliminary Risk Assessment", ["Low", "Medium", "High", "Critical"])
        
        specific_question = st.text_area(
            "Specific Questions/Concerns",
            placeholder="Any specific aspects you want analyzed or guidance needed",
            height=80
        )
        
        analyze_btn = st.form_submit_button("Generate Comprehensive Analysis", use_container_width=True)
        
        if analyze_btn and case_details:
            with st.spinner("Generating comprehensive case analysis..."):
                evidence_str = ", ".join(evidence_available) if evidence_available else "None specified"
                
                prompt = f"""
                As a senior fraud investigation analyst, provide a comprehensive analysis of this case:
                
                Case Type: {case_type}
                Case Details: {case_details}
                Customer Information: {customer_info}
                Evidence Available: {evidence_str}
                Current Risk Level: {risk_level}
                Specific Questions: {specific_question}
                
                Provide a detailed analysis including:
                
                1. EXECUTIVE SUMMARY
                   - Key findings overview
                   - Risk assessment validation
                   
                2. EVIDENCE EVALUATION
                   - Strength of available evidence
                   - Gaps in evidence collection
                   
                3. FRAUD INDICATORS
                   - Red flags identified
                   - Pattern analysis
                   
                4. RECOMMENDED ACTIONS
                   - Immediate next steps
                   - Investigation priorities
                   - Documentation requirements
                   
                5. RISK MITIGATION
                   - Recommended controls
                   - Monitoring requirements
                   
                6. REGULATORY COMPLIANCE
                   - Reporting obligations
                   - Timeline considerations
                
                Keep the analysis professional, detailed, and actionable for banking operations.
                """
                
                result = query_huggingface_model(model_id, prompt, max_tokens=1200)
                
                st.subheader("Comprehensive Case Analysis")
                st.text_area("", value=result, height=600, key="case_analysis_result")
                
                # Download option
                st.download_button(
                    label="Download Analysis Report",
                    data=result,
                    file_name=f"case_analysis_{case_type.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )

def draft_notice_tool(model_id):
    """Draft Notice Tool"""
    st.subheader("📝 Draft Notice")
    
    with st.form("draft_notice_form"):
        notice_type = st.selectbox(
            "Notice Type",
            ["Show Cause Notice", "Information Request", "Warning Notice", "Compliance Notice", "Recovery Notice", "Legal Notice"]
        )
        
        recipient = st.text_input("Recipient Name", placeholder="Customer/Entity name")
        
        case_details = st.text_area(
            "Case Details/Reason",
            placeholder="Describe the case details and reason for the notice",
            height=100
        )
        
        loan_amount = st.number_input("Loan Amount (if applicable)", min_value=0.0, step=1000.0)
        
        action_required = st.text_input("Action Required", placeholder="Specify what action is required from recipient")
        
        timeline = st.selectbox("Response Timeline", ["7 days", "15 days", "21 days", "30 days", "Other"])
        
        if timeline == "Other":
            custom_timeline = st.text_input("Specify Timeline")
            timeline = custom_timeline if custom_timeline else "15 days"
        
        draft_btn = st.form_submit_button("Generate Professional Notice", use_container_width=True)
        
        if draft_btn and case_details:
            with st.spinner("Generating professional notice..."):
                prompt = f"""
                Draft a professional {notice_type} for a financial institution:
                
                Recipient: {recipient or "Customer"}
                Case Details: {case_details}
                Loan Amount: ₹{loan_amount:,.2f} {"" if loan_amount > 0 else ""}
                Action Required: {action_required}
                Response Timeline: {timeline}
                
                Create a formal, legally compliant notice with:
                1. Proper bank letterhead format
                2. Reference number and date
                3. Clear statement of the issue/violation
                4. Specific action required from recipient
                5. Consequences of non-compliance
                6. Timeline for response ({timeline})
                7. Contact information for queries
                8. Professional signature block
                
                Use formal banking language and ensure legal compliance.
                """
                
                result = query_huggingface_model(model_id, prompt, max_tokens=800)
                
                st.subheader(f"Generated {notice_type}")
                st.text_area("", value=result, height=500, key="draft_notice_result")
                
                # Download option
                st.download_button(
                    label="Download Notice as Text File",
                    data=result,
                    file_name=f"{notice_type.lower().replace(' ', '_')}_{recipient or 'notice'}.txt",
                    mime="text/plain"
                )

def investigation_guide_tool(model_id):
    """Investigation Guide Tool"""
    st.subheader("🔍 Investigation Guide")
    
    with st.form("investigation_guide_form"):
        investigation_type = st.selectbox(
            "Investigation Type",
            ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Other"]
        )
        
        current_stage = st.selectbox(
            "Current Stage",
            ["Initial Assessment", "Evidence Collection", "Analysis", "Report Preparation", "Closure"]
        )
        
        specific_challenge = st.text_area(
            "Specific Challenge",
            placeholder="Describe any specific challenges or questions",
            height=100
        )
        
        guide_btn = st.form_submit_button("Get Guidance", use_container_width=True)
        
        if guide_btn:
            with st.spinner("Generating guidance..."):
                prompt = f"""
                Provide investigation guidance for:
                
                Type: {investigation_type}
                Current Stage: {current_stage}
                Challenge: {specific_challenge}
                
                Include:
                1. Best practices for this stage
                2. Key evidence to collect
                3. Common pitfalls to avoid
                4. Next steps
                5. Documentation requirements
                
                Focus on practical, actionable advice.
                """
                
                result = query_huggingface_model(model_id, prompt, max_tokens=700)
                
                st.subheader("Investigation Guidance")
                st.text_area("", value=result, height=400, key="investigation_guide_result")

def free_chat_assistant(model_id):
    """Free Chat Assistant"""
    st.subheader("💬 Free AI Chat Assistant")
    st.markdown("Ask questions about investigations, compliance, or case management.")
    
    # Initialize chat history
    if "free_chat_messages" not in st.session_state:
        st.session_state.free_chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your free AI assistant. I can help with investigation questions, case guidance, and general compliance matters. How can I assist you?"}
        ]
    
    # Display chat history
    for message in st.session_state.free_chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your question..."):
        # Add user message
        st.session_state.free_chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    context_prompt = f"""
                    You are a helpful assistant for fraud investigation and compliance matters.
                    Provide clear, practical advice for this question: {prompt}
                    
                    Keep responses helpful, professional, and concise.
                    """
                    
                    ai_response = query_huggingface_model(model_id, context_prompt, max_tokens=400)
                    st.write(ai_response)
                    
                    # Add AI response to chat history
                    st.session_state.free_chat_messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.free_chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.free_chat_messages = [
            {"role": "assistant", "content": "Chat cleared. How can I assist you today?"}
        ]
        st.rerun()