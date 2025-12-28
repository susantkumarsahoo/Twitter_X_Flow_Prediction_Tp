import os
import pandas as pd
import numpy as np
import sys

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

logger = get_logger(__name__)

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
        logger.error(f"Error generating missing values report: {str(e)}", exc_info=True)
        raise CustomException(e, sys) from e


import pandas as pd
from typing import List, Dict, Optional

def apply_pivot_examples(dataset_path: str) -> pd.DataFrame:
    # Load dataset
    df = pd.read_excel(dataset_path)

    # Ensure required columns exist
    required = ['COMPLAINT TYPE', 'DEPT', 'CLOSED/OPEN']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Work on a copy and clean text
    d = df[required].copy()

    # Normalize strings: strip, lower, then title-case
    def norm(s: Optional[str]) -> str:
        if pd.isna(s):
            return '(blank)'
        s = str(s).strip()
        return '(blank)' if s == '' else s

    d['COMPLAINT TYPE'] = d['COMPLAINT TYPE'].map(norm)
    d['DEPT'] = d['DEPT'].map(norm)
    d['CLOSED/OPEN'] = d['CLOSED/OPEN'].map(norm)

    # Optional: unify common variants in complaint types
    # Map variations to a single canonical form
    type_map: Dict[str, str] = {
        'Civil Works': 'Civil works',
        'NO Power Supply': 'No Power Supply',
        'Pole Shifting / Lt Sagging': 'Pole Shifting / Lt Sagging',
        'Transformer Failure / NCC': 'Transformer failure / NCC',
    }
    d['COMPLAINT TYPE'] = d['COMPLAINT TYPE'].replace(type_map)

    # Normalize DEPT values to desired set
    dept_map: Dict[str, str] = {
        'Commercial': 'Commercial',
        'O&M': 'O&M',
        'Operation & Maintenance': 'O&M',
        'Other': 'Other',
        'Others': 'Other',
        '(blank)': '(blank)',
    }
    d['DEPT'] = d['DEPT'].map(lambda x: dept_map.get(x, x))

    # Normalize CLOSED/OPEN values to exactly CLOSED / OPEN
    status_map: Dict[str, str] = {
        'Closed': 'CLOSED',
        'closed': 'CLOSED',
        'OPEN': 'OPEN',
        'Open': 'OPEN',
        'open': 'OPEN',
        '(blank)': '(blank)',
    }
    d['CLOSED/OPEN'] = d['CLOSED/OPEN'].map(lambda x: status_map.get(x, x))

    # Build pivot with counts using size (do not set `values`)
    pivot = d.pivot_table(
        index='COMPLAINT TYPE',
        columns=['DEPT', 'CLOSED/OPEN'],
        aggfunc='size',
        fill_value=0
    )

    # Ensure consistent column order
    desired_depts: List[str] = ['Commercial', 'O&M', 'Other', '(blank)']
    desired_status: List[str] = ['CLOSED', 'OPEN']
    # Reindex columns to the desired multi-index order, keep missing combinations as 0
    pivot = pivot.reindex(
        pd.MultiIndex.from_product([desired_depts, desired_status], names=pivot.columns.names),
        axis=1,
        fill_value=0
    )

    # Add per-department TOTAL columns
    for dept in desired_depts:
        closed_col = (dept, 'CLOSED')
        open_col = (dept, 'OPEN')
        total_series = pivot.get(closed_col, 0) + pivot.get(open_col, 0)
        pivot[(dept, 'TOTAL')] = total_series

    # Add GRAND TOTAL across department TOTALs
    total_cols = [(dept, 'TOTAL') for dept in desired_depts]
    pivot[('Grand', 'TOTAL')] = pivot[total_cols].sum(axis=1)

    # Sort rows alphabetically (optional: or by Grand TOTAL descending)
    # pivot = pivot.sort_values(('Grand', 'TOTAL'), ascending=False)

    # Flatten columns to match your readability preference
    pivot.columns = [f"{lvl0} {lvl1}".strip() for lvl0, lvl1 in pivot.columns]

    # Reset index to have COMPLAINT TYPE as a column
    pivot = pivot.reset_index()

    return pivot


import pandas as pd

def all_data_generate_report(dataset_path) -> None:
    """
    Generates a standardized summary report with filters and totals.
    Output format:
    Category | Sub-Category | Count
    """
    df = pd.read_excel(dataset_path)
    report_blocks = []

    def add_counts(category_name, series):
        temp = series.reset_index()
        temp.columns = ["Sub-Category", "Count"]
        temp["Category"] = category_name
        report_blocks.append(temp)

    # Basic value counts
    add_counts("SHIFT DUTY", df["SHIFT DUTY"].value_counts())
    add_counts("QUERY/REQUEST/COMPLAINT", df["QUERY/REQUEST/COMPLAINT"].value_counts())
    add_counts("DIVISION", df["DIVISION"].value_counts())
    add_counts("CIRCLE", df["CIRCLE"].value_counts())
    add_counts("DEPT", df["DEPT"].value_counts())
    add_counts("CLOSED/OPEN", df["CLOSED/OPEN"].value_counts())

    add_counts(
        "TWEET-LINK SUMMARY",
        pd.Series({
            "Total": df["TWEET-LINK"].count(),
            "DM": df.loc[df["TWEET-LINK"] == "DM", "TWEET-LINK"].count(),
            "Non-DM": df.loc[df["TWEET-LINK"] != "DM", "TWEET-LINK"].count()
        })
    )

    # Filtered counts
    add_counts("SECTION", df["SECTION"].value_counts()[lambda x: x >= 10])
    add_counts("SUB-DIVISION", df["SUB-DIVISION"].value_counts()[lambda x: x >= 5])
    add_counts("COMPLAINANT NAME", df["COMPLAINANT NAME"].value_counts()[lambda x: x >= 20])

    # Totals
    totals = pd.DataFrame({
        "Category": [
            "COMPLAINT NUMBER (Total)",
            "CONSUMER NUMBER (Total)",
            "MOBILE NUMB (Total)"
        ],
        "Sub-Category": ["Total", "Total", "Total"],
        "Count": [
            df["COMPLAINT NUMBER"].count(),
            df["CONSUMER NUMBER"].count(),
            df["MOBILE NUMB"].count()
        ]
    })

    final_report = pd.concat(report_blocks + [totals], ignore_index=True)
    return final_report




