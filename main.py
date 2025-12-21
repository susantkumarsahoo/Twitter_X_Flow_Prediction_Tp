from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

# -----------------------------------------------------------------------------
# Logger (single source of truth)
# -----------------------------------------------------------------------------
logger = get_logger(__name__)

# -----------------------------------------------------------------------------
# Imports with logging
# -----------------------------------------------------------------------------
try:
    from src.constants.paths import dataset_path
    from src.backend_api.fastapi_helper import (
        report_missing_values,
        get_dataset_info,
    )

    from src.visualization.figure_plot import (
        complaint_analysis_pie,
        
    )    
    logger.info("Custom FastAPI modules loaded successfully")
except ImportError as e:
    logger.warning("Import issue detected, using fallback dataset path", exc_info=True)
    dataset_path = "data/dataset.xlsx"

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Twitter Flow Analysis API",
    description="API for Twitter analytics and data visualization",
    version="1.0.0",
)

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Startup
# -----------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Starting Twitter Flow Analysis API")
    logger.info("=" * 60)

    if os.path.exists(dataset_path):
        logger.info("Dataset found | path=%s", dataset_path)
        try:
            df = pd.read_excel(dataset_path)
            logger.info(
                "Dataset loaded successfully | rows=%s cols=%s",
                df.shape[0],
                df.shape[1],
            )
        except Exception as e:
            logger.exception(
                "Failed to read dataset during startup"
            )
            raise CustomException(e)
    else:
        logger.warning("Dataset not found | path=%s", dataset_path)

    logger.info("=" * 60)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/")
def read_root():
    return {
        "message": "Twitter Flow Analysis API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "healthcheck": "/healthcheck",
            "report": "/report_missing_values",
            "docs": "/docs",
        },
    }


@app.get("/healthcheck")
def get_healthcheck():
    dataset_exists = os.path.exists(dataset_path)

    return {
        "status": "healthy" if dataset_exists else "degraded",
        "dataset_available": dataset_exists,
        "dataset_path": dataset_path,
    }


@app.get("/report_missing_values")
def get_report_missing_values():
    try:
        if not os.path.exists(dataset_path):
            logger.warning("Dataset missing | path=%s", dataset_path)
            raise HTTPException(
                status_code=404,
                detail="Dataset file not found",
            )

        logger.info("Generating missing values report")
        report = report_missing_values(dataset_path=dataset_path)
        logger.info("Missing values report generated successfully")

        return JSONResponse(content=report)

    except HTTPException:
        # Business / client error → FastAPI handles response
        raise

    except Exception as e:
        # System / unexpected error → wrap with CustomException
        logger.exception("Unhandled error while generating missing values report")
        raise CustomException(e)


@app.get("/read_dataset_info")
def geting_dataset_info():
    try:
        return get_dataset_info(dataset_path=dataset_path)
    except Exception as e:
        logger.exception("Failed to fetch dataset info")
        raise CustomException(e)
    
@app.get("/pie_chart")
def get_pie_chart():
    try:
        return complaint_analysis_pie(dataset_path=dataset_path)
    except Exception as e:
        logger.exception("Failed to fetch pie chart data")
        raise CustomException(e)


# -----------------------------------------------------------------------------
# Local run
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
