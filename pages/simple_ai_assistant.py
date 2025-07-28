import streamlit as st
from auth import require_role

@require_role(["Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Admin"])
def show():
    """Simple AI Assistant using predefined templates"""
    st.title("🤖 AI Assistant")
    st.markdown("**Template-based assistant for case analysis and document drafting**")
    
    # Quick Action Buttons
    st.subheader("Available Tools")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Case Analysis Templates", use_container_width=True):
            st.session_state.ai_tool = "case_analysis"
    
    with col2:
        if st.button("📝 Document Templates", use_container_width=True):
            st.session_state.ai_tool = "document_templates"
    
    with col3:
        if st.button("🔍 Investigation Guidelines", use_container_width=True):
            st.session_state.ai_tool = "investigation_guide"
    
    st.divider()
    
    # Show selected tool
    if "ai_tool" in st.session_state:
        tool = st.session_state.ai_tool
        
        if tool == "case_analysis":
            show_case_analysis_templates()
        elif tool == "document_templates":
            show_document_templates()
        elif tool == "investigation_guide":
            show_investigation_guidelines()
    else:
        # Default view
        st.subheader("Template-Based AI Assistant")
        st.markdown("""
        **Available Tools:**
        
        1. **Case Analysis Templates**: Pre-built analysis frameworks for different case types
        2. **Document Templates**: Professional templates for notices, reports, and communications
        3. **Investigation Guidelines**: Step-by-step investigation procedures and checklists
        
        **Note**: This assistant uses predefined professional templates - no external API required.
        """)

