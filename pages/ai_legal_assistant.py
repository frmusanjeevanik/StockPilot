import streamlit as st
from openai import OpenAI
import os
from auth import require_role

# Configure OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@require_role(["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Admin"])
def show():
    """AI Legal Assistant page for fraud investigation and legal document generation"""
    st.title("🤖 AI Legal Assistant")
    st.markdown("**Expert legal assistant for fraud investigation and document generation**")
    
    # Quick Action Buttons
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Show Cause Notice", use_container_width=True):
            st.session_state.ai_template = "show_cause"
    
    with col2:
        if st.button("📄 Reasoned Order", use_container_width=True):
            st.session_state.ai_template = "reasoned_order"
    
    with col3:
        if st.button("📝 Investigation Report", use_container_width=True):
            st.session_state.ai_template = "investigation_report"
    
    with col4:
        if st.button("💬 Chat Assistant", use_container_width=True):
            st.session_state.ai_template = "chat"
    
    st.divider()
    
    # Template-based interface
    if "ai_template" in st.session_state:
        template = st.session_state.ai_template
        
        if template == "show_cause":
            generate_show_cause_notice()
        elif template == "reasoned_order":
            generate_reasoned_order()
        elif template == "investigation_report":
            generate_investigation_report()
        elif template == "chat":
            chat_assistant()
    else:
        # Default view with examples
        st.subheader("How to Use AI Legal Assistant")
        
        st.markdown("""
        **Available Features:**
        
        1. **Show Cause Notice**: Generate professional show cause notices based on investigation findings
        2. **Reasoned Order**: Convert investigation summaries into formal reasoned orders
        3. **Investigation Report**: Create comprehensive investigation reports
        4. **Chat Assistant**: Interactive guidance for legal and investigation matters
        
        **Example Prompts:**
        - "Draft a Show Cause Notice based on this: customer submitted forged bank statement..."
        - "Convert this investigation finding into a Reasoned Order: customer failed to respond to multiple notices..."
        - "Suggest how to respond to customer claiming duplicate rejection"
        - "Help me identify what kind of investigation this is based on these findings..."
        """)

def generate_show_cause_notice():
    """Generate Show Cause Notice"""
    st.subheader("📋 Generate Show Cause Notice")
    
    with st.form("show_cause_form"):
        # Input fields
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        loan_account = st.text_input("Loan Account Number", placeholder="Enter LAN")
        violation_details = st.text_area(
            "Violation Details", 
            placeholder="Describe the violation/fraud discovered (e.g., forged documents, false information, etc.)",
            height=120
        )
        investigation_findings = st.text_area(
            "Key Investigation Findings",
            placeholder="Summarize the key findings from investigation",
            height=100
        )
        
        generate_btn = st.form_submit_button("Generate Show Cause Notice", use_container_width=True)
        
        if generate_btn and violation_details:
            with st.spinner("Generating show cause notice..."):
                try:
                    prompt = f"""
                    You are an expert legal assistant for a financial institution's fraud investigation team. 
                    Generate a professional Show Cause Notice with the following details:
                    
                    Customer Name: {customer_name or '[Customer Name]'}
                    Loan Account: {loan_account or '[Loan Account Number]'}
                    Violation: {violation_details}
                    Investigation Findings: {investigation_findings}
                    
                    The notice should:
                    1. Be formal and legally compliant
                    2. Clearly state the violation and consequences
                    3. Provide response timeline (typically 15-30 days)
                    4. Include next steps if no response
                    5. Follow standard banking/financial institution format
                    
                    Format as a complete formal document.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1500,
                        temperature=0.3
                    )
                    
                    result = response.choices[0].message.content
                    
                    st.subheader("Generated Show Cause Notice")
                    st.text_area("", value=result, height=400, key="show_cause_result")
                    
                    # Download option
                    st.download_button(
                        label="Download as Text File",
                        data=result or "",
                        file_name=f"show_cause_notice_{customer_name or 'customer'}_{loan_account or 'loan'}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating notice: {str(e)}")

def generate_reasoned_order():
    """Generate Reasoned Order"""
    st.subheader("📄 Generate Reasoned Order")
    
    with st.form("reasoned_order_form"):
        case_details = st.text_area(
            "Case Background",
            placeholder="Provide case background and context",
            height=100
        )
        investigation_summary = st.text_area(
            "Investigation Summary", 
            placeholder="Summarize the complete investigation findings and evidence",
            height=150
        )
        legal_basis = st.text_area(
            "Legal/Policy Basis",
            placeholder="Mention relevant laws, regulations, or internal policies",
            height=80
        )
        decision = st.selectbox(
            "Decision", 
            ["Account Closure", "Penalty Imposition", "Legal Action", "Warning", "Other"]
        )
        
        generate_btn = st.form_submit_button("Generate Reasoned Order", use_container_width=True)
        
        if generate_btn and investigation_summary:
            with st.spinner("Generating reasoned order..."):
                try:
                    prompt = f"""
                    You are an expert legal officer in a financial institution. Generate a comprehensive Reasoned Order based on:
                    
                    Case Background: {case_details}
                    Investigation Summary: {investigation_summary}
                    Legal Basis: {legal_basis}
                    Decision: {decision}
                    
                    The reasoned order should include:
                    1. Case reference and parties involved
                    2. Factual background
                    3. Investigation findings with evidence
                    4. Legal analysis and applicable provisions
                    5. Reasoning for the decision
                    6. Final order/direction
                    7. Appeal/review process if applicable
                    
                    Use formal legal language and structure typical of financial institution orders.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    
                    result = response.choices[0].message.content
                    
                    st.subheader("Generated Reasoned Order")
                    st.text_area("", value=result, height=500, key="reasoned_order_result")
                    
                    st.download_button(
                        label="Download as Text File",
                        data=result or "",
                        file_name=f"reasoned_order_{decision.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating order: {str(e)}")

