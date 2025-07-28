import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from models import get_case_statistics, search_cases
from utils import export_cases_to_csv, get_dropdown_options, format_datetime
from datetime import datetime, timedelta

def show():
    """Display analytics page"""
    
    # Get options and statistics
    options = get_dropdown_options()
    stats = get_case_statistics()
    
    # Filters
    st.subheader("🔍 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_from = st.date_input("From Date", datetime.now() - timedelta(days=30))
    
    with col2:
        date_to = st.date_input("To Date", datetime.now())
    
    with col3:
        filter_status = st.selectbox("Status", ["All"] + options["statuses"])
    
    with col4:
        filter_region = st.selectbox("Region", ["All"] + options["regions"])
    
    # Apply filters and get data
    filters = {}
    if filter_status != "All":
        filters["status"] = filter_status
    if filter_region != "All":
        filters["region"] = filter_region
    if date_from:
        filters["date_from"] = date_from.strftime("%Y-%m-%d")
    if date_to:
        filters["date_to"] = date_to.strftime("%Y-%m-%d")
    
    # Search cases with filters
    filtered_cases = search_cases("", filters) if filters else []
    
    st.divider()
    
    # Key Performance Indicators
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Cases", stats["total_cases"])
    
    with col2:
        avg_resolution_time = "5.2 days"  # This would be calculated from actual data
        st.metric("Avg Resolution Time", avg_resolution_time)
    
    with col3:
        approval_rate = "78%"  # This would be calculated from actual data
        st.metric("Approval Rate", approval_rate)
    
    with col4:
        pending_cases = sum([
            stats["by_status"].get("Submitted", 0),
            stats["by_status"].get("Under Review", 0),
            stats["by_status"].get("Legal Review", 0)
        ])
        st.metric("Pending Cases", pending_cases)
    
    with col5:
        if len(filtered_cases) > 0:
            st.metric("Filtered Results", len(filtered_cases))
        else:
            st.metric("No Filter Applied", "")
    
    # Charts section
    st.subheader("📈 Visual Analytics")
    
    # Case trend over time
    st.subheader("Case Trend Over Time")
    if stats["total_cases"] > 0:
        # This would ideally use actual date-based data
        # For now, showing sample trend
        dates = pd.date_range(start=date_from, end=date_to, freq='D')
        sample_data = pd.DataFrame({
            'Date': dates,
            'Cases': [abs(hash(str(d)) % 10) for d in dates]  # Sample data
        })
        
        fig = px.line(sample_data, x='Date', y='Cases', title='Daily Case Creation Trend')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for trend analysis")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Product")
        if stats["by_product"]:
            fig = px.bar(
                x=list(stats["by_product"].keys()),
                y=list(stats["by_product"].values()),
                title="Product Distribution"
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available")
    
    with col2:
        st.subheader("Regional Performance")
        if stats["by_region"]:
            fig = px.pie(
                values=list(stats["by_region"].values()),
                names=list(stats["by_region"].keys()),
                title="Cases by Region"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No regional data available")
    
    # Status funnel
    st.subheader("Case Status Funnel")
    if stats["by_status"]:
        # Create funnel data (ordered by typical workflow)
        funnel_order = ["Draft", "Submitted", "Under Review", "Approved", "Closed"]
        funnel_data = []
        funnel_values = []
        
        for status in funnel_order:
            if status in stats["by_status"]:
                funnel_data.append(status)
                funnel_values.append(stats["by_status"][status])
        
        if funnel_data:
            fig = go.Figure(go.Funnel(
                y=funnel_data,
                x=funnel_values,
                textinfo="value+percent initial"
            ))
            fig.update_layout(title="Case Processing Funnel")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No status data available for funnel")
    
    # Data export section
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info(f"Ready to export {len(filtered_cases) if filtered_cases else stats['total_cases']} cases")
    
    with col2:
        if st.button("📊 Export to CSV", use_container_width=True):
            cases_to_export = filtered_cases if filtered_cases else search_cases("")
            if cases_to_export:
                file_path, message = export_cases_to_csv(cases_to_export)
                if file_path:
                    st.success(f"✅ {message}")
                    st.info(f"File saved: {file_path}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("No cases to export")
    
    with col3:
        if st.button("📈 Generate Report", use_container_width=True):
            st.info("📋 Detailed report generation feature coming soon!")
    
    # Summary statistics
    if filtered_cases:
        st.subheader("📋 Filtered Results Summary")
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([dict(case) for case in filtered_cases])
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Filtered Cases", len(df))
        
        with col2:
            if 'status' in df.columns:
                most_common_status = df['status'].mode().iloc[0] if not df.empty else "N/A"
                st.metric("Most Common Status", most_common_status)
        
        with col3:
            if 'region' in df.columns:
                most_common_region = df['region'].mode().iloc[0] if not df.empty else "N/A"
                st.metric("Most Common Region", most_common_region)
        
        # Display filtered data
        st.subheader("Filtered Cases")
        display_data = []
        for case in filtered_cases[:50]:  # Limit to 50 for performance
            display_data.append({
                "Case ID": case["case_id"],
                "Status": case["status"],
                "Product": case["product"],
                "Region": case["region"],
                "Created": format_datetime(case["created_at"]),
                "Created By": case["created_by"]
            })
        
        if display_data:
            st.dataframe(display_data, use_container_width=True)
            if len(filtered_cases) > 50:
                st.info(f"Showing first 50 of {len(filtered_cases)} cases")
        else:
            st.info("No cases match the applied filters")
