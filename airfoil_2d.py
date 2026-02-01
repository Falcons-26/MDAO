import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "polars")

def _read_polar(airfoil, Re):
    path = os.path.join(DATA_DIR, f"{airfoil}_{Re}.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def _extract_features(df):
    alpha = df["alpha"].values
    cl = df["cl"].values
    cd = df["cd"].values

    # ---- Linear lift region fit ----
    mask = (alpha > -4) & (alpha < 6)
    m, b = np.polyfit(alpha[mask], cl[mask], 1)
    alpha_0 = -b / m

    # ---- Cd0 at Cl ≈ 0 ----
    idx0 = np.argmin(np.abs(cl))
    Cd0 = cd[idx0]

    # ---- Drag polar fit ----
    k, _ = np.polyfit(cl**2, cd - Cd0, 1)

    # ---- Stall ----
    i = np.argmax(cl)
    Cl_max = cl[i]

    return {
        "Cl_alpha": m,
        "alpha_0": alpha_0,
        "Cd0": Cd0,
        "k": k,
        "Cl_max_2d": Cl_max
    }

def airfoil_2d_features(airfoil, Re):
    f150 = _extract_features(_read_polar(airfoil, 150))
    f250 = _extract_features(_read_polar(airfoil, 250))

    w = (np.log(Re) - np.log(150_000)) / (np.log(250_000) - np.log(150_000))
    w = np.clip(w, 0.0, 1.0)

    return {
        k: (1 - w) * f150[k] + w * f250[k]
        for k in f150
    }
