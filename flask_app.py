import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

# flask_app.py

# Try to import custom modules
try:
    from src.constants.paths import dataset_path
    from src.backend_api.flask_helper import get_complaint_report
    CUSTOM_IMPORTS = True
except ImportError:
    print("⚠️ Warning: Custom modules not found, using fallback")
    dataset_path = "data/dataset.xlsx"
    CUSTOM_IMPORTS = False
    

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """Root endpoint"""
    return jsonify({
        "message": "Flask API for Twitter Analytics",
        "version": "1.0.0",
        "endpoints": {
            "complaint_report": "/complaint_report"
        },
        "custom_modules_loaded": CUSTOM_IMPORTS
    })


@app.route("/complaint_report", methods=["GET"])
def complaint_report():
    """
    Endpoint to return complaint pivot report.
    """
    try:
        # Allow overriding dataset path via query param (optional)
        data_path = request.args.get("dataset_path", dataset_path)

        report = get_complaint_report(data_path)
        return jsonify(report)

    except FileNotFoundError:
        return jsonify({
            "error": "Dataset file not found",
            "path": data_path
        }), 404

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("="*60)
    print("Starting Flask API Server")
    print("="*60)
    print(f"Dataset path: {dataset_path}")
    print(f"Custom modules loaded: {CUSTOM_IMPORTS}")
    print("="*60)
    app.run(debug=True, host="0.0.0.0", port=5000)
