import streamlit as st
from models import get_cases_by_status, get_case_by_id, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Reviewer", "Admin"])
def show():
    """Display reviewer panel"""
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Review", "🔄 In Progress", "✅ Completed"])
    
    with tab1:
        st.subheader("Cases Pending Review")
        submitted_cases = get_cases_by_status("Submitted")
        
        if submitted_cases:
            for case in submitted_cases:
                with st.expander(f"Case: {case['case_id']} - {case['product']} ({case['region']})"):
                    show_case_details(case, current_user, allow_review=True)
        else:
            st.info("📭 No cases pending review")
    
    with tab2:
        st.subheader("Cases Under Review")
        under_review_cases = get_cases_by_status("Under Review")
        
        if under_review_cases:
            for case in under_review_cases:
                with st.expander(f"Case: {case['case_id']} - {case['product']} ({case['region']})"):
                    show_case_details(case, current_user, allow_review=True)
        else:
            st.info("📭 No cases under review")
    
    with tab3:
        st.subheader("Reviewed Cases")
        reviewed_cases = get_cases_by_status("Approved") + get_cases_by_status("Rejected")
        
        if reviewed_cases:
            for case in reviewed_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} {case['status']}"):
                    show_case_details(case, current_user, allow_review=False)
        else:
            st.info("📭 No reviewed cases")

def show_case_details(case, current_user, allow_review=True):
    """Display detailed case information"""
    
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
        st.write(f"**Created At:** {format_datetime(case['created_at'])}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
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
    
    # Comments
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Comments History:**")
        for comment in comments:
            st.write(f"**{comment['created_by']}** ({format_datetime(comment['created_at'])}) - *{comment['comment_type']}*")
            st.write(comment['comment'])
            st.divider()
    
    # Review actions (only if allowed)
    if allow_review and case['status'] in ['Submitted', 'Under Review']:
        st.write("**Review Actions:**")
        
        # Comment section
        review_comment = st.text_area(
            "Add Review Comment",
            key=f"comment_{case['case_id']}",
            placeholder="Enter your review comments..."
        )
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"🔄 Start Review", key=f"start_{case['case_id']}"):
                if update_case_status(case['case_id'], "Under Review", current_user, review_comment):
                    st.success("✅ Case moved to Under Review")
                    st.rerun()
        
        with col2:
            if st.button(f"✅ Approve", key=f"approve_{case['case_id']}"):
                if review_comment.strip():
                    if update_case_status(case['case_id'], "Approved", current_user, review_comment):
                        st.success("✅ Case approved successfully")
                        st.rerun()
                else:
                    st.warning("Please add a comment before approving")
        
        with col3:
            if st.button(f"❌ Reject", key=f"reject_{case['case_id']}"):
                if review_comment.strip():
                    if update_case_status(case['case_id'], "Rejected", current_user, review_comment):
                        st.success("✅ Case rejected")
                        st.rerun()
                else:
                    st.warning("Please add a comment before rejecting")
        
        with col4:
            if st.button(f"⚖️ Send to Legal", key=f"legal_{case['case_id']}"):
                if update_case_status(case['case_id'], "Legal Review", current_user, review_comment):
                    st.success("✅ Case sent to legal review")
                    st.rerun()
        
        # Add comment only
        if st.button(f"💬 Add Comment Only", key=f"add_comment_{case['case_id']}"):
            if review_comment.strip():
                add_case_comment(case['case_id'], review_comment, "Reviewer Comment", current_user)
                st.success("✅ Comment added")
                st.rerun()
            else:
                st.warning("Please enter a comment")
