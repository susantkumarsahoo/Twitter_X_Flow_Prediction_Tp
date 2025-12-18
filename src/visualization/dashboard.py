import pandas as pd
import plotly.express as px
from typing import Optional
from plotly.graph_objs import Figure

# src/visualization/dashboard.py

def plot_missing_values(
    dataset_path: str,
    title: str = "Missing Values per Column",
    height: int = 600,
    width: int = 1200,
) -> Optional[Figure]:
    """
    Reads a dataset from the given path and plots missing values per column.

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
        Plotly figure if missing values exist, otherwise None.
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

    # Create bar chart
    fig = px.bar(
        null_data,
        x="Column",
        y="Missing Values",
        title=title,
        text="Missing Values",
        color="Missing Values",
        color_continuous_scale="Blues",
    )

    # Show values on bars
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside"
    )

    # Improve layout
    fig.update_layout(
        xaxis_title="Columns",
        yaxis_title="Count of Missing Values",
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        height=height,
        width=width,
        showlegend=False,
    )

    return fig

