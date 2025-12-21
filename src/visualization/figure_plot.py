import pandas as pd
import plotly.express as px
from typing import Optional
from plotly.graph_objs import Figure
import logging

import pandas as pd
import matplotlib.pyplot as plt



def complaint_analysis_pie(datapath):
    """
    Reads complaint data from a CSV file and returns data for pie charts:
    1. Complaints per Department
    2. Complaints per Year
    3. Closed vs Open Complaints (All Years Combined)
    
    Parameters:
        datapath (str): Path to the CSV file containing columns
                        ['DATE','COMPLAINT TYPE','DEPT','CLOSED/OPEN']
    Returns:
        dict: Dictionary containing data for three pie charts
    """
    # --- Step 1: Load Data ---
    df = pd.read_csv(datapath)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year

    # --- Step 2: Summaries ---
    dept_summary = df.groupby('DEPT').size().reset_index(name='TOTAL_COMPLAINTS')
    yearly_counts = df.groupby('YEAR').size().reset_index(name='TOTAL_COMPLAINTS')
    status_summary = df.groupby(['YEAR','CLOSED/OPEN']).size().reset_index(name='COUNT')
    status_total = status_summary.groupby('CLOSED/OPEN')['COUNT'].sum().reset_index()

    # --- Step 3: Return JSON-serializable data ---
    return {
        "department_chart": {
            "labels": dept_summary['DEPT'].tolist(),
            "values": dept_summary['TOTAL_COMPLAINTS'].tolist()
        },
        "yearly_chart": {
            "labels": [str(year) for year in yearly_counts['YEAR'].tolist()],
            "values": yearly_counts['TOTAL_COMPLAINTS'].tolist()
        },
        "status_chart": {
            "labels": status_total['CLOSED/OPEN'].tolist(),
            "values": status_total['COUNT'].tolist()
        }
    }

def analysis_pie(datapath):
    """
    Reads complaint data from a CSV file and generates pie charts:
    1. Complaints per Department
    2. Complaints per Year
    3. Closed vs Open Complaints (All Years Combined)
    
    Parameters:
        datapath (str): Path to the CSV file containing columns
                        ['DATE','COMPLAINT TYPE','DEPT','CLOSED/OPEN']
    Returns:
        None (displays plots)
    """
    # --- Step 1: Load Data ---
    df = pd.read_csv(datapath)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year

    # --- Step 2: Summaries ---
    dept_summary = df.groupby('DEPT').size().reset_index(name='TOTAL_COMPLAINTS')
    yearly_counts = df.groupby('YEAR').size().reset_index(name='TOTAL_COMPLAINTS')
    status_summary = df.groupby(['YEAR','CLOSED/OPEN']).size().reset_index(name='COUNT')
    status_total = status_summary.groupby('CLOSED/OPEN')['COUNT'].sum().reset_index()

    # --- Step 3: Combined Pie Charts ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. Complaints per Department
    axes[0].pie(
        dept_summary['TOTAL_COMPLAINTS'],
        labels=dept_summary['DEPT'],
        autopct='%1.1f%%',
        startangle=90
    )
    axes[0].set_title("Complaints per Department")

    # 2. Complaints per Year
    axes[1].pie(
        yearly_counts['TOTAL_COMPLAINTS'],
        labels=yearly_counts['YEAR'],
        autopct='%1.1f%%',
        startangle=90
    )
    axes[1].set_title("Complaints per Year")

    # 3. Closed vs Open Complaints (All Years Combined)
    axes[2].pie(
        status_total['COUNT'],
        labels=status_total['CLOSED/OPEN'],
        autopct='%1.1f%%',
        startangle=90,
        colors=['orange','blue']
    )
    axes[2].set_title("Closed vs Open Complaints (All Years)")

    plt.tight_layout()
    plt.show()

