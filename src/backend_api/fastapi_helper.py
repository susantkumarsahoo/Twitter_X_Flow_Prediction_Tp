import pandas as pd
from typing import Dict, Any, List
import logging
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
logger = logging.getLogger(__name__)


def report_missing_values(dataset_path: str) -> Dict[str, Any]:
    """
    Generate a comprehensive report of missing values in the dataset.

    Parameters
    ----------
    dataset_path : str
        Path to the dataset file (Excel)

    Returns
    -------
    Dict[str, Any]
        JSON-serializable report containing missing value statistics
    """
    
    try:
        # Read dataset
        logger.info(f"Reading dataset from: {dataset_path}")
        df = pd.read_excel(dataset_path)
        logger.info(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        total_rows = len(df)
        total_columns = df.shape[1]
        total_cells = total_rows * total_columns
        
        # Calculate missing values
        missing_count = df.isnull().sum()
        missing_percent = (missing_count / total_rows) * 100
        
        # Build report dataframe
        report_df = pd.DataFrame({
            "column": missing_count.index,
            "missing_count": missing_count.values,
            "missing_percentage": missing_percent.values.round(2)
        })
        
        # Filter only columns with missing values
        report_df = report_df[report_df["missing_count"] > 0]
        
        # Sort by missing count (descending)
        report_df = report_df.sort_values("missing_count", ascending=False)
        
        # Convert to records for JSON serialization
        missing_summary = report_df.to_dict(orient="records")
        
        # Calculate totals
        total_missing = int(missing_count.sum())
        missing_percentage_total = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0
        
        # Identify severity categories
        severity_summary = {
            "critical": len(report_df[report_df["missing_percentage"] >= 50]),  # >= 50%
            "high": len(report_df[(report_df["missing_percentage"] >= 25) & (report_df["missing_percentage"] < 50)]),  # 25-49%
            "medium": len(report_df[(report_df["missing_percentage"] >= 10) & (report_df["missing_percentage"] < 25)]),  # 10-24%
            "low": len(report_df[report_df["missing_percentage"] < 10])  # < 10%
        }
        
        # Build final report
        report = {
            "dataset_path": dataset_path,
            "total_rows": int(total_rows),
            "total_columns": int(total_columns),
            "total_cells": int(total_cells),
            "total_missing_values": total_missing,
            "overall_missing_percentage": missing_percentage_total,
            "columns_with_missing_values": int(len(report_df)),
            "columns_without_missing_values": int(total_columns - len(report_df)),
            "severity_summary": severity_summary,
            "missing_values_summary": missing_summary,
            "recommendations": generate_recommendations(report_df, total_rows)
        }
        
        logger.info("Report generated successfully")
        return report
    
    except FileNotFoundError as e:
        logger.error(f"Dataset file not found: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise


def generate_recommendations(report_df: pd.DataFrame, total_rows: int) -> List[str]:
    """
    Generate recommendations based on missing values analysis.
    
    Parameters
    ----------
    report_df : pd.DataFrame
        DataFrame containing missing values analysis
    total_rows : int
        Total number of rows in dataset
    
    Returns
    -------
    List[str]
        List of recommendations
    """
    recommendations = []
    
    if report_df.empty:
        recommendations.append("✅ No missing values detected. Dataset is complete.")
        return recommendations
    
    # Check for critical columns
    critical_cols = report_df[report_df["missing_percentage"] >= 50]
    if not critical_cols.empty:
        recommendations.append(
            f"⚠️ CRITICAL: {len(critical_cols)} column(s) have ≥50% missing values. "
            f"Consider dropping these columns: {', '.join(critical_cols['column'].tolist())}"
        )
    
    # Check for high missing columns
    high_cols = report_df[(report_df["missing_percentage"] >= 25) & (report_df["missing_percentage"] < 50)]
    if not high_cols.empty:
        recommendations.append(
            f"⚠️ HIGH: {len(high_cols)} column(s) have 25-50% missing values. "
            f"Consider imputation or feature engineering."
        )
    
    # Check for medium missing columns
    medium_cols = report_df[(report_df["missing_percentage"] >= 10) & (report_df["missing_percentage"] < 25)]
    if not medium_cols.empty:
        recommendations.append(
            f"ℹ️ MEDIUM: {len(medium_cols)} column(s) have 10-25% missing values. "
            f"Standard imputation techniques recommended."
        )
    
    # Check for low missing columns
    low_cols = report_df[report_df["missing_percentage"] < 10]
    if not low_cols.empty:
        recommendations.append(
            f"✓ LOW: {len(low_cols)} column(s) have <10% missing values. "
            f"Simple imputation or row deletion may be sufficient."
        )
    
    # General recommendations
    if len(report_df) > 0:
        recommendations.append(
            "💡 Recommended actions: "
            "1) Analyze patterns in missing data, "
            "2) Determine if data is MCAR, MAR, or MNAR, "
            "3) Choose appropriate imputation strategy"
        )
    
    return recommendations



import os
import pandas as pd

def get_dataset_info(dataset_path: str) -> dict:
    """
    Get basic dataset information from an Excel file.

    Parameters
    ----------
    dataset_path : str
        Path to the dataset file (.xlsx)

    Returns
    -------
    dict
        Dictionary containing dataset details
    """
    try:
        if not os.path.exists(dataset_path):
            return {"error": f"Dataset file not found at {dataset_path}"}
        
        df = pd.read_excel(dataset_path)

        return {
            "dataset_path": dataset_path,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }

    except Exception as e:
        return {"error": f"Error reading dataset: {str(e)}"}
