import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Generate sample data for demonstration
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    complaints = pd.DataFrame({
        'complaint_id': [f'CMP{str(i).zfill(5)}' for i in range(1, 101)],
        'date': np.random.choice(dates, 100),
        'category': np.random.choice(['Billing', 'Service', 'Technical', 'Payment', 'Connection'], 100),
        'priority': np.random.choice(['High', 'Medium', 'Low'], 100, p=[0.2, 0.5, 0.3]),
        'status': np.random.choice(['Open', 'In-Progress', 'Closed', 'Pending'], 100, p=[0.15, 0.25, 0.5, 0.1]),
        'resolution_days': np.random.randint(1, 30, 100),
        'consumer_id': [f'CSM{str(i).zfill(4)}' for i in np.random.randint(1000, 9999, 100)],
        'assigned_to': np.random.choice(['Agent A', 'Agent B', 'Agent C', 'Agent D'], 100),
        'satisfaction_score': np.random.randint(1, 6, 100)
    })
    
    return complaints


def complaint_overview_dashboard():
    """
    Complete Complaint Overview Dashboard
    Call this function inside your tab to render the entire dashboard
    """
    
    st.subheader("📊 Complaint Overview Dashboard")
    
    # Load data
    df = generate_sample_data()
    
    # Filter Section
    with st.expander("🔍 Filters", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            date_range = st.date_input(
                "Date Range",
                value=(df['date'].min().date(), df['date'].max().date()),
                key="date_filter"
            )
        
        with col_f2:
            status_filter = st.multiselect(
                "Status",
                options=df['status'].unique(),
                default=df['status'].unique()
            )
        
        with col_f3:
            priority_filter = st.multiselect(
                "Priority",
                options=df['priority'].unique(),
                default=df['priority'].unique()
            )
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['priority'].isin(priority_filter))
    ]
    
    # KPI Metrics with delta
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_complaints = len(filtered_df)
    open_complaints = len(filtered_df[filtered_df['status'] == 'Open'])
    closed_complaints = len(filtered_df[filtered_df['status'] == 'Closed'])
    in_progress = len(filtered_df[filtered_df['status'] == 'In-Progress'])
    avg_resolution = filtered_df[filtered_df['status'] == 'Closed']['resolution_days'].mean()
    high_priority = len(filtered_df[filtered_df['priority'] == 'High'])
    
    with col1:
        st.metric(
            label="Total Complaints",
            value=f"{total_complaints}",
            delta=f"{int(total_complaints * 0.12)} vs last period"
        )
    
    with col2:
        st.metric(
            label="Open Complaints",
            value=f"{open_complaints}",
            delta=f"-{int(open_complaints * 0.08)}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Closed Complaints",
            value=f"{closed_complaints}",
            delta=f"+{int(closed_complaints * 0.15)}"
        )
    
    with col4:
        st.metric(
            label="In-Progress",
            value=f"{in_progress}",
            delta=f"{int(in_progress * 0.05)}"
        )
    
    with col5:
        st.metric(
            label="Avg Resolution Time",
            value=f"{avg_resolution:.1f} days",
            delta=f"-{avg_resolution * 0.1:.1f} days",
            delta_color="inverse"
        )
    
    with col6:
        st.metric(
            label="High Priority",
            value=f"{high_priority}",
            delta=f"{int(high_priority * 0.18)}",
            delta_color="inverse"
        )
    
    st.divider()
    
    # Visualization Section
    st.markdown("### 📊 Analytics & Insights")
    
    tab_viz1, tab_viz2, tab_viz3 = st.tabs(["Trends", "Performance", "Details"])
    
    with tab_viz1:
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            # Complaint Trend Over Time
            trend_data = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
            trend_data.columns = ['Date', 'Count']
            
            fig_trend = px.line(
                trend_data,
                x='Date',
                y='Count',
                title='Complaint Trends Over Time',
                markers=True
            )
            fig_trend.update_layout(height=300)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col_v2:
            # Status Distribution
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Complaint Status Distribution',
                hole=0.4
            )
            fig_status.update_layout(height=300)
            st.plotly_chart(fig_status, use_container_width=True)
        
        col_v3, col_v4 = st.columns(2)
        
        with col_v3:
            # Category Distribution
            category_counts = filtered_df['category'].value_counts()
            fig_category = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title='Complaints by Category',
                labels={'x': 'Category', 'y': 'Count'}
            )
            fig_category.update_layout(height=300)
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col_v4:
            # Priority Breakdown
            priority_counts = filtered_df['priority'].value_counts()
            fig_priority = px.funnel(
                y=priority_counts.index,
                x=priority_counts.values,
                title='Priority Distribution'
            )
            fig_priority.update_layout(height=300)
            st.plotly_chart(fig_priority, use_container_width=True)
    
    with tab_viz2:
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # Agent Performance
            agent_perf = filtered_df.groupby('assigned_to').agg({
                'complaint_id': 'count',
                'resolution_days': 'mean'
            }).reset_index()
            agent_perf.columns = ['Agent', 'Total Cases', 'Avg Resolution Days']
            
            fig_agent = px.bar(
                agent_perf,
                x='Agent',
                y='Total Cases',
                title='Agent Performance - Cases Handled',
                color='Avg Resolution Days',
                color_continuous_scale='RdYlGn_r'
            )
            fig_agent.update_layout(height=300)
            st.plotly_chart(fig_agent, use_container_width=True)
        
        with col_p2:
            # Satisfaction Score
            satisfaction_avg = filtered_df.groupby('category')['satisfaction_score'].mean().reset_index()
            
            fig_satisfaction = px.bar(
                satisfaction_avg,
                x='category',
                y='satisfaction_score',
                title='Average Satisfaction Score by Category',
                labels={'category': 'Category', 'satisfaction_score': 'Avg Score'},
                color='satisfaction_score',
                color_continuous_scale='RdYlGn'
            )
            fig_satisfaction.update_layout(height=300, yaxis_range=[0, 5])
            st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        # Resolution Time Heatmap
        resolution_heatmap = filtered_df.groupby(['category', 'priority'])['resolution_days'].mean().unstack()
        
        fig_heatmap = px.imshow(
            resolution_heatmap,
            title='Average Resolution Time (Days) - Category vs Priority',
            labels=dict(x="Priority", y="Category", color="Days"),
            color_continuous_scale='RdYlGn_r',
            aspect="auto"
        )
        fig_heatmap.update_layout(height=300)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab_viz3:
        # Search and filter
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_query = st.text_input("🔍 Search by Complaint ID or Consumer ID", "")
        
        with search_col2:
            show_records = st.selectbox("Show records", [10, 25, 50, 100])
        
        # Filter data based on search
        display_df = filtered_df.copy()
        if search_query:
            display_df = display_df[
                (display_df['complaint_id'].str.contains(search_query, case=False)) |
                (display_df['consumer_id'].str.contains(search_query, case=False))
            ]
        
        # Display data table
        st.dataframe(
            display_df.head(show_records)[
                ['complaint_id', 'date', 'consumer_id', 'category', 'priority', 'status', 'assigned_to', 'resolution_days']
            ].style.background_gradient(subset=['resolution_days'], cmap='RdYlGn_r'),
            use_container_width=True,
            height=400
        )
        
        # Export options
        col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 4])
        
        with col_exp1:
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f'complaints_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        
        with col_exp2:
            st.button("📊 Generate Report", type="secondary")
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("➕ New Complaint", use_container_width=True):
            st.info("📝 New Complaint form - Feature ready for integration")
    
    with col_q2:
        if st.button("📈 Advanced Analytics", use_container_width=True):
            st.info("🔬 Advanced Analytics module - Ready for deployment")
    
    with col_q3:
        if st.button("🔔 Set Alerts", use_container_width=True):
            st.info("⚙️ Alert Configuration - SLA breach notifications ready")
    
    with col_q4:
        if st.button("📧 Bulk Actions", use_container_width=True):
            st.info("🚀 Bulk Operations - Ready for integration")
    
    # Quick Links Section
    st.markdown("### 🔗 Quick Links")
    
    quick_option = st.selectbox(
        "Navigate to related features:",
        [
            "Select an option",
            "Consumer History",
            "Consumer Ledger",
            "Consumer Bill Wise Balances",
            "Bill Calculator",
            "Adhoc Reports"
        ]
    )
    
    if quick_option == "Consumer History":
        st.success("✅ Consumer History - Click to view detailed consumer interaction timeline")
    elif quick_option == "Consumer Ledger":
        st.success("✅ Consumer Ledger - Access complete financial transaction history")
    elif quick_option == "Consumer Bill Wise Balances":
        st.success("✅ Consumer Bill Wise Balances - View outstanding balances by billing period")
    elif quick_option == "Bill Calculator":
        st.success("✅ Bill Calculator - Calculate estimates based on usage patterns")
    elif quick_option == "Adhoc Reports":
        st.success("✅ Adhoc Reports - Generate custom reports with flexible parameters")


# USAGE EXAMPLE:
# with tab1:
#     complaint_overview_dashboard()