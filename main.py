from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
import logging
from pathlib import Path

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

# main.py
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from src.constants.paths import dataset_path
    from src.backend_api.fastapi_helper import report_missing_values, get_dataset_info
except ImportError as e:
    logger.warning(f"Import warning: {e}")
    # Fallback to relative imports if src module not found
    dataset_path = "data/dataset.xlsx"  # Update this path

# Initialize FastAPI
app = FastAPI(
    title="Twitter Flow Analysis API",
    description="API for Twitter analytics and data visualization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Check dataset availability on startup"""
    logger.info("="*60)
    logger.info("Starting Twitter Flow Analysis API")
    logger.info("="*60)
    
    if os.path.exists(dataset_path):
        logger.info(f"✓ Dataset found: {dataset_path}")
        try:
            df = pd.read_excel(dataset_path)
            logger.info(f"✓ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        except Exception as e:
            logger.error(f"✗ Error reading dataset: {e}")
    else:
        logger.warning(f"⚠ Dataset not found: {dataset_path}")
    
    logger.info("="*60)


@app.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "message": "Twitter Flow Analysis API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "healthcheck": "/healthcheck",
            "figure": "/figure_plt",
            "report": "/report_missing_values",
            "docs": "/docs"
        }
    }


@app.get("/healthcheck")
def get_healthcheck():
    """Health check endpoint"""
    dataset_exists = os.path.exists(dataset_path)
    
    return {
        "status": "healthy" if dataset_exists else "degraded",
        "message": "Twitter Flow Analysis API",
        "dataset_available": dataset_exists,
        "dataset_path": dataset_path
    }

@app.get("/report_missing_values")
def get_report_missing_values():
    """Get missing values report"""
    try:
        # Check if dataset exists
        if not os.path.exists(dataset_path):
            raise HTTPException(
                status_code=404,
                detail=f"Dataset file not found at: {dataset_path}"
            )
        
        # Generate report
        logger.info("Generating missing values report...")
        report = report_missing_values(dataset_path=dataset_path)
        logger.info("Report generated successfully")
        
        return JSONResponse(content=report)
    
    except FileNotFoundError as e:
        logger.error(f"Dataset not found: {e}")
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    



@app.get("/read_dataset_info")
def geting_dataset_info():
    return get_dataset_info(dataset_path=dataset_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")