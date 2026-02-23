import pandas as pd
import streamlit as st
import requests
import os
from typing import List, Dict


# ===============================
# CONFIG
# ===============================

DB_PATH = "db/FLAT_CMPL.txt"

HEADERS = {
    "User-Agent": "VehicleDefectAnalyzer/1.0",
    "Accept": "application/json"
}


# ===============================
# VIN DECODER
# ===============================

def decode_vin(vin: str) -> Dict | None:
    """
    Decode VIN using NHTSA vPIC API.
    """

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    data = response.json()
    results = data.get("Results", [])

    if not results:
        return None

    vehicle = results[0]

    make = vehicle.get("Make")
    model = vehicle.get("Model")
    year = vehicle.get("ModelYear")

    if not make or not year:
        return None

    return {
        "make": make.upper(),
        "model": model.upper() if model else "",
        "year": year,
    }


# ===============================
# LOAD COMPLAINT DATASET
# ===============================


@st.cache_data(show_spinner=True)
def load_complaints_dataset():
    return pd.read_parquet("db/complaints.parquet")

# ===============================
# FILTER COMPLAINTS
# ===============================

def get_complaints(make: str, model: str, year: str) -> List[Dict]:
    """
    Filter complaints locally from full flat file.
    """

    df = load_complaints_dataset()

    filtered = df[
        (df["MAKETXT"] == make.upper()) &
        (df["MODELTXT"] == model.upper()) &
        (df["YEARTXT"] == str(year))
    ]

    normalized = []

    for _, row in filtered.iterrows():
        normalized.append({
            "complaint_id": row.get("ODINO"),
            "date": row.get("FAILDATE"),
            "component": row.get("COMPDESC") or "UNKNOWN",
            "summary": row.get("CDESCR"),
            "state": row.get("STATE") or "UNKNOWN",
            "crash": 1 if row.get("CRASH") == "Y" else 0,
            "injury": int(row.get("INJURED") or 0),
            "fire": 1 if row.get("FIRE") == "Y" else 0,
            "death": int(row.get("DEATHS") or 0),
        })

    return normalized


# ===============================
# RECALLS FETCHER (API)
# ===============================

def get_recalls(make: str, model: str, year: str) -> List[Dict]:
    """
    Fetch recalls using NHTSA recallsByVehicle endpoint.
    """

    url = "https://api.nhtsa.gov/recalls/recallsByVehicle"

    params = {
        "make": make.upper(),
        "model": model.upper(),
        "modelYear": year
    }

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])