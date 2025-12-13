from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate data once at startup
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
df = pd.DataFrame({
    'date': dates,
    'sales': np.random.randint(100, 1000, 100),
    'category': np.random.choice(['Electronics', 'Clothing', 'Food'], 100)
})

# Pre-calculate summary and category stats
SUMMARY = {
    "total_sales": int(df['sales'].sum()),
    "avg_sales": float(df['sales'].mean()),
    "max_sales": int(df['sales'].max()),
    "min_sales": int(df['sales'].min())
}

CATEGORY_STATS = df.groupby('category')['sales'].sum().to_dict()

# Convert df to dict once
DATA = df.to_dict(orient='records')

@app.get("/")
def read_root():
    return {"message": "Sales Analysis API", "status": "running"}

@app.get("/data")
def get_data():
    return DATA

@app.get("/summary")
def get_summary():
    return SUMMARY

@app.get("/category-stats")
def get_category_stats():
    return CATEGORY_STATS