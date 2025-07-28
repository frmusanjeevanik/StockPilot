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
    
    # TAT (Turn Around Time) Section
    st.subheader("📊 Turn Around Time (TAT) Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg. Review TAT", "2.5 days", delta="-0.3 days")
    
    with col2:
        st.metric("Avg. Approval TAT", "1.8 days", delta="+0.2 days")
    
    with col3:
        st.metric("Avg. Legal Review TAT", "3.2 days", delta="-0.5 days")
    
    with col4:
        st.metric("Avg. Closure TAT", "1.2 days", delta="-0.1 days")
    
    # TAT Trend Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("TAT Trends")
        # Sample data for TAT trends
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[2.8, 2.5, 2.3, 2.5],
            mode='lines+markers',
            name='Review TAT',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[2.0, 1.8, 1.6, 1.8],
            mode='lines+markers',
            name='Approval TAT',
            line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[3.7, 3.2, 3.0, 3.2],
            mode='lines+markers',
            name='Legal Review TAT',
            line=dict(color='purple')
        ))
        fig.update_layout(
            title="TAT Trends (Days)",
            xaxis_title="Time Period",
            yaxis_title="Days",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("SLA Compliance")
        # SLA compliance data
        sla_data = {
            "Review": 85,
            "Approval": 92,
            "Legal Review": 78,
            "Closure": 95
        }
        
        fig = px.bar(
            x=list(sla_data.keys()),
            y=list(sla_data.values()),
            title="SLA Compliance (%)",
            labels={"x": "Process", "y": "Compliance %"},
            color=list(sla_data.values()),
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
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
                    "Submitted": format_datetime(case["created_at"])
                })
            st.dataframe(review_data, use_container_width=True)
        else:
            st.info("📭 No cases pending review")
    
    if user_role in ["Approver", "Admin"]:
        st.subheader("✅ Cases Requiring Approval")
        # Get cases that need approval (Approved by reviewer status)
        approval_cases = get_cases_by_status("Approved")
        
        if approval_cases:
            approval_data = []
            for case in approval_cases:
                approval_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Reviewed": format_datetime(case["updated_at"])
                })
            st.dataframe(approval_data, use_container_width=True)
        else:
            st.info("📭 No cases pending approval")
    
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
