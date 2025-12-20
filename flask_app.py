import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from src.constants.paths import dataset_path
from src.backend_api.flask_helper import get_complaint_report

app = Flask(__name__)


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
            "error": "Dataset file not found"
        }), 404

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

