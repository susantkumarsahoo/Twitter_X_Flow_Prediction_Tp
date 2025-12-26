import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


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

import pandas as pd
import plotly.express as px

def unique_value_bar_chart(dataset_path: str):
    """
    Reads complaint dataset and returns an interactive Plotly bar chart
    showing the number of unique values per selected column.
    """
    # Load dataset
    df = pd.read_excel(dataset_path)

    # Columns to analyze
    cols = [
        'SHIFT DUTY', 'QUERY/REQUEST/COMPLAINT',
        'COMPLAINT DETAILS', 'COMPLAINT NUMBER', 'SECTION', 'SUB-DIVISION',
        'DIVISION', 'CIRCLE', 'COMPLAINT TYPE', 'CONSUMER NUMBER',
        'MOBILE NUMB', 'DEPT', 'CLOSED/OPEN', 'TWEET-LINK',
        'COMPLAINANT NAME'
    ]

    # Compute unique counts
    unique_counts = {col: df[col].nunique() for col in cols}
    unique_df = pd.DataFrame(list(unique_counts.items()), columns=['Column', 'Unique Values'])

    # Build colorful interactive bar chart
    fig = px.bar(
        unique_df,
        x='Column',
        y='Unique Values',
        text='Unique Values',
        color='Unique Values',  # adds color scale
        color_continuous_scale='Rainbow',  # vibrant palette
        title='🌈 Unique Value Counts per Column',
        labels={'Unique Values': 'Number of Unique Entries'},
    )

    # Layout tweaks for more style
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_tickangle=-45,
        template='plotly_dark',  # dark theme for contrast
        yaxis_title='Unique Value Count',
        xaxis_title='Column Name',
        font=dict(size=12, color='white'),
        title_font=dict(size=18, color='gold'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(30,30,30,1)',
        width=1400, # custom width in pixels 
        height=600 # custom height in pixels
    )

    return fig




import plotly.express as px

import pandas as pd
import plotly.express as px

import pandas as pd
import plotly.express as px

def plot_complaint_pie_chart(data_path, column_name='COMPLAINT TYPE',
                             title="Complaint Distribution", width=1400, height=1100):
    """
    Reads complaint data from a file and returns an interactive donut-style pie chart.

    Parameters:
        data_path (str): Path to the CSV/Excel file containing complaint data
        column_name (str): Column name to analyze (default: 'COMPLAINT TYPE')
        title (str): Chart title
        width (int): Chart width in pixels
        height (int): Chart height in pixels
    """
    # Load data (auto-detect CSV or Excel)
    if data_path.endswith(".csv"):
        df = pd.read_csv(data_path)
    elif data_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(data_path)
    else:
        raise ValueError("Unsupported file format. Use .csv, .xls, or .xlsx")

    # Get complaint counts
    complaint_counts = df[column_name].value_counts()

    # Define a bold, deep color palette

    color_palette = [
        "#1f77b4",  # deep blue
        "#ff7f0e",  # vivid orange
        "#2ca02c",  # strong green
        "#d62728",  # deep red
        "#9467bd",  # rich purple
        "#8c564b",  # earthy brown
        "#e377c2",  # magenta
        "#7f7f7f",  # dark gray
        "#bcbd22",  # olive
        "#17becf"   # teal
    ]

    # Create pie chart with dark background
    fig = px.pie(
        names=complaint_counts.index,
        values=complaint_counts.values,
        title=title,
        hole=0.4,
        color=complaint_counts.index,
        color_discrete_sequence=color_palette
    )

    # Enhance trace details with visible text
    fig.update_traces(
        textinfo='percent+label',
        textfont=dict(color="white", size=14),   # bright text for visibility
        pull=[0.05] * len(complaint_counts),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}"
    )

    # Layout improvements with deep gray background and visible fonts
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=22, family="Arial", color="white")),
        legend=dict(title="Complaint Type", orientation="h", y=-0.2, x=0.5, xanchor="center",
                    font=dict(color="white")),   # legend text in white
        margin=dict(t=50, b=50, l=50, r=50),
        width=width,
        height=height,
        paper_bgcolor="#2f2f2f",   # deep gray outer background
        plot_bgcolor="#2f2f2f"     # deep gray inner background
    )

    return fig



import plotly.express as px

def visualize_report(
    report_df: pd.DataFrame,
    category: str,
    top_n: int = 10
):
    """
    Creates an interactive, colorful bar chart for a selected category.
    Returns Plotly Figure.
    """

    filtered_df = (
        report_df[report_df["Category"] == category]
        .sort_values("Count", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        filtered_df,
        x="Sub-Category",
        y="Count",
        color="Count",
        text="Count",
        color_continuous_scale=px.colors.sequential.Viridis,
        title=f"{category} — Top {top_n} Distribution",
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="",
        yaxis_title="Count",
        title_x=0.5,
        font=dict(size=14),
        height=500,
        margin=dict(l=40, r=40, t=60, b=80),
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=1.5
    )

    return fig









