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