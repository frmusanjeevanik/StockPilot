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
        **Available AI Tools:**
        
        1. **Smart Case Analysis**: AI-powered analysis of case details with intelligent insights
        2. **AI Document Generator**: Generate professional documents with AI assistance
        3. **AI Chat Assistant**: Interactive chat for investigation guidance and compliance questions
        
        **Note**: Powered by Google Gemini AI for intelligent, context-aware assistance.
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
        return f"Error: {str(e)}"

def show_smart_case_analysis():
    """AI-powered case analysis"""
    st.subheader("📋 Smart Case Analysis")
    
    with st.form("case_analysis_form"):
        case_type = st.selectbox(
            "Case Type",
            ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"]
        )
        
        case_details = st.text_area(
            "Case Details",
            placeholder="Describe the case details, evidence, and specific concerns...",
            height=150
        )
        
        specific_questions = st.text_area(
            "Specific Questions (Optional)",
            placeholder="Any specific questions or areas you want the AI to focus on...",
            height=100
        )
        
        submit_analysis = st.form_submit_button("🔍 Analyze Case", use_container_width=True)
    
    if submit_analysis and case_details:
        with st.spinner("Analyzing case with AI..."):
            prompt = f"""
            You are an expert fraud investigation analyst. Analyze the following case and provide a comprehensive analysis.
            
            Case Type: {case_type}
            Case Details: {case_details}
            Specific Questions: {specific_questions if specific_questions else "None"}
            
            Please provide:
            1. Risk Assessment (High/Medium/Low with reasoning)
            2. Key Red Flags identified
            3. Investigation priorities and next steps
            4. Recommended actions
            5. Potential legal/regulatory implications
            6. Evidence preservation requirements
            
            Format the response professionally with clear sections and actionable recommendations.
            """
            
            analysis = query_gemini(prompt, max_tokens=1500)
            
            st.subheader("AI Case Analysis Report")
            st.text_area("Analysis Report", value=analysis, height=600)
            
            # Download option
            st.download_button(
                label="Download Analysis Report",
                data=analysis,
                file_name=f"{case_type.lower().replace(' ', '_')}_analysis_{st.session_state.get('current_user', {}).get('user_id', 'report')}.txt",
                mime="text/plain"
            )
    
    templates = {
        "Document Fraud": """
**DOCUMENT FRAUD ANALYSIS TEMPLATE**

1. **Document Verification Findings:**
   - Physical examination results: [Original/Forged/Altered]
   - Technical analysis: [Digital manipulation/Physical alteration/Genuine]
   - Verification with issuing authority: [Confirmed/Denied/Pending]

2. **Key Red Flags Identified:**
   - Inconsistent formatting or fonts
   - Altered dates or figures
   - Missing security features
   - Suspicious digital artifacts

3. **Risk Assessment:**
   - Fraud confidence level: [Low/Medium/High/Certain]
   - Financial impact: ₹[Amount]
   - Regulatory implications: [Yes/No]

4. **Recommended Actions:**
   - Immediate: [Stop processing/Freeze account/Request originals]
   - Investigation: [Field verification/Authority confirmation/Expert analysis]
   - Documentation: [Preserve evidence/Take photographs/Secure originals]
   - Reporting: [Internal escalation/Regulatory filing/Legal consultation]

5. **Next Steps:**
   - Timeline for completion: [X days]
   - Responsible team: [Investigation/Legal/Compliance]
   - Required approvals: [Branch Manager/Regional Head/Legal]
        """,
        
        "Identity Fraud": """
**IDENTITY FRAUD ANALYSIS TEMPLATE**

1. **Identity Verification Results:**
   - Photo verification: [Match/No Match/Inconclusive]
   - Biometric comparison: [Positive/Negative/Not Available]
   - Address verification: [Confirmed/Failed/Pending]

2. **Suspicious Indicators:**
   - Multiple applications with same details
   - Inconsistent personal information
   - Unverifiable contact details
   - Suspicious behavioral patterns

3. **Investigation Findings:**
   - Employment verification: [Confirmed/Denied/Pending]
   - Reference checks: [Positive/Negative/Unresponsive]
   - Database cross-checks: [Clean/Red Flags/Inconclusive]

4. **Risk Level Assessment:**
   - Identity confidence: [Verified/Suspicious/Fraudulent]
   - Impact assessment: [Low/Medium/High/Critical]
   - Regulatory risk: [Minimal/Moderate/High]

5. **Action Plan:**
   - Immediate measures: [Account freeze/Transaction monitoring/Alert setup]
   - Investigation steps: [Field visit/Police verification/Database checks]
   - Documentation: [Evidence collection/Statement recording/Photo comparison]
   - Escalation: [Internal committee/Law enforcement/Regulatory bodies]
        """,
        
        "Financial Fraud": """
**FINANCIAL FRAUD ANALYSIS TEMPLATE**

1. **Financial Pattern Analysis:**
   - Income verification: [Verified/Inflated/Fabricated]
   - Bank statement analysis: [Genuine/Manipulated/Suspicious]
   - Transaction patterns: [Normal/Unusual/Fraudulent]

2. **Key Findings:**
   - Income source legitimacy: [Confirmed/Questionable/False]
   - Asset verification: [Verified/Overvalued/Non-existent]
   - Liability disclosure: [Complete/Partial/Concealed]

3. **Red Flag Analysis:**
   - Sudden large deposits before application
   - Circular transactions between accounts
   - Inconsistent financial behavior
   - Undisclosed existing loans

4. **Impact Assessment:**
   - Potential loss: ₹[Amount]
   - Recovery probability: [High/Medium/Low]
   - Systemic risk: [Isolated/Potential spread/High contagion]

5. **Remedial Actions:**
   - Account actions: [Freeze/Monitor/Close]
   - Legal measures: [Notice/Recovery/Criminal complaint]
   - Regulatory reporting: [RBI/CIBIL/FIU]
   - Internal controls: [Process review/System updates/Training]
        """,
        
        "Compliance Violation": """
**COMPLIANCE VIOLATION ANALYSIS TEMPLATE**

1. **Regulatory Assessment:**
   - Violated regulation: [RBI Guidelines/KYC Norms/AML Requirements]
   - Violation severity: [Minor/Major/Critical]
   - Regulatory timeline: [Within limits/Overdue/Significantly delayed]

2. **Compliance Gap Analysis:**
   - Process adherence: [Full/Partial/Non-compliant]
   - Documentation status: [Complete/Incomplete/Missing]
   - Approval matrix: [Followed/Bypassed/Inadequate]

3. **Root Cause Analysis:**
   - System issues: [Technical/Process/Human error]
   - Training gaps: [Staff knowledge/Procedure awareness]
   - Control failures: [Supervision/Monitoring/Reporting]

4. **Regulatory Risk:**
   - Penalty exposure: ₹[Amount]
   - License risk: [None/Warning/Suspension threat]
   - Reputation impact: [Minimal/Moderate/Significant]

5. **Corrective Measures:**
   - Immediate compliance: [Gap closure/Process correction]
   - System improvements: [Controls/Monitoring/Reporting]
   - Training programs: [Staff/Management/Board]
   - Regulatory engagement: [Self-disclosure/Remediation plan]
        """,
        
        "Operational Risk": """
**OPERATIONAL RISK ANALYSIS TEMPLATE**

1. **Risk Event Analysis:**
   - Event category: [Process/People/Systems/External]
   - Occurrence frequency: [One-time/Recurring/Systematic]
   - Detection method: [Internal audit/External/Customer complaint]

2. **Impact Assessment:**
   - Financial loss: ₹[Amount]
   - Operational disruption: [Hours/Days/Weeks]
   - Customer impact: [Number affected/Severity]
   - Reputation risk: [Local/Regional/National]

3. **Control Failure Analysis:**
   - Preventive controls: [Adequate/Inadequate/Bypassed]
   - Detective controls: [Effective/Delayed/Failed]
   - Corrective controls: [Prompt/Delayed/Inadequate]

4. **Business Continuity:**
   - Service availability: [Maintained/Reduced/Disrupted]
   - Recovery time: [Immediate/Hours/Days]
   - Customer communication: [Proactive/Reactive/None]

5. **Risk Mitigation:**
   - Process improvements: [Redesign/Automation/Controls]
   - System enhancements: [Upgrades/Monitoring/Backup]
   - Training requirements: [Technical/Process/Awareness]
   - Monitoring mechanisms: [Real-time/Periodic/Event-driven]
        """
    }
    
    if case_type in templates:
        st.subheader(f"{case_type} Analysis Framework")
        st.text_area("Analysis Template", value=templates[case_type], height=600)
        
        st.download_button(
            label="Download Template",
            data=templates[case_type],
            file_name=f"{case_type.lower().replace(' ', '_')}_analysis_template.txt",
            mime="text/plain"
        )

