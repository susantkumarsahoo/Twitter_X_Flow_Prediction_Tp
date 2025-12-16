"""
Energy Consumption Dashboard Demo
Minimal FastAPI + NiceGUI application with random energy data
"""

import random
from datetime import datetime, timedelta

import pandas as pd
from fastapi import FastAPI
from nicegui import ui

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(title="Energy Consumption Dashboard")

# -------------------------------------------------
# Data Generator
# -------------------------------------------------
def generate_energy_data(days: int = 30) -> pd.DataFrame:
    data = []
    base_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "total_consumption": round(random.uniform(15, 40), 2),
            "heating": round(random.uniform(5, 15), 2),
            "lighting": round(random.uniform(2, 8), 2),
            "appliances": round(random.uniform(3, 12), 2),
            "temperature": round(random.uniform(15, 30), 1),
            "cost": round(random.uniform(3, 12), 2),
        })

    return pd.DataFrame(data)

# -------------------------------------------------
# NiceGUI Page
# -------------------------------------------------
@ui.page("/")
def main_dashboard():
    df = generate_energy_data(30)

    with ui.header(elevated=True).classes("bg-blue-800 text-white"):
        ui.label("⚡ Energy Consumption Dashboard").classes("text-2xl font-bold")

    with ui.row().classes("w-full justify-center gap-4 p-4"):
        with ui.card().classes("w-48"):
            ui.label("Total Consumption")
            ui.label(f"{df['total_consumption'].sum():.1f} kWh").classes("text-xl")

        with ui.card().classes("w-48"):
            ui.label("Total Cost")
            ui.label(f"${df['cost'].sum():.1f}").classes("text-xl")

        with ui.card().classes("w-48"):
            ui.label("Daily Avg")
            ui.label(f"{df['total_consumption'].mean():.1f} kWh").classes("text-xl")




# -------------------------------------------------
# Mount NiceGUI on FastAPI
# -------------------------------------------------
ui.run_with(
    app,
    title="Energy Consumption Dashboard",
    favicon="⚡",
    dark=False,
)

# -------------------------------------------------
# Run App (CORRECT)
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "gui:app",
        host="127.0.0.1",
        port=8080,
        reload=False
    )
