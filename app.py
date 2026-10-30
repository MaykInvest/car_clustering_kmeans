# ============================================================
# 🚗 CAR MARKET SEGMENTATION API
# ============================================================
# Serves the K-Means model exported by project.ipynb.
# Run with:  uvicorn app:app --reload

from typing import Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

# --- Load the exported bundle once, at startup ---
bundle        = joblib.load("car_clustering_model.pkl")
preprocessor  = bundle["preprocessor"]
kmeans        = bundle["kmeans_model"]
cluster_names = bundle["cluster_names"]

app = FastAPI(
    title="Car Market Segmentation API",
    description="Assigns a car to one of 3 market segments found by K-Means clustering.",
)


# --- Input schema: only values the model saw during training are accepted ---
class Car(BaseModel):
    year: int = Field(..., ge=1990, le=2017, examples=[2015])
    engine_hp: float | None = Field(None, gt=0, examples=[180])
    engine_cylinders: float | None = Field(None, gt=0, examples=[4])
    number_of_doors: float | None = Field(None, examples=[4])
    highway_mpg: float = Field(..., gt=0, lt=100, examples=[34])
    city_mpg: float = Field(..., gt=0, lt=100, examples=[25])
    msrp: float = Field(..., gt=0, lt=500000, examples=[24000])
    engine_fuel_type: Literal[
        'diesel', 'flex-fuel (premium unleaded recommended/E85)',
        'flex-fuel (premium unleaded required/E85)', 'flex-fuel (unleaded/E85)',
        'flex-fuel (unleaded/natural gas)', 'natural gas',
        'premium unleaded (recommended)', 'premium unleaded (required)',
        'regular unleaded'] | None = Field(None, examples=['regular unleaded'])
    transmission_type: Literal[
        'AUTOMATED_MANUAL', 'AUTOMATIC', 'DIRECT_DRIVE', 'MANUAL', 'UNKNOWN'] = Field(..., examples=['AUTOMATIC'])
    driven_wheels: Literal[
        'all wheel drive', 'four wheel drive', 'front wheel drive', 'rear wheel drive'] = Field(..., examples=['front wheel drive'])
    vehicle_size: Literal['Compact', 'Large', 'Midsize'] = Field(..., examples=['Midsize'])
    vehicle_style: Literal[
        '2dr Hatchback', '2dr SUV', '4dr Hatchback', '4dr SUV', 'Cargo Minivan',
        'Cargo Van', 'Convertible', 'Convertible SUV', 'Coupe', 'Crew Cab Pickup',
        'Extended Cab Pickup', 'Passenger Minivan', 'Passenger Van',
        'Regular Cab Pickup', 'Sedan', 'Wagon'] = Field(..., examples=['Sedan'])


@app.get("/")
def health():
    return {"status": "ok", "segments": list(cluster_names.values())}


@app.post("/segment")
def segment(car: Car):
    df = pd.DataFrame([car.model_dump()])
    df["log_msrp"] = np.log1p(df["msrp"])  # same transform as the notebook

    X         = preprocessor.transform(df)
    cluster   = int(kmeans.predict(X)[0])
    distances = kmeans.transform(X)[0]  # smaller = more typical of that segment

    return {
        "cluster": cluster,
        "segment": cluster_names[cluster],
        "distance_to_each_segment": {
            cluster_names[i]: round(float(d), 3) for i, d in enumerate(distances)
        },
    }
