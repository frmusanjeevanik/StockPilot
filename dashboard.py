import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from models import get_case_statistics, get_audit_logs
from utils import get_status_color, format_datetime
from auth import get_current_user_role

def show():
    """Display dashboard page"""
    st.title("📊 Dashboard")
    
    # Get statistics
    stats = get_case_statistics()
    user_role = get_current_user_role()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", stats["total_cases"])
    
    with col2:
        pending_cases = stats["by_status"].get("Submitted", 0) + stats["by_status"].get("Under Review", 0)
        st.metric("Pending Cases", pending_cases)
    
    with col3:
        approved_cases = stats["by_status"].get("Approved", 0)
        st.metric("Approved Cases", approved_cases)
    
    with col4:
        closed_cases = stats["by_status"].get("Closed", 0)
        st.metric("Closed Cases", closed_cases)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Status")
        if stats["by_status"]:
            fig = px.pie(
                values=list(stats["by_status"].values()),
                names=list(stats["by_status"].keys()),
                title="Case Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case data available")
    
    with col2:
        st.subheader("Cases by Region")
        if stats["by_region"]:
            fig = px.bar(
                x=list(stats["by_region"].keys()),
                y=list(stats["by_region"].values()),
                title="Cases by Region",
                labels={"x": "Region", "y": "Number of Cases"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No regional data available")
    
    # Recent cases
    st.subheader("Recent Cases")
    if stats["recent_cases"]:
        cases_data = []
        for case in stats["recent_cases"]:
            cases_data.append({
                "Case ID": case["case_id"],
                "LAN": case["lan"] or "N/A",
                "Status": f"{get_status_color(case['status'])} {case['status']}",
                "Product": case["product"],
                "Region": case["region"],
                "Created": format_datetime(case["created_at"]),
                "Created By": case["created_by"]
            })
        
        st.dataframe(cases_data, use_container_width=True)
    else:
        st.info("No recent cases found")
    
    # Role-specific sections
    if user_role in ["Reviewer", "Admin"]:
        st.subheader("🔍 Cases Requiring Review")
        # Get cases that need review (Submitted status)
        from models import get_cases_by_status
        review_cases = get_cases_by_status("Submitted")
        
        if review_cases:
            review_data = []
            for case in review_cases:
                review_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Referred By": case["referred_by"],
                    "Created": format_datetime(case["created_at"]),
                    "Created By": case["created_by"]
                })
            
            st.dataframe(review_data, use_container_width=True)
        else:
            st.info("No cases pending review")
    
    if user_role in ["Approver", "Admin"]:
        st.subheader("✅ Cases Requiring Approval")
        # Get cases that need approval (Under Review status)
        from models import get_cases_by_status
        approval_cases = get_cases_by_status("Under Review")
        
        if approval_cases:
            approval_data = []
            for case in approval_cases:
                approval_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Referred By": case["referred_by"],
                    "Created": format_datetime(case["created_at"]),
                    "Created By": case["created_by"]
                })
            
            st.dataframe(approval_data, use_container_width=True)
        else:
            st.info("No cases pending approval")
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_logs = get_audit_logs(limit=10)
    if recent_logs:
        activity_data = []
        for log in recent_logs:
            activity_data.append({
                "Time": format_datetime(log["performed_at"]),
                "Case ID": log["case_id"] or "System",
                "Action": log["action"],
                "Details": log["details"] or "N/A",
                "User": log["performed_by"]
            })
        
        st.dataframe(activity_data, use_container_width=True)
    else:
        st.info("No recent activity found")
