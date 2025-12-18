from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from src.constants.paths import dataset_path
from src.visualization.dashboard import plot_missing_values
import json

# main.py
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Twitter Flow Analysis API", "status": "running"}

@app.get("/figure_plt")
def get_dashboard():
    fig = plot_missing_values(dataset_path=dataset_path)
    return fig

@app.get("/healthcheck")
def get_healthcheck():
    return {"message": "Twitter Flow Analysis API", "status": "running"}