def generate_investigation_report():
    """Generate Investigation Report"""
    st.subheader("📝 Generate Investigation Report")
    
    with st.form("investigation_report_form"):
        case_id = st.text_input("Case ID", placeholder="Enter case ID")
        allegation = st.text_area(
            "Allegation/Complaint",
            placeholder="Describe the initial allegation or complaint",
            height=100
        )
        investigation_steps = st.text_area(
            "Investigation Steps Taken",
            placeholder="List all investigation activities performed",
            height=120
        )
        evidence_found = st.text_area(
            "Evidence and Findings",
            placeholder="Detail all evidence collected and key findings",
            height=120
        )
        conclusion = st.text_area(
            "Investigation Conclusion",
            placeholder="Summarize the final conclusion",
            height=80
        )
        
        generate_btn = st.form_submit_button("Generate Investigation Report", use_container_width=True)
        
        if generate_btn and allegation and evidence_found:
            with st.spinner("Generating investigation report..."):
                try:
                    prompt = f"""
                    You are a senior investigation officer in a financial institution. Create a comprehensive investigation report:
                    
                    Case ID: {case_id or '[Case ID]'}
                    Allegation: {allegation}
                    Investigation Steps: {investigation_steps}
                    Evidence & Findings: {evidence_found}
                    Conclusion: {conclusion}
                    
                    Structure the report with:
                    1. Executive Summary
                    2. Case Details and Allegation
                    3. Investigation Methodology
                    4. Detailed Findings with Evidence
                    5. Analysis and Assessment
                    6. Conclusions and Recommendations
                    7. Next Steps/Action Required
                    
                    Use professional investigation report format with clear sections and objective language.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2500,
                        temperature=0.3
                    )
                    
                    result = response.choices[0].message.content
                    
                    st.subheader("Generated Investigation Report")
                    st.text_area("", value=result, height=600, key="investigation_report_result")
                    
                    st.download_button(
                        label="Download as Text File",
                        data=result or "",
                        file_name=f"investigation_report_{case_id or 'case'}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

def chat_assistant():
    """Interactive Chat Assistant"""
    st.subheader("💬 AI Legal Assistant Chat")
    st.markdown("Ask questions about legal procedures, investigation guidance, or document drafting.")
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your AI Legal Assistant. I can help with:\n\n• Legal document drafting\n• Investigation guidance\n• Fraud detection advice\n• Regulatory compliance\n• Case analysis\n\nHow can I assist you today?"}
        ]
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your legal/investigation question..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    system_prompt = """
                    You are an expert legal assistant and fraud investigation officer for a financial institution. 
                    Provide clear, professional, and actionable guidance on:
                    
                    1. Legal document drafting (notices, orders, reports)
                    2. Investigation procedures and best practices
                    3. Fraud detection and prevention
                    4. Regulatory compliance matters
                    5. Case analysis and evidence evaluation
                    
                    Always provide practical, legally sound advice suitable for banking/financial sector.
                    Be concise but comprehensive in your responses.
                    """
                    
                    messages = [{"role": "system", "content": system_prompt}]
                    for msg in st.session_state.chat_messages[-5:]:  # Last 5 messages for context
                        messages.append(msg)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.4
                    )
                    
                    ai_response = response.choices[0].message.content or ""
                    st.write(ai_response)
                    
                    # Add AI response to chat history
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat cleared. How can I assist you today?"}
        ]
        st.rerun()