def show_case_analysis_templates():
    """Show case analysis templates"""
    st.subheader("📋 Case Analysis Templates")
    
    case_type = st.selectbox(
        "Select Case Type",
        ["Document Fraud", "Identity Fraud", "Financial Fraud", "Compliance Violation", "Operational Risk"]
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

def show_document_templates():
    """Show document templates"""
    st.subheader("📝 Document Templates")
    
    doc_type = st.selectbox(
        "Select Document Type",
        ["Show Cause Notice", "Investigation Report", "Legal Notice", "Recovery Notice", "Compliance Report"]
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

def show_investigation_guidelines():
    """Show investigation guidelines"""
    st.subheader("🔍 Investigation Guidelines")
    
    guideline_type = st.selectbox(
        "Select Guideline Type",
        ["Document Fraud Investigation", "Field Investigation", "Digital Evidence", "Interview Process", "Evidence Preservation"]
    )
    
    guidelines = {
        "Document Fraud Investigation": """
DOCUMENT FRAUD INVESTIGATION GUIDELINES

1. INITIAL ASSESSMENT
   □ Obtain original documents
   □ Identify type of fraud suspected
   □ Assess urgency and risk level
   □ Assign investigation team

2. DOCUMENT EXAMINATION
   □ Physical inspection for alterations
   □ Check paper quality and watermarks
   □ Verify security features
   □ Look for digital manipulation signs
   □ Compare with known genuine samples

3. TECHNICAL ANALYSIS
   □ UV light examination
   □ Magnification analysis
   □ Digital forensics if applicable
   □ Handwriting analysis
   □ Ink analysis

4. VERIFICATION PROCESS
   □ Contact issuing authority
   □ Cross-check with databases
   □ Verify with third parties
   □ Check sequential numbering
   □ Validate dates and timelines

5. EVIDENCE COLLECTION
   □ Photograph all documents
   □ Maintain chain of custody
   □ Preserve original condition
   □ Document all findings
   □ Secure expert opinions

6. REPORTING
   □ Prepare detailed findings
   □ Include photographic evidence
   □ Provide expert opinions
   □ Recommend actions
   □ Submit to legal team
        """,
        
        "Field Investigation": """
FIELD INVESTIGATION GUIDELINES

1. PRE-INVESTIGATION PLANNING
   □ Review case details thoroughly
   □ Prepare investigation checklist
   □ Gather contact information
   □ Plan route and schedule
   □ Carry identification documents

2. RESIDENTIAL VERIFICATION
   □ Verify physical address
   □ Check name plate/house number
   □ Interview neighbors
   □ Assess living standards
   □ Take photographs
   □ Verify utilities connection

3. EMPLOYMENT VERIFICATION
   □ Visit registered office
   □ Meet HR/Admin personnel
   □ Verify employment details
   □ Check salary structure
   □ Confirm designation
   □ Assess business authenticity

4. BUSINESS VERIFICATION
   □ Check business premises
   □ Verify registration documents
   □ Interview business associates
   □ Assess business operations
   □ Check financial health
   □ Verify GST registration

5. INTERVIEW TECHNIQUES
   □ Be professional and courteous
   □ Ask open-ended questions
   □ Verify facts consistently
   □ Note behavioral patterns
   □ Record responses accurately
   □ Maintain confidentiality

6. DOCUMENTATION
   □ Complete investigation report
   □ Include photographic evidence
   □ Attach supporting documents
   □ Note GPS coordinates
   □ Record time and date
   □ Get verification signatures
        """,
        
        "Digital Evidence": """
DIGITAL EVIDENCE GUIDELINES

1. DIGITAL DOCUMENT ANALYSIS
   □ Check metadata properties
   □ Verify creation/modification dates
   □ Look for digital signatures
   □ Analyze file compression
   □ Check for layers in PDFs

2. IMAGE FORENSICS
   □ Examine EXIF data
   □ Look for digital manipulation
   □ Check consistency in lighting
   □ Verify shadows and reflections
   □ Use reverse image search

3. EMAIL INVESTIGATION
   □ Verify sender authentication
   □ Check email headers
   □ Trace IP addresses
   □ Verify timestamps
   □ Check for spoofing

4. DATABASE VERIFICATION
   □ Cross-check with internal systems
   □ Verify with external databases
   □ Check data consistency
   □ Look for duplicate entries
   □ Verify data sources

5. EVIDENCE PRESERVATION
   □ Create forensic copies
   □ Maintain hash values
   □ Document chain of custody
   □ Store in secure environment
   □ Backup evidence properly

6. EXPERT CONSULTATION
   □ Engage certified experts
   □ Get technical opinions
   □ Obtain court-admissible reports
   □ Understand limitations
   □ Document expert credentials
        """,
        
        "Interview Process": """
INTERVIEW PROCESS GUIDELINES

1. PREPARATION
   □ Review case background
   □ Prepare question list
   □ Arrange suitable venue
   □ Inform about rights
   □ Have witness present

2. INTERVIEW STRUCTURE
   □ Introduction and purpose
   □ Obtain consent for recording
   □ Start with open questions
   □ Move to specific details
   □ Clarify inconsistencies
   □ Summarize key points

3. QUESTIONING TECHNIQUES
   □ Use neutral language
   □ Avoid leading questions
   □ Allow complete answers
   □ Follow up on responses
   □ Challenge inconsistencies politely
   □ Note non-verbal cues

4. DOCUMENTATION
   □ Record interview accurately
   □ Note time and participants
   □ Include verbatim responses
   □ Document refusals to answer
   □ Get interview acknowledged
   □ Maintain confidentiality

5. LEGAL CONSIDERATIONS
   □ Inform about rights
   □ Avoid coercion
   □ Allow legal representation
   □ Respect privacy
   □ Follow company policies
   □ Consider criminal implications

6. POST-INTERVIEW
   □ Review and verify notes
   □ Identify follow-up actions
   □ Share relevant information
   □ Maintain evidence security
   □ Plan additional interviews
   □ Update investigation status
        """,
        
        "Evidence Preservation": """
EVIDENCE PRESERVATION GUIDELINES

1. INITIAL HANDLING
   □ Document original condition
   □ Photograph before handling
   □ Use gloves when necessary
   □ Avoid contamination
   □ Label immediately
   □ Record date and time

2. CHAIN OF CUSTODY
   □ Maintain detailed log
   □ Record all handlers
   □ Note transfer reasons
   □ Get acknowledgments
   □ Track location changes
   □ Document access times

3. PHYSICAL EVIDENCE
   □ Store in appropriate conditions
   □ Protect from damage
   □ Maintain temperature control
   □ Prevent unauthorized access
   □ Use proper containers
   □ Label clearly

4. DIGITAL EVIDENCE
   □ Create backup copies
   □ Use write-protection
   □ Calculate hash values
   □ Store on secure media
   □ Maintain access logs
   □ Document software used

5. DOCUMENTATION
   □ Complete evidence forms
   □ Photograph all evidence
   □ Note condition changes
   □ Record examination results
   □ Maintain inventory
   □ Update status regularly

6. LEGAL REQUIREMENTS
   □ Follow court procedures
   □ Maintain admissibility
   □ Respect privacy laws
   □ Follow retention policies
   □ Prepare for testimony
   □ Coordinate with legal team
        """
    }
    
    if guideline_type in guidelines:
        st.subheader(f"{guideline_type} Checklist")
        st.text_area("Investigation Guidelines", value=guidelines[guideline_type], height=600)
        
        st.download_button(
            label="Download Guidelines",
            data=guidelines[guideline_type],
            file_name=f"{guideline_type.lower().replace(' ', '_')}_guidelines.txt",
            mime="text/plain"
        )