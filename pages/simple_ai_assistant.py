import streamlit as st
import os
from auth import require_role
from google import genai
from google.genai import types

@require_role(["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Investigator", "Admin"])
def show():
    """AI Assistant using Gemini API"""
    st.title("🤖 AI Assistant")
    st.markdown("**Intelligent assistant for case analysis and document drafting powered by Gemini AI**")
    
    # Initialize Gemini client
    if not hasattr(st.session_state, 'gemini_client'):
        try:
            os.environ['GEMINI_API_KEY'] = 'AIzaSyAZCvpTcGq-ie_3Vnh2obVaAzrFTnFnDqc'
            st.session_state.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            st.success("✅ AI Assistant ready with Gemini intelligence")
        except Exception as e:
            st.error(f"❌ Error initializing AI: {str(e)}")
            return
    
    # Quick Action Buttons
    st.subheader("Available Tools")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Smart Case Analysis", use_container_width=True):
            st.session_state.ai_tool = "smart_case_analysis"
    
    with col2:
        if st.button("📝 AI Document Generator", use_container_width=True):
            st.session_state.ai_tool = "ai_document_generator"
    
    with col3:
        if st.button("💬 AI Chat Assistant", use_container_width=True):
            st.session_state.ai_tool = "ai_chat"
    
    st.divider()
    
    # Show selected tool
    if "ai_tool" in st.session_state:
        tool = st.session_state.ai_tool
        
        if tool == "smart_case_analysis":
            show_smart_case_analysis()
        elif tool == "ai_document_generator":
            show_ai_document_generator()
        elif tool == "ai_chat":
            show_ai_chat_assistant()
    else:
        # Default view
        st.subheader("Gemini-Powered AI Assistant")
        st.markdown("""
        Available AI Tools:
        
        1. Smart Case Analysis: AI-powered analysis of case details with intelligent insights
        2. AI Document Generator: Generate professional documents with AI assistance
        3. AI Chat Assistant: Interactive chat for investigation guidance and compliance questions
        
        Note: Powered by Google Gemini AI for intelligent, context-aware assistance.
        """)

def query_gemini(prompt, max_tokens=1000):
    """Query Gemini API for intelligent responses"""
    try:
        client = st.session_state.gemini_client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.3
            )
        )
        return response.text if response.text else "Unable to generate response"
    except Exception as e:
        return f"Error generating response: {str(e)}"

