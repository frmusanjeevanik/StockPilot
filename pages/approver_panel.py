import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Approver", "Admin"])
def show():
    """Display approver panel"""
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Approval", "✅ Approved", "❌ Rejected"])
    
    with tab1:
        st.subheader("Cases Pending Approval")
        approved_cases = get_cases_by_status("Approved")  # Cases approved by reviewers, pending final approval
        
        if approved_cases:
            for case in approved_cases:
                with st.expander(f"Case: {case['case_id']} - {case['product']} ({case['region']})"):
                    show_case_details_for_approval(case, current_user)
        else:
            st.info("📭 No cases pending approval")
    
    with tab2:
        st.subheader("Final Approved Cases")
        # You might want to add a new status like "Final Approved" for this
        st.info("Cases with final approval will appear here")
    
    with tab3:
        st.subheader("Rejected Cases")
        rejected_cases = get_cases_by_status("Rejected")
        
        if rejected_cases:
            for case in rejected_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} {case['status']}"):
                    show_read_only_case_details(case)
        else:
            st.info("📭 No rejected cases")

def show_case_details_for_approval(case, current_user):
    """Display case details for approval workflow"""
    
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
    
    # Approval actions
    st.write("**Approval Actions:**")
    
    approval_comment = st.text_area(
        "Approval Comments",
        key=f"approval_comment_{case['case_id']}",
        placeholder="Enter your approval decision comments..."
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"✅ Final Approve", key=f"final_approve_{case['case_id']}"):
            if approval_comment.strip():
                # You might want to create a new status like "Final Approved"
                if update_case_status(case['case_id'], "Closed", current_user, f"APPROVED: {approval_comment}"):
                    st.success("✅ Case given final approval")
                    st.rerun()
            else:
                st.warning("Please add approval comments")
    
    with col2:
        if st.button(f"❌ Reject", key=f"final_reject_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Rejected", current_user, f"REJECTED: {approval_comment}"):
                    st.success("✅ Case rejected")
                    st.rerun()
            else:
                st.warning("Please add rejection comments")
    
    with col3:
        if st.button(f"🔙 Send Back for Review", key=f"send_back_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Under Review", current_user, f"SENT BACK: {approval_comment}"):
                    st.success("✅ Case sent back for review")
                    st.rerun()
            else:
                st.warning("Please add comments explaining why it's being sent back")

def show_read_only_case_details(case):
    """Display read-only case details"""
    
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
        st.write(f"**Last Updated:** {format_datetime(case['updated_at'])}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Comments history
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Comments History:**")
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
