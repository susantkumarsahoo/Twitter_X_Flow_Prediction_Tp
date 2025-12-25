import sys
import pandas as pd
from typing import Dict, Any, List
import logging
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.constants.paths import dataset_path


logger = get_logger(__name__)



import pandas as pd
from typing import Dict, Any, List

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

logger = get_logger(__name__)


def report_missing_values(dataset_path: str) -> Dict[str, Any]:
    """
    Generate a comprehensive report of missing values in the dataset.
    """
    try:
        logger.info("Reading dataset | path=%s", dataset_path)
        df = pd.read_excel(dataset_path)

        logger.info(
            "Dataset loaded successfully | rows=%s cols=%s",
            df.shape[0],
            df.shape[1],
        )

        total_rows = len(df)
        total_columns = df.shape[1]
        total_cells = total_rows * total_columns

        missing_count = df.isnull().sum()
        missing_percent = (missing_count / total_rows) * 100

        report_df = pd.DataFrame(
            {
                "column": missing_count.index,
                "missing_count": missing_count.values,
                "missing_percentage": missing_percent.values.round(2),
            }
        )

        report_df = report_df[report_df["missing_count"] > 0]
        report_df = report_df.sort_values("missing_count", ascending=False)

        missing_summary = report_df.to_dict(orient="records")

        total_missing = int(missing_count.sum())
        overall_missing_pct = (
            round((total_missing / total_cells) * 100, 2)
            if total_cells > 0
            else 0
        )

        severity_summary = {
            "critical": int((report_df["missing_percentage"] >= 50).sum()),
            "high": int(
                ((report_df["missing_percentage"] >= 25)
                 & (report_df["missing_percentage"] < 50)).sum()
            ),
            "medium": int(
                ((report_df["missing_percentage"] >= 10)
                 & (report_df["missing_percentage"] < 25)).sum()
            ),
            "low": int((report_df["missing_percentage"] < 10).sum()),
        }

        report = {
            "dataset_path": dataset_path,
            "total_rows": int(total_rows),
            "total_columns": int(total_columns),
            "total_cells": int(total_cells),
            "total_missing_values": total_missing,
            "overall_missing_percentage": overall_missing_pct,
            "columns_with_missing_values": int(len(report_df)),
            "columns_without_missing_values": int(total_columns - len(report_df)),
            "severity_summary": severity_summary,
            "missing_values_summary": missing_summary,
            "recommendations": generate_recommendations(report_df),
        }

        logger.info("Missing values report generated successfully")
        return report

    except FileNotFoundError:
        logger.warning("Dataset file not found | path=%s", dataset_path)
        raise

    except Exception as e:
        logger.error(
            f"Error generating missing values report: {str(e)}",exc_info=True)
        raise CustomException(e, sys) from e


def generate_recommendations(report_df: pd.DataFrame) -> List[str]:
    """
    Generate recommendations based on missing values analysis.
    """
    recommendations = []

    if report_df.empty:
        return ["✅ No missing values detected. Dataset is complete."]

    critical = report_df[report_df["missing_percentage"] >= 50]
    high = report_df[(report_df["missing_percentage"] >= 25) & (report_df["missing_percentage"] < 50)]
    medium = report_df[(report_df["missing_percentage"] >= 10) & (report_df["missing_percentage"] < 25)]
    low = report_df[report_df["missing_percentage"] < 10]

    if not critical.empty:
        recommendations.append(
            f"⚠️ CRITICAL: {len(critical)} column(s) have ≥50% missing values. "
            f"Consider dropping: {', '.join(critical['column'])}"
        )

    if not high.empty:
        recommendations.append(
            f"⚠️ HIGH: {len(high)} column(s) have 25–50% missing values. "
            f"Consider imputation or feature engineering."
        )

    if not medium.empty:
        recommendations.append(
            f"ℹ️ MEDIUM: {len(medium)} column(s) have 10–25% missing values. "
            f"Standard imputation recommended."
        )

    if not low.empty:
        recommendations.append(
            f"✓ LOW: {len(low)} column(s) have <10% missing values. "
            f"Simple imputation or row deletion may be sufficient."
        )

    recommendations.append(
        "💡 Recommended actions: analyze missingness patterns (MCAR/MAR/MNAR) "
        "and apply an appropriate imputation strategy."
    )

    return recommendations


import os
import pandas as pd


def get_dataset_info(dataset_path: str) -> dict:
    """
    Get basic dataset information from an Excel file.
    """
    if not os.path.exists(dataset_path):
        logger.warning("Dataset file not found | path=%s", dataset_path)
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    try:
        df = pd.read_excel(dataset_path)
        
        logger.info(
            "Dataset info retrieved | rows=%s cols=%s",
            df.shape[0],
            df.shape[1],
        )

        return {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": df.columns.tolist(),
        }
    
    except Exception as e:
        logger.error(
            f"Error retrieving dataset info: {str(e)}",exc_info=True)
        raise CustomException(e, sys) from e
    




import pandas as pd

def get_complaint_report(datapath, column_name='COMPLAINT TYPE'):
    """
    Loads a CSV from datapath and returns value counts for a specific column.
    """
    # Load the data from the provided path
    df = pd.read_excel(datapath)
    
    # Return the frequency of unique values in the column
    return df[column_name].value_counts()