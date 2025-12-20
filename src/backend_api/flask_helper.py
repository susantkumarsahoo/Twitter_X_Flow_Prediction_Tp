import os
import pandas as pd

def get_complaint_report(dataset_path: str) -> dict:
    """
    Generate a pivot report of complaints by department and status.

    Parameters
    ----------
    dataset_path : str
        Path to the dataset file (.xlsx)

    Returns
    -------
    dict
        Pivot table report in JSON format
    """
    try:
        if not os.path.exists(dataset_path):
            return {"error": f"Dataset file not found at {dataset_path}"}

        # Load dataset
        df = pd.read_excel(dataset_path)

        # Create pivot table
        pivot_df = pd.pivot_table(
            df,
            index="COMPLAINT TYPE",   # rows
            columns="DEPT",           # columns
            values="CLOSED/OPEN",     # values to aggregate
            aggfunc="count"           # aggregation function
        ).fillna(0)

        # Convert to JSON-friendly dict
        report = pivot_df.to_dict(orient="index")

        return {"report": report}

    except Exception as e:
        return {"error": f"Error generating report: {str(e)}"}