def show_ai_document_generator():
    """AI-powered document generation"""
    st.subheader("📝 AI Document Generator")
    
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
        
        case_summary = st.text_area(
            "Case Summary/Key Details",
            placeholder="Provide key details about the case, violations, or issues...",
            height=150
        )
        
        specific_requirements = st.text_area(
            "Specific Requirements",
            placeholder="Any specific points to include, tone required, or special instructions...",
            height=100
        )
        
        submit_document = st.form_submit_button("📝 Generate Document", use_container_width=True)
    
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
            
            Generate a complete, ready-to-use document.
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
    
    templates = {
        "Show Cause Notice": """
[BANK LETTERHEAD]

Ref: [Case Number]
Date: [Date]

To,
[Customer Name]
[Customer Address]

Subject: Show Cause Notice - Irregularities in Loan Account [LAN Number]

Dear [Mr./Ms. Customer Name],

This is with reference to your loan account bearing number [LAN] sanctioned on [Date] for an amount of ₹[Amount].

During our routine verification process, we have observed the following irregularities:

1. [Specific irregularity 1]
2. [Specific irregularity 2]
3. [Specific irregularity 3]

The above irregularities constitute a breach of the terms and conditions of the loan agreement dated [Date].

You are hereby required to:
1. Provide written explanation for the above irregularities
2. Submit supporting documents as evidence
3. Appear in person for a meeting with our investigation team

You are required to respond to this notice within 15 days from the date of receipt. Failure to respond or provide satisfactory explanation may result in:
- Immediate recall of the loan amount
- Initiation of legal proceedings
- Reporting to credit bureaus
- Criminal proceedings as per applicable laws

For any clarifications, you may contact the undersigned during business hours.

Yours faithfully,

[Name]
[Designation]
[Contact Details]
        """,
        
        "Investigation Report": """
INVESTIGATION REPORT

Case Details:
- Case ID: [Case ID]
- LAN: [LAN Number]
- Customer: [Customer Name]
- Loan Amount: ₹[Amount]
- Investigation Period: [Start Date] to [End Date]

Executive Summary:
[Brief overview of investigation findings]

Investigation Methodology:
1. Document verification
2. Field investigation
3. Reference checks
4. Database verification
5. Technical analysis

Key Findings:
1. [Finding 1 with supporting evidence]
2. [Finding 2 with supporting evidence]
3. [Finding 3 with supporting evidence]

Evidence Collected:
- [List of documents/evidence]
- [Photographs/recordings]
- [Witness statements]

Risk Assessment:
- Fraud Probability: [Percentage]
- Financial Impact: ₹[Amount]
- Regulatory Implications: [Yes/No]

Recommendations:
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

Conclusion:
[Final conclusion with rationale]

Prepared by: [Investigation Officer]
Date: [Date]
Reviewed by: [Senior Officer]
        """,
        
        "Legal Notice": """
[LAWYER LETTERHEAD]

LEGAL NOTICE

To,
[Customer Name]
[Address]

NOTICE UNDER SECTION 138 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881

Dear Sir/Madam,

I am instructed by my client [Bank Name] to serve upon you this legal notice for the following facts and circumstances:

1. That you availed a loan facility of ₹[Amount] from my client on [Date].

2. That as per the loan agreement, you were required to [specific obligations].

3. That you have committed default/breach by [specific breach details].

4. That despite repeated requests and reminders, you have failed to rectify the default.

5. That your actions constitute [legal violations].

TAKE NOTICE that you are hereby called upon to:
- [Specific demand 1]
- [Specific demand 2]
- [Specific demand 3]

Within 15 days of receipt of this notice, failing which my client shall be constrained to initiate appropriate legal proceedings against you for recovery of the amount along with interest, costs, and damages.

This notice is issued without prejudice to any other rights and remedies available to my client under law.

Yours faithfully,

[Advocate Name]
[Bar Council Registration]
[Date]
        """,
        
        "Recovery Notice": """
[BANK LETTERHEAD]

FINAL DEMAND NOTICE

Ref: [Case Number]
Date: [Date]

To,
[Customer Name]
[Address]

Subject: Final Demand for Recovery - Loan Account [LAN]

Dear [Customer Name],

We refer to our earlier communications regarding your loan account [LAN] which has become irregular/overdue.

Outstanding Details as on [Date]:
- Principal Outstanding: ₹[Amount]
- Interest Accrued: ₹[Amount]
- Penal Interest: ₹[Amount]
- Other Charges: ₹[Amount]
- Total Outstanding: ₹[Total Amount]

Despite our repeated requests, you have failed to regularize your account. This final notice is being issued to demand payment of the total outstanding amount of ₹[Total Amount] within 30 days from the date of this notice.

Please note that:
1. This is the final opportunity to settle the account
2. Legal action will be initiated immediately after the notice period
3. Your name will be reported to credit bureaus
4. Criminal proceedings may be initiated for willful default

You are advised to:
- Contact our recovery department immediately
- Arrange for payment of the outstanding amount
- Provide acceptable reasons for delay if any

For payment arrangements or queries, contact:
[Recovery Officer Name]
[Contact Details]

Yours faithfully,

[Recovery Manager Name]
[Designation]
        """,
        
        "Compliance Report": """
COMPLIANCE INVESTIGATION REPORT

Report Details:
- Report ID: [Report ID]
- Prepared Date: [Date]
- Review Period: [Period]
- Prepared by: [Officer Name]

Compliance Area: [Specific regulation/guideline]

Scope of Review:
[Description of what was reviewed]

Methodology:
1. Document review
2. Process observation
3. Sample testing
4. Interview with staff
5. System analysis

Compliance Status:
✓ Compliant Areas:
- [Area 1]
- [Area 2]

⚠ Areas of Concern:
- [Issue 1] - [Impact Level]
- [Issue 2] - [Impact Level]

✗ Non-Compliant Areas:
- [Violation 1] - [Risk Level]
- [Violation 2] - [Risk Level]

Regulatory Risk Assessment:
- Overall Risk Rating: [High/Medium/Low]
- Potential Penalty: ₹[Amount]
- Timeline for Compliance: [Days]

Recommendations:
1. Immediate Actions:
   - [Action 1]
   - [Action 2]

2. Medium-term Measures:
   - [Measure 1]
   - [Measure 2]

3. Long-term Improvements:
   - [Improvement 1]
   - [Improvement 2]

Management Response:
[To be filled by management]

Follow-up Schedule:
- Review Date: [Date]
- Responsible Person: [Name]

Prepared by: [Compliance Officer]
Reviewed by: [Chief Compliance Officer]
Date: [Date]
        """
    }
    
    if doc_type in templates:
        st.subheader(f"{doc_type} Template")
        st.text_area("Document Template", value=templates[doc_type], height=600)
        
        st.download_button(
            label="Download Template",
            data=templates[doc_type],
            file_name=f"{doc_type.lower().replace(' ', '_')}_template.txt",
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
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI Assistant:** {message['content']}")
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
            
            Keep the response helpful, accurate, and appropriately detailed.
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