def show_smart_case_analysis():
    """Smart case analysis with AI insights"""
    st.subheader("📋 Smart Case Analysis")
    
    with st.form("case_analysis_form"):
        case_type = st.selectbox(
            "Case Type", 
            ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            case_id = st.text_input("Case ID")
            loan_amount = st.text_input("Loan Amount")
        with col2:
            customer_name = st.text_input("Customer Name")
            branch = st.text_input("Branch/Location")
        
        case_details = st.text_area(
            "Case Details",
            placeholder="Provide detailed information about the case, irregularities, evidence, etc.",
            height=150
        )
        
        analyze_case = st.form_submit_button("🔍 Analyze Case", use_container_width=True)
    
    if analyze_case and case_details:
        with st.spinner("Analyzing case with AI..."):
            analysis_prompt = f"""
            You are an expert fraud investigation analyst. Analyze the following case and provide comprehensive insights:
            
            Case Type: {case_type}
            Case ID: {case_id}
            Customer: {customer_name}
            Loan Amount: {loan_amount}
            Branch: {branch}
            Case Details: {case_details}
            
            Provide analysis in the following format (without bold formatting):
            
            1. CASE OVERVIEW
            Summarize the case in professional terms
            
            2. RISK ASSESSMENT
            - Risk Level: [High/Medium/Low]
            - Fraud Probability: [Percentage]
            - Financial Impact: Amount at risk
            
            3. KEY RED FLAGS
            List specific indicators of fraud or irregularities
            
            4. INVESTIGATION PRIORITIES
            Prioritized list of investigation steps
            
            5. REGULATORY IMPLICATIONS
            Compliance considerations and reporting requirements
            
            6. RECOMMENDED ACTIONS
            Immediate and long-term action items
            
            7. EVIDENCE PRESERVATION
            Critical evidence to secure and preserve
            
            Use professional language suitable for banking compliance and investigation reports.
            """
            
            analysis = query_gemini(analysis_prompt, max_tokens=1500)
            
            st.subheader("AI Case Analysis Report")
            st.text_area("Analysis Report", value=analysis, height=800)
            
            # Download option
            st.download_button(
                label="Download Analysis Report",
                data=analysis,
                file_name=f"case_analysis_{case_id}_{case_type.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )

def show_ai_document_generator():
    """AI-powered document generation"""
    st.subheader("📝 AI Document Generator")
    
    # Add informational note about case description enhancement
    st.info("💡 Use AI to improve your case description: Type your summary in the box. Click the small button on the bottom-right that says 'Enhance Description' to auto-generate or improve it using AI.")
    
    with st.form("document_generator_form"):
        doc_type = st.selectbox(
            "Document Type",
            ["Show Cause Notice", "Investigation Report", "Legal Notice", "Recovery Notice", "Compliance Report", "Email Communication", "Internal Memo"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            recipient_name = st.text_input("Recipient Name")
            case_id = st.text_input("Case ID/LAN")
        with col2:
            loan_amount = st.text_input("Loan Amount (if applicable)")
            branch_location = st.text_input("Branch/Location")
        
        # Case summary with enhancement option
        col1, col2 = st.columns([4, 1])
        with col1:
            case_summary = st.text_area(
                "Case Summary/Key Details",
                placeholder="Provide key details about the case, violations, or issues...",
                height=150,
                key="case_summary_input"
            )
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            enhance_desc = st.form_submit_button("✨ Enhance Description", help="Use AI to improve case description")
        
        # Show enhanced description if available
        if "enhanced_case_summary" in st.session_state:
            case_summary = st.text_area(
                "Enhanced Case Summary",
                value=st.session_state.enhanced_case_summary,
                height=150,
                key="enhanced_summary_display"
            )
        
        specific_requirements = st.text_area(
            "Specific Requirements",
            placeholder="Any specific points to include, tone required, or special instructions...",
            height=100
        )
        
        submit_document = st.form_submit_button("📝 Generate Document", use_container_width=True)
    
    # Handle description enhancement
    if enhance_desc and st.session_state.get("case_summary_input"):
        with st.spinner("Enhancing description with AI..."):
            enhanced_prompt = f"""
            Please enhance and improve the following case description for a fraud investigation report. 
            Make it more professional, detailed, and comprehensive while maintaining accuracy:
            
            Original description: {st.session_state.case_summary_input}
            
            Please provide an enhanced version that:
            1. Uses professional fraud investigation terminology
            2. Structures information clearly
            3. Highlights key risk factors
            4. Maintains factual accuracy
            5. Follows banking industry standards
            
            Do not use any bold formatting with asterisks in the output.
            """
            
            enhanced_description = query_gemini(enhanced_prompt, max_tokens=800)
            st.session_state.enhanced_case_summary = enhanced_description
            st.rerun()
    
    if submit_document and recipient_name and case_summary:
        with st.spinner("Generating document with AI..."):
            prompt = f"""
            You are a professional legal document writer for a financial institution. Generate a {doc_type} with the following details:
            
            Recipient: {recipient_name}
            Case ID/LAN: {case_id}
            Loan Amount: {loan_amount}
            Branch: {branch_location}
            Case Summary: {case_summary}
            Special Requirements: {specific_requirements if specific_requirements else "Standard format"}
            
            Requirements:
            1. Use professional, formal language appropriate for banking/legal context
            2. Include proper letterhead format (placeholder for bank details)
            3. Follow legal and regulatory compliance standards
            4. Include all necessary legal disclaimers and rights
            5. Structure with clear sections and professional formatting
            6. Include proper contact information and next steps
            7. Use appropriate tone - firm but professional
            8. Do not use any bold formatting with asterisks in the output
            
            Generate a complete, ready-to-use document with clean formatting.
            """
            
            document = query_gemini(prompt, max_tokens=2000)
            
            st.subheader(f"Generated {doc_type}")
            st.text_area("Generated Document", value=document, height=600)
            
            # Download option
            st.download_button(
                label="Download Document",
                data=document,
                file_name=f"{doc_type.lower().replace(' ', '_')}_{recipient_name.replace(' ', '_')}_{case_id}.txt",
                mime="text/plain"
            )

def show_ai_chat_assistant():
    """Interactive AI chat assistant"""
    st.subheader("💬 AI Chat Assistant")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"You: {message['content']}")
            else:
                st.markdown(f"AI Assistant: {message['content']}")
            st.divider()
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_area(
            "Ask your question:",
            placeholder="Ask about investigation procedures, compliance requirements, legal guidance, case analysis, or any other assistance you need...",
            height=100,
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit_chat = st.form_submit_button("💬 Send", use_container_width=True)
        with col2:
            if st.form_submit_button("🔄 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with col3:
            if st.form_submit_button("📋 Quick Help", use_container_width=True):
                user_question = "What are the key steps for investigating a suspected fraud case?"
                submit_chat = True
    
    if submit_chat and user_question:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with st.spinner("AI is thinking..."):
            # Create context from chat history
            chat_context = ""
            if len(st.session_state.chat_history) > 1:
                recent_context = st.session_state.chat_history[-3:]  # Last 3 messages
                chat_context = "Previous conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_context])
            
            prompt = f"""
            You are an expert fraud investigation and compliance assistant for a financial institution. Provide helpful, accurate, and professional guidance.
            
            {chat_context}
            
            Current question: {user_question}
            
            Provide a comprehensive, professional response that includes:
            1. Direct answer to the question
            2. Relevant procedures or guidelines
            3. Best practices
            4. Any legal/regulatory considerations
            5. Practical next steps if applicable
            
            Keep the response helpful, accurate, and appropriately detailed. Do not use bold formatting with asterisks.
            """
            
            ai_response = query_gemini(prompt, max_tokens=1200)
            
            # Add AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Refresh to show new messages
            st.rerun()
    
    # Quick action buttons
    st.subheader("Quick Questions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Document Verification Steps", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "What are the standard steps for document verification in fraud cases?"
            })
            st.rerun()
        
        if st.button("📋 Legal Notice Guidelines", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "What should be included in a legal notice for loan default?"
            })
            st.rerun()
    
    with col2:
        if st.button("⚖️ Compliance Requirements", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "What are the key compliance requirements for fraud investigation?"
            })
            st.rerun()
        
        if st.button("🎯 Evidence Collection", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user", 
                "content": "How should evidence be collected and preserved in fraud cases?"
            })
            st.rerun()
    
    # Hidden label at the bottom left
    st.markdown("""
    <div style='position: fixed; bottom: 5px; left: 5px; font-size: 1px; color: #F2F0F6; z-index: 1000;'>
    app admin panel analytics approver panel case entry closure panel dashboard legal panel reviewer panel simple ai assistant user management
    </div>
    """, unsafe_allow_html=True)
    
    # Footer credit at the bottom center
    st.markdown("""
    <div style='position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); color: #C7222A; font-size: 12px; font-weight: 500; text-align: center; z-index: 1000;'>
    Powered by Fraud Risk Management Unit
    </div>
    """, unsafe_allow_html=True)