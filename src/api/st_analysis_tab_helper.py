import streamlit as st
import pandas as pd
import plotly.express as px
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
import streamlit as st
import plotly.express as px

def complaint_report_dashboard(complaint_df):
    """
    Display complaint report as interactive table + Plotly chart in Streamlit.
    """

    col1, col2 = st.columns([1, 1.4])

    # --- Left column: Raw table ---
    with col1:
        st.markdown("### 📋 Raw Counts")
        st.dataframe(
            complaint_df,
            use_container_width=True,
            hide_index=True
        )

    # --- Right column: Interactive chart ---
    with col2:
        st.markdown("### 📊 Visual Report")

        # Sort by count for readability
        complaint_df_sorted = complaint_df.sort_values("Count", ascending=False)

        fig = px.bar(
            complaint_df_sorted,
            x="Complaint Type",
            y="Count",
            text="Count",
            color="Complaint Type",
                title="Complaint Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"Complaint Type": True, "Count": True}
        )

        # Layout polish + interactivity
        fig.update_layout(
            template="plotly_white",
            height=500,
            title_x=0.5,
            xaxis_title="Complaint Type",
            yaxis_title="Total Count",
            xaxis_tickangle=-30,
            font=dict(size=13),
            margin=dict(l=40, r=40, t=60, b=80),
            hovermode="x unified",   # unified hover line
            dragmode="zoom",         # allow zoom with mouse drag
            showlegend=True          # keep legend for click-to-hide
        )

        # Trace styling
        fig.update_traces(
            textposition="outside",
            marker_line_width=1.3,
            marker_line_color="red",
            hovertemplate="<b>%{x}</b><br>Count: %{y}"  # custom tooltip
        )

        st.plotly_chart(fig, use_container_width=True, config={
            "displayModeBar": True,   # show toolbar
            "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"], # annotation tools
            "scrollZoom": True        # enable zoom with mouse wheel
        })
