import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Legal Reviewer", "Admin"])
def show():
    """Display legal reviewer panel"""
    st.title("⚖️ Legal Review Panel")
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Legal Review", "📄 SCN/Orders", "✅ Completed"])
    
    with tab1:
        st.subheader("Cases Requiring Legal Review")
        legal_cases = get_cases_by_status("Legal Review")
        
        if legal_cases:
            for case in legal_cases:
                with st.expander(f"Case: {case['case_id']} - {case['product']} ({case['region']})"):
                    show_legal_case_details(case, current_user)
        else:
            st.info("📭 No cases pending legal review")
    
    with tab2:
        st.subheader("Show Cause Notices & Orders")
        show_scn_orders_section()
    
    with tab3:
        st.subheader("Completed Legal Reviews")
        # Cases that were in legal review and are now closed or moved to other status
        st.info("Completed legal reviews will appear here")

def show_legal_case_details(case, current_user):
    """Display case details for legal review"""
    
    # Basic case information
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Case ID:** {case['case_id']}")
        st.write(f"**LAN:** {case['lan']}")
        st.write(f"**Type:** {case['case_type']}")
        st.write(f"**Product:** {case['product']}")
        st.write(f"**Region:** {case['region']}")
    
    with col2:
        st.write(f"**Status:** {get_status_color(case['status'])} {case['status']}")
        st.write(f"**Referred By:** {case['referred_by']}")
        st.write(f"**Case Date:** {case['case_date']}")
        st.write(f"**Created By:** {case['created_by']}")
        st.write(f"**Reviewed By:** {case['reviewed_by'] or 'N/A'}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Review history
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Review History:**")
        for comment in comments:
            st.write(f"**{comment['created_by']}** ({format_datetime(comment['created_at'])}) - *{comment['comment_type']}*")
            st.write(comment['comment'])
            st.divider()
    
    # Documents
    documents = get_case_documents(case['case_id'])
    if documents:
        st.write("**Supporting Documents:**")
        for doc in documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📎 {doc['original_filename']}")
            with col2:
                st.write(format_file_size(doc['file_size']))
            with col3:
                st.write(format_datetime(doc['uploaded_at']))
    
    # Legal review actions
    st.write("**Legal Review Actions:**")
    
    # Legal comments with AI suggestions
    st.markdown("**Legal Review Comments**")
    col_leg1, col_leg2 = st.columns([3, 1])
    with col_leg2:
        if st.button("💡 Quick Remarks", key=f"legal_sugg_{case['case_id']}"):
            from ai_suggestions import get_remarks_suggestions
            suggestions = get_remarks_suggestions()["legal_stage"]
            st.session_state[f"legal_suggestions_{case['case_id']}"] = suggestions
    
    # Show suggestions
    if f"legal_suggestions_{case['case_id']}" in st.session_state:
        st.markdown("**Quick Remarks:**")
        legal_cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state[f"legal_suggestions_{case['case_id']}"][:4]):
            col_idx = i % 2
            with legal_cols[col_idx]:
                if st.button(f"📝 {suggestion[:30]}...", key=f"leg_sugg_{case['case_id']}_{i}", help=suggestion):
                    st.session_state[f"selected_legal_{case['case_id']}"] = suggestion
                    st.rerun()
    
    initial_legal = st.session_state.get(f"selected_legal_{case['case_id']}", "")
    legal_comment = st.text_area(
        "",
        value=initial_legal,
        key=f"legal_comment_{case['case_id']}",
        placeholder="Enter legal analysis and recommendations or use quick remarks above...",
        height=80
    )
    
    # Legal action type
    legal_action = st.selectbox(
        "Legal Action Required",
        ["No Legal Action", "Show Cause Notice", "Recovery Action", "Settlement", "Closure", "Other"],
        key=f"legal_action_{case['case_id']}"
    )
    
    if legal_action == "Other":
        other_action = st.text_input(
            "Specify Other Action",
            key=f"other_action_{case['case_id']}"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"✅ Legal Cleared", key=f"legal_clear_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"LEGAL CLEARED: {legal_comment}"
                if legal_action != "No Legal Action":
                    comment_text += f" | Action: {legal_action}"
                
                if update_case_status(case['case_id'], "Approved", current_user, comment_text):
                    st.success("✅ Case legally cleared")
                    st.rerun()
            else:
                st.warning("Please add legal review comments")
    
    with col2:
        if st.button(f"⚠️ Legal Issues", key=f"legal_issues_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"LEGAL ISSUES IDENTIFIED: {legal_comment}"
                if legal_action != "No Legal Action":
                    comment_text += f" | Action Required: {legal_action}"
                
                if update_case_status(case['case_id'], "Under Review", current_user, comment_text):
                    st.success("✅ Legal issues logged, case sent back for review")
                    st.rerun()
            else:
                st.warning("Please specify the legal issues")
    
    with col3:
        if st.button(f"📄 Issue SCN", key=f"issue_scn_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"SHOW CAUSE NOTICE ISSUED: {legal_comment}"
                add_case_comment(case['case_id'], comment_text, "SCN Issued", current_user)
                st.success("✅ Show Cause Notice marked as issued")
                st.rerun()
            else:
                st.warning("Please add SCN details")
    
    with col4:
        if st.button(f"🔒 Close Case", key=f"close_legal_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"CASE CLOSED BY LEGAL: {legal_comment}"
                if update_case_status(case['case_id'], "Closed", current_user, comment_text):
                    st.success("✅ Case closed")
                    st.rerun()
            else:
                st.warning("Please add closure reason")

def show_scn_orders_section():
    """Display SCN and Orders management section"""
    
    st.write("### Show Cause Notices & Orders Management")
    
    # SCN/Orders entry form
    with st.expander("📝 Create New SCN/Order"):
        with st.form("scn_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                scn_case_id = st.text_input("Related Case ID")
                scn_type = st.selectbox("Type", ["Show Cause Notice", "Recovery Order", "Settlement Order", "Closure Order"])
                scn_date = st.date_input("Issue Date")
            
            with col2:
                scn_number = st.text_input("SCN/Order Number")
                scn_status = st.selectbox("Status", ["Draft", "Issued", "Response Received", "Closed"])
                response_date = st.date_input("Response Due Date")
            
            scn_details = st.text_area("Details/Content", height=100)
            
            if st.form_submit_button("📤 Create SCN/Order"):
                if all([scn_case_id, scn_number, scn_details]):
                    # Here you would save SCN/Order to database
                    # For now, just show success message
                    st.success("✅ SCN/Order created successfully")
                else:
                    st.error("Please fill all required fields")
    
    # Display existing SCN/Orders (this would come from database)
    st.write("### Existing SCN/Orders")
    
    # Sample data - in real implementation, this would come from database
    sample_scns = [
        {
            "scn_number": "SCN/2024/001",
            "case_id": "CASE001",
            "type": "Show Cause Notice",
            "status": "Issued",
            "issue_date": "2024-01-15",
            "response_due": "2024-01-30"
        },
        {
            "scn_number": "RO/2024/001",
            "case_id": "CASE002",
            "type": "Recovery Order",
            "status": "Response Received",
            "issue_date": "2024-01-10",
            "response_due": "2024-01-25"
        }
    ]
    
    if sample_scns:
        for scn in sample_scns:
            with st.expander(f"{scn['scn_number']} - {scn['type']} ({scn['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**SCN/Order Number:** {scn['scn_number']}")
                    st.write(f"**Related Case:** {scn['case_id']}")
                    st.write(f"**Type:** {scn['type']}")
                
                with col2:
                    st.write(f"**Status:** {scn['status']}")
                    st.write(f"**Issue Date:** {scn['issue_date']}")
                    st.write(f"**Response Due:** {scn['response_due']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📝 Update Status", key=f"update_{scn['scn_number']}"):
                        st.info("Status update functionality")
                
                with col2:
                    if st.button(f"📎 Add Documents", key=f"docs_{scn['scn_number']}"):
                        st.info("Document management functionality")
                
                with col3:
                    if st.button(f"🔒 Close", key=f"close_scn_{scn['scn_number']}"):
                        st.info("SCN closure functionality")
    else:
        st.info("No SCN/Orders found")
