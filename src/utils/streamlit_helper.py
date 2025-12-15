import streamlit as st
import plotly.express as px

def sales_distribution_plots(df):
    """
    Generate sales distribution and box plots using Plotly in Streamlit.

    Parameters:
    df (pd.DataFrame): DataFrame containing at least 'sales' and 'category' columns.
    """

    # Distribution plot
    st.subheader("Sales Distribution")
    fig = px.histogram(df, x='sales', nbins=20, title='Sales Distribution')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Box plot
    st.subheader("Sales Box Plot by Category")
    fig2 = px.box(df, x='category', y='sales', title='Sales Distribution by Category')
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)



import streamlit as st

def display_sales_summary(summary: dict):
    """
    Display sales summary metrics in Streamlit.

    Parameters:
    summary (dict): Dictionary containing keys:
        - 'total_sales'
        - 'avg_sales'
        - 'max_sales'
        - 'min_sales'
    """

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"${summary['total_sales']:,}")
    col2.metric("Average Sales", f"${summary['avg_sales']:.0f}")
    col3.metric("Max Sales", f"${summary['max_sales']:,}")
    col4.metric("Min Sales", f"${summary['min_sales']:,}")
