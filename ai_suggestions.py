"""
AI-powered auto-suggestions for case descriptions and remarks
"""

def get_case_description_suggestions():
    """Get common case description suggestions"""
    return [
        # Document Fraud
        "Customer submitted forged bank statements with altered transaction history",
        "Fake salary certificate provided with inflated income figures",
        "Identity documents appear to be tampered or fabricated",
        "Property documents submitted contain suspicious alterations",
        "Educational certificates provided are not from recognized institutions",
        
        # Financial Fraud
        "Multiple loan applications detected across different branches with same details",
        "Income source verification reveals discrepancies in employment history",
        "Bank account statements show unusual large cash deposits before loan application",
        "Credit history manipulation detected through external agency verification",
        "Guarantor details found to be fictitious upon verification",
        
        # Compliance Violations
        "KYC documents incomplete or not updated as per regulatory requirements",
        "Customer failed to respond to multiple verification requests",
        "Suspicious transaction patterns detected post loan disbursement",
        "Non-compliance with loan utilization terms and conditions",
        "Customer address verification failed - premises not traceable",
        
        # Investigation Findings
        "Field investigation reveals customer business premises non-existent",
        "Reference check confirms false information provided in application",
        "Credit bureau report shows hidden existing loans not declared",
        "Employment verification failed - company denies employee association",
        "Collateral valuation found to be significantly overestimated"
    ]

def get_remarks_suggestions():
    """Get common remarks suggestions for different stages"""
    return {
        "review_stage": [
            "Documents verified and found to be authentic",
            "Requires additional documentation for income verification",
            "Field investigation recommended for address verification",
            "Credit bureau check shows satisfactory credit history",
            "Referred to legal team for opinion on property documents",
            "Case forwarded to approver with positive recommendation",
            "Hold pending receipt of additional supporting documents",
            "Customer response required within 15 days"
        ],
        
        "approval_stage": [
            "Case approved based on satisfactory verification",
            "Rejected due to insufficient income proof",
            "Approved with additional conditions and monitoring",
            "Referred to senior management for final decision",
            "Case closed - customer withdrew application",
            "Approved subject to execution of additional security",
            "Rejected - credit history does not meet standards",
            "Conditional approval pending compliance requirements"
        ],
        
        "legal_stage": [
            "Legal documents reviewed and found in order",
            "Title clearance required before final approval",
            "Property legal verification completed successfully",
            "Stamp duty and registration charges verified",
            "Legal opinion provided - no adverse findings",
            "Additional legal documentation required",
            "Legal clearance provided with conditions",
            "Referred to panel lawyer for detailed verification"
        ],
        
        "closure_stage": [
            "Case closed successfully - no further action required",
            "Loan account regularized as per agreed terms",
            "Recovery proceedings initiated as per policy",
            "Account written off as per board approval",
            "Settlement executed and case closed",
            "Legal action initiated for recovery",
            "Case transferred to specialized recovery unit",
            "Compromise settlement accepted and implemented"
        ]
    }

def get_investigation_keywords():
    """Get keywords for investigation context"""
    return {
        "fraud_indicators": [
            "forged documents", "false information", "identity theft", "income inflation",
            "property fraud", "collateral manipulation", "guarantor fraud", "multiple applications"
        ],
        
        "verification_methods": [
            "field investigation", "telephonic verification", "employment check", "address verification",
            "credit bureau check", "income verification", "bank statement analysis", "reference check"
        ],
        
        "outcomes": [
            "case approved", "application rejected", "additional documentation required",
            "legal action initiated", "account closure", "recovery proceedings", "settlement reached"
        ]
    }

def suggest_next_action(case_type, current_status):
    """Suggest next action based on case type and status"""
    suggestions = {
        ("Document Fraud", "Submitted"): "Initiate detailed document verification and forensic analysis",
        ("Document Fraud", "Under Review"): "Complete technical examination of suspected documents",
        ("Identity Fraud", "Submitted"): "Conduct thorough identity verification and background check",
        ("Financial Fraud", "Under Review"): "Analyze financial statements and conduct income verification",
        ("Compliance Violation", "Submitted"): "Review compliance checklist and regulatory requirements",
        ("Operational Risk", "Under Review"): "Assess risk impact and recommend mitigation measures"
    }
    
    return suggestions.get((case_type, current_status), "Proceed with standard investigation protocol")

def get_risk_assessment_template(risk_level):
    """Get risk assessment template based on risk level"""
    templates = {
        "High": """
        HIGH RISK CASE ASSESSMENT:
        - Immediate escalation required
        - Enhanced due diligence recommended
        - Senior management notification necessary
        - Consider external expert consultation
        - Implement additional monitoring controls
        """,
        
        "Medium": """
        MEDIUM RISK CASE ASSESSMENT:
        - Standard verification procedures applicable
        - Additional documentation may be required
        - Regular monitoring recommended
        - Periodic review scheduled
        - Escalation if risk factors increase
        """,
        
        "Low": """
        LOW RISK CASE ASSESSMENT:
        - Standard processing procedures
        - Routine verification sufficient
        - Normal monitoring applicable
        - Regular review cycle
        - Standard approval process
        """
    }
    
    return templates.get(risk_level, "Standard risk assessment required")