import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_complaints_visualization(data_path):
    """
    Create interactive complaints visualization using Plotly.
    
    Parameters:
    -----------
    data_path : str
        Path to the CSV file containing complaints data
        
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Interactive Plotly figure with 3 subplots
    """
    
    # Load data
    df = pd.read_excel(data_path)
    
    # Prepare data
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year
    
    # Calculate summaries
    dept_summary = df.groupby('DEPT').size().reset_index(name='TOTAL_COMPLAINTS')
    dept_summary = dept_summary.sort_values('TOTAL_COMPLAINTS', ascending=False)
    
    daily_counts = df.groupby('DATE').size().reset_index(name='TOTAL_COMPLAINTS')
    
    status_summary = df.groupby(['YEAR', 'CLOSED/OPEN']).size().reset_index(name='COUNT')
    pivot_status = status_summary.pivot(index='YEAR', columns='CLOSED/OPEN', values='COUNT').fillna(0)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "Complaints per Department",
            "Daily Complaints Trend",
            "Closed vs Open Complaints per Year"
        ),
        vertical_spacing=0.12,
        specs=[[{"type": "bar"}],
               [{"type": "scatter"}],
               [{"type": "bar"}]]
    )
    
    # 1. Complaints per Department (Bar Chart)
    fig.add_trace(
        go.Bar(
            x=dept_summary['DEPT'],
            y=dept_summary['TOTAL_COMPLAINTS'],
            name='Department Complaints',
            marker_color='skyblue',
            hovertemplate='<b>%{x}</b><br>Complaints: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Daily Complaints Trend (Line Chart)
    fig.add_trace(
        go.Scatter(
            x=daily_counts['DATE'],
            y=daily_counts['TOTAL_COMPLAINTS'],
            mode='lines+markers',
            name='Daily Complaints',
            line=dict(color='green', width=2),
            marker=dict(size=4),
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Complaints:</b> %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 3. Closed vs Open Complaints per Year (Stacked Bar Chart)
    years = pivot_status.index.tolist()
    
    for column in pivot_status.columns:
        fig.add_trace(
            go.Bar(
                x=years,
                y=pivot_status[column],
                name=column,
                marker_color='orange' if column == 'CLOSED' else 'blue',
                hovertemplate=f'<b>Year:</b> %{{x}}<br><b>{column}:</b> %{{y}}<extra></extra>'
            ),
            row=3, col=1
        )
    
    # Update layout
    fig.update_xaxes(title_text="Department", row=1, col=1)
    fig.update_yaxes(title_text="Number of Complaints", row=1, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Number of Complaints", row=2, col=1)
    
    fig.update_xaxes(title_text="Year", row=3, col=1)
    fig.update_yaxes(title_text="Number of Complaints", row=3, col=1)
    
    # Update overall layout
    fig.update_layout(
        height=1200,
        showlegend=True,
        title_text="<b>Complaints Analysis Dashboard</b>",
        title_x=0.5,
        title_font_size=20,
        hovermode='closest',
        barmode='stack'
    )
    
    return fig


# Example usage:
# fig = create_complaints_visualization('complaints_data.csv')
# fig.show()  # Display in Jupyter/browser
# fig.write_html('complaints_dashboard.html')  # Save as HTML


def process_complaints_data(data_path):
    """
    Process complaints data and generate interactive pie chart visualizations.
    
    Parameters:
    -----------
    data_path : str
        Path to the CSV or Excel file containing complaints data
        
    Returns:
    --------
    fig : plotly figure object with interactive pie charts
    """
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import os
    
    # Load data based on file extension
    file_extension = os.path.splitext(data_path)[1].lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(data_path)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(data_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    # Prepare Data
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year
    
    # Generate Summaries
    dept_summary = df.groupby('DEPT').size().reset_index(name='TOTAL_COMPLAINTS')
    yearly_counts = df.groupby('YEAR').size().reset_index(name='TOTAL_COMPLAINTS')
    status_summary = df.groupby(['YEAR', 'CLOSED/OPEN']).size().reset_index(name='COUNT')
    status_total = status_summary.groupby('CLOSED/OPEN')['COUNT'].sum().reset_index()
    
    # Create Interactive Plotly Pie Charts
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type':'pie'}, {'type':'pie'}, {'type':'pie'}]],
        subplot_titles=("Complaints per Department", 
                       "Complaints per Year", 
                       "Closed vs Open Complaints (All Years)")
    )
    
    # Department pie chart
    fig.add_trace(
        go.Pie(labels=dept_summary['DEPT'], 
               values=dept_summary['TOTAL_COMPLAINTS'],
               name="Department"),
        row=1, col=1
    )
    
    # Year pie chart
    fig.add_trace(
        go.Pie(labels=yearly_counts['YEAR'], 
               values=yearly_counts['TOTAL_COMPLAINTS'],
               name="Year"),
        row=1, col=2
    )
    
    # Status pie chart
    fig.add_trace(
        go.Pie(labels=status_total['CLOSED/OPEN'], 
               values=status_total['COUNT'],
               marker=dict(colors=['orange', 'blue']),
               name="Status"),
        row=1, col=3
    )
    
    # Update layout
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="Complaints Data Analysis"
    )
    
    return fig



import pandas as pd
import plotly.express as px
from typing import Optional
from plotly.graph_objs import Figure

# src/visualization/dashboard.py

def create_missing_values_chart(    
    dataset_path: str,
    title: str = "Missing Values per Column",
    height: int = 600,
    width: int = 1200,
) -> Optional[Figure]:
    """
    Reads a dataset from the given path and creates an interactive Plotly chart 
    showing missing values per column.

    Parameters
    ----------
    dataset_path : str
        Path to the dataset file (Excel).
    title : str, optional
        Chart title.
    height : int, optional
        Figure height.
    width : int, optional
        Figure width.

    Returns
    -------
    plotly.graph_objs.Figure or None
        Interactive Plotly figure if missing values exist, otherwise None.
    """

    # Read dataset
    df = pd.read_excel(dataset_path)

    # Calculate missing values per column
    null_data = df.isnull().sum().reset_index()
    null_data.columns = ["Column", "Missing Values"]

    # Filter columns with missing values
    null_data = null_data[null_data["Missing Values"] > 0]

    # If no missing values, return None
    if null_data.empty:
        return None

    # Create interactive bar chart
    fig = px.bar(
        null_data,
        x="Column",
        y="Missing Values",
        title=title,
        text="Missing Values",
        color="Missing Values",
        color_continuous_scale="Blues",
        hover_data=["Missing Values"],
    )

    # Show values on bars
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside"
    )

    # Improve layout for interactivity
    fig.update_layout(
        xaxis_title="Columns",
        yaxis_title="Count of Missing Values",
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        height=height,
        width=width,
        showlegend=False,
        hovermode="x unified",
        xaxis_tickangle=-45,
    )

    return fig




import pandas as pd
import plotly.express as px

def complaints_status_stacked_bar(dataset_path: str):
    """
    Reads complaint data from Excel and returns a Plotly stacked bar chart.
    Shows Closed vs Open complaints per month, faceted by year.
    """
    # Load and preprocess
    df = pd.read_excel(dataset_path)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year
    df['MONTH_NAME'] = df['DATE'].dt.strftime('%B')

    # Group by YEAR, MONTH_NAME, CLOSED/OPEN
    summary = (
        df.groupby(['YEAR', 'MONTH_NAME', 'CLOSED/OPEN'])
          .size()
          .reset_index(name='COUNT')
    )

    # Build stacked bar chart
    fig = px.bar(
        summary,
        x="MONTH_NAME",
        y="COUNT",
        color="CLOSED/OPEN",
        barmode="stack",
        facet_col="YEAR",
        title="Complaints Status by Month and Year",
        labels={"COUNT": "Number of Complaints"}
    )

    fig.update_layout(
        legend_title_text="Complaint Status",
        xaxis_title="Month",
        yaxis_title="Complaint Count",
        template="plotly_white"
    )

    return fig



import pandas as pd
import plotly.express as px

def complaints_trend_line(dataset_path: str):
    """
    Reads complaint data from Excel and returns a Plotly line chart.
    Shows monthly complaint counts with year-wise color differentiation.
    """
    # Load and preprocess
    df = pd.read_excel(dataset_path)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year
    df['MONTH'] = df['DATE'].dt.month

    # Group by YEAR, MONTH
    summary = (
        df.groupby(['YEAR', 'MONTH'])
          .size()
          .reset_index(name='COUNT')
    )

    # Build line chart
    fig = px.line(
        summary,
        x="MONTH",
        y="COUNT",
        color="YEAR",
        markers=True,
        title="Complaints Count by Month (Year-wise Colors)",
        labels={"COUNT": "Number of Complaints", "MONTH": "Month"}
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        ),
        template="plotly_white"
    )

    return fig
