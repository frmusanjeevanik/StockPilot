import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Actioner", "Admin"])
def show():
    """Display actioner panel"""
    st.title("🔒 Actioner Panel")
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Ready for Closure", "🔒 Closed Cases", "📊 Closure Analytics"])
    
    with tab1:
        st.subheader("Cases Ready for Closure")
        
        # Cases that can be closed (approved cases, legal cleared cases, etc.)
        approved_cases = get_cases_by_status("Approved")
        
        if approved_cases:
            for case in approved_cases:
                with st.expander(f"Case: {case['case_id']} - {case['product']} ({case['region']})"):
                    show_closure_case_details(case, current_user)
        else:
            st.info("📭 No cases ready for closure")
    
    with tab2:
        st.subheader("Closed Cases")
        closed_cases = get_cases_by_status("Closed")
        
        if closed_cases:
            for case in closed_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} Closed"):
                    show_closed_case_details(case)
        else:
            st.info("📭 No closed cases")
    
    with tab3:
        st.subheader("Closure Analytics")
        show_closure_analytics()

def show_closure_case_details(case, current_user):
    """Display case details for closure workflow"""
    
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
        st.write(f"**Approved By:** {case['approved_by'] or 'N/A'}")
    
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
    
    # Closure actions
    st.write("**Closure Actions:**")
    
    closure_reason = st.selectbox(
        "Closure Reason",
        [
            "Case Resolved Successfully",
            "Recovery Completed",
            "Settlement Reached",
            "Legal Action Completed",
            "Customer Satisfied",
            "No Further Action Required",
            "Transferred to Other Department",
            "Duplicate Case",
            "Other"
        ],
        key=f"closure_reason_{case['case_id']}"
    )
    
    if closure_reason == "Other":
        other_reason = st.text_input(
            "Specify Other Reason",
            key=f"other_closure_{case['case_id']}"
        )
    
    closure_comments = st.text_area(
        "Closure Comments",
        key=f"closure_comment_{case['case_id']}",
        placeholder="Enter detailed closure comments, actions taken, and final resolution..."
    )
    
    # Additional closure details
    col1, col2 = st.columns(2)
    
    with col1:
        recovery_amount = st.number_input(
            "Recovery Amount (if applicable)",
            min_value=0.0,
            key=f"recovery_{case['case_id']}"
        )
    
    with col2:
        follow_up_required = st.checkbox(
            "Follow-up Required",
            key=f"followup_{case['case_id']}"
        )
    
    if follow_up_required:
        follow_up_date = st.date_input(
            "Follow-up Date",
            key=f"followup_date_{case['case_id']}"
        )
        follow_up_notes = st.text_area(
            "Follow-up Notes",
            key=f"followup_notes_{case['case_id']}"
        )
    else:
        follow_up_date = None
        follow_up_notes = ""
    
    # Closure buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🔒 Close Case", key=f"close_{case['case_id']}"):
            if closure_comments.strip():
                final_comment = f"CASE CLOSED - Reason: {closure_reason}\n\nDetails: {closure_comments}"
                
                if recovery_amount > 0:
                    final_comment += f"\n\nRecovery Amount: ₹{recovery_amount:,.2f}"
                
                if follow_up_required:
                    final_comment += f"\n\nFollow-up Required: Yes (Date: {follow_up_date})\nNotes: {follow_up_notes}"
                
                if update_case_status(case['case_id'], "Closed", current_user, final_comment):
                    st.success("✅ Case closed successfully")
                    st.rerun()
            else:
                st.warning("Please add closure comments")
    
    with col2:
        if st.button(f"🔙 Send Back", key=f"send_back_closure_{case['case_id']}"):
            if closure_comments.strip():
                comment_text = f"SENT BACK FROM CLOSURE: {closure_comments}"
                if update_case_status(case['case_id'], "Under Review", current_user, comment_text):
                    st.success("✅ Case sent back for review")
                    st.rerun()
            else:
                st.warning("Please specify reason for sending back")
    
    with col3:
        if st.button(f"📝 Add Note", key=f"add_note_closure_{case['case_id']}"):
            if closure_comments.strip():
                add_case_comment(case['case_id'], closure_comments, "Closure Note", current_user)
                st.success("✅ Note added")
                st.rerun()
            else:
                st.warning("Please enter a note")

def show_closed_case_details(case):
    """Display read-only details for closed cases"""
    
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
        st.write(f"**Closed By:** {case['closed_by'] or 'N/A'}")
        st.write(f"**Closed At:** {format_datetime(case['closed_at'])}")
        st.write(f"**Created By:** {case['created_by']}")
        st.write(f"**Case Date:** {case['case_date']}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Comments history (including closure reason)
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Complete History:**")
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

def show_closure_analytics():
    """Display closure analytics and statistics"""
    
    st.write("### Closure Performance Metrics")
    
    # Sample metrics - in real implementation, these would come from database queries
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cases Closed This Month", "45")
    
    with col2:
        st.metric("Average Closure Time", "12.5 days")
    
    with col3:
        st.metric("Total Recovery Amount", "₹2.5M")
    
    with col4:
        st.metric("Follow-up Cases", "8")
    
    st.divider()
    
    # Closure reasons chart
    st.write("### Closure Reasons Distribution")
    
    # Sample data - replace with actual database query
    closure_reasons = {
        "Case Resolved Successfully": 25,
        "Recovery Completed": 15,
        "Settlement Reached": 10,
        "Legal Action Completed": 8,
        "No Further Action Required": 5,
        "Other": 3
    }
    
    import plotly.express as px
    
    fig = px.pie(
        values=list(closure_reasons.values()),
        names=list(closure_reasons.keys()),
        title="Case Closure Reasons"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly closure trend
    st.write("### Monthly Closure Trend")
    
    # Sample trend data
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='ME')
    closures = [30, 35, 28, 42, 38, 45]  # Sample data
    
    trend_data = pd.DataFrame({
        'Month': dates,
        'Closures': closures
    })
    
    fig = px.line(trend_data, x='Month', y='Closures', title='Monthly Case Closures')
    st.plotly_chart(fig, use_container_width=True)
    
    # Export options
    st.write("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Closure Report"):
            st.info("Closure report export functionality")
    
    with col2:
        if st.button("📈 Generate Analytics Dashboard"):
            st.info("Advanced analytics dashboard")
