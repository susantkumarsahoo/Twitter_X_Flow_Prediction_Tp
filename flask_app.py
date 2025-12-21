import pandas as pd
import numpy as np
from flask import Flask, jsonify, request

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
logger = get_logger(__name__)

# -----------------------------------------------------------------------------
# Try to import custom modules
# -----------------------------------------------------------------------------
try:
    from src.constants.paths import dataset_path
    from src.backend_api.flask_helper import get_complaint_report
    CUSTOM_IMPORTS = True
    logger.info("Custom Flask modules loaded successfully")
except ImportError as e:
    logger.warning(
        "Custom modules not found, using fallback configuration",
        exc_info=True,
    )
    dataset_path = "data/dataset.xlsx"
    CUSTOM_IMPORTS = False

# -----------------------------------------------------------------------------
# Flask App
# -----------------------------------------------------------------------------
app = Flask(__name__)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    logger.info("Health check endpoint hit (Flask)")
    return jsonify(
        {
            "message": "Flask API for Twitter Analytics",
            "version": "1.0.0",
            "endpoints": {
                "complaint_report": "/complaint_report",
            },
            "custom_modules_loaded": CUSTOM_IMPORTS,
        }
    )


@app.route("/complaint_report", methods=["GET"])
def complaint_report():
    """
    Endpoint to return complaint pivot report.
    """
    try:
        data_path = request.args.get("dataset_path", dataset_path)
        logger.info("Generating complaint report | path=%s", data_path)

        report = get_complaint_report(data_path)

        logger.info("Complaint report generated successfully")
        return jsonify(report)

    except FileNotFoundError:
        logger.warning("Dataset file not found | path=%s", data_path)
        return (
            jsonify(
                {
                    "error": "Dataset file not found",
                    "path": data_path,
                }
            ),
            404,
        )

    except Exception as e:
        logger.exception("Unhandled error while generating complaint report")
        raise CustomException(e)


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Flask API Server")
    logger.info("Dataset path: %s", dataset_path)
    logger.info("Custom modules loaded: %s", CUSTOM_IMPORTS)
    logger.info("=" * 60)

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
    )

