# analysis/wing_analysis.py

import numpy as np
import io
import matplotlib.patches as patches
import matplotlib.pyplot as plt

# ==================================================
# HELPERS TO READ AIRFOIL COORDS
# ==================================================

def get_airfoil_coords_from_string(data_str):
    with io.StringIO(data_str) as f:
        coords = np.loadtxt(f, skiprows=1)
    return coords


def get_airfoil_coords_from_file(path):
    return np.loadtxt(path)


# ==================================================
# CP / CoP HELPER
# ==================================================

def calculate_cop_location(cp_text):
    try:
        with io.StringIO(cp_text) as f:
            cp_table = np.loadtxt(f, skiprows=1)
    except Exception:
        return 0.25

    x_all = cp_table[:, 0]
    cp_all = cp_table[:, 1]

    le_index = np.argmin(x_all)

    x_upper_raw = x_all[:le_index + 1]
    cp_upper_raw = cp_all[:le_index + 1]

    x_lower_raw = x_all[le_index:]
    cp_lower_raw = cp_all[le_index:]

    upper_sort = np.argsort(x_upper_raw)
    lower_sort = np.argsort(x_lower_raw)

    x_upper = x_upper_raw[upper_sort]
    cp_upper = cp_upper_raw[upper_sort]

    x_lower = x_lower_raw[lower_sort]
    cp_lower = cp_lower_raw[lower_sort]

    x_common = np.linspace(0.0, 1.0, 200)

    cp_upper_interp = np.interp(x_common, x_upper, cp_upper)
    cp_lower_interp = np.interp(x_common, x_lower, cp_lower)

    delta_cp = cp_lower_interp - cp_upper_interp

    cl = np.trapz(delta_cp, x_common)
    cm_le = np.trapz(delta_cp * x_common, x_common)

    if cl == 0.0:
        return 0.25

    return cm_le / cl


# ==================================================
# AIRFOIL THICKNESS & CENTER
# ==================================================

def get_airfoil_thickness_and_center(coords, x_fraction, chord_length):
    x = coords[:, 0]
    y = coords[:, 1]

    current_chord = np.max(x)
    scale_factor = chord_length / current_chord

    x = x * scale_factor
    y = y * scale_factor

    le_index = np.argmin(x)

    x_upper = x[:le_index + 1]
    y_upper = y[:le_index + 1]

    x_lower = x[le_index:]
    y_lower = y[le_index:]

    u_sort = np.argsort(x_upper)
    l_sort = np.argsort(x_lower)

    x_upper = x_upper[u_sort]
    y_upper = y_upper[u_sort]

    x_lower = x_lower[l_sort]
    y_lower = y_lower[l_sort]

    target_x = x_fraction * chord_length

    y_u = np.interp(target_x, x_upper, y_upper)
    y_l = np.interp(target_x, x_lower, y_lower)

    thickness = y_u - y_l
    center_y = 0.5 * (y_u + y_l)

    return float(thickness), float(center_y)


# ==================================================
# CORE WING ANALYSIS (MDAO INTERFACE)
# ==================================================

def wing_spar_sizing(row, coords, cp_text=None):
    """
    row    : single aircraft row from dimensions CSV
    coords : airfoil coordinates (Nx2)
    """

    # ---- INPUTS FROM CSV ROW ----
    chord_mm = row["wing_rib_chord_mm"]
    span_mm = row["wing_span_mm"]

    chord_m = chord_mm / 1000.0
    span_m = span_mm / 1000.0

    # ---- CONSTANTS (LOCKED FOR NOW) ----
    ws_input = 45.38
    mor_MPa = 20.0
    fos = 3.0

    x1_frac = 0.25
    x2_frac = 0.65

    # ---- AIRFOIL GEOMETRY ----
    h1_mm, y1_center = get_airfoil_thickness_and_center(
        coords, x1_frac, chord_mm
    )
    h2_mm, y2_center = get_airfoil_thickness_and_center(
        coords, x2_frac, chord_mm
    )

    h1_m = h1_mm / 1000.0
    h2_m = h2_mm / 1000.0

    # ---- LOAD SHARING ----
    k1 = h1_m ** 3
    k2 = h2_m ** 3

    total_k = k1 + k2 if (k1 + k2) != 0.0 else 1.0

    r1 = k1 / total_k
    r2 = k2 / total_k

    area = chord_m * span_m
    arm = span_m / 4.0

    M_total = 0.5 * ws_input * area * arm

    M1 = M_total * r1
    M2 = M_total * r2

    # ---- STRENGTH ----
    sigma_allow = (mor_MPa * 1e6) / fos

    Y1 = h1_m / 2.0
    Y2 = h2_m / 2.0

    I1_req = (M1 * Y1) / sigma_allow
    I2_req = (M2 * Y2) / sigma_allow

    b1_mm = (12.0 * I1_req / (h1_m ** 3)) * 1000.0 if h1_m > 0.0 else 0.0
    b2_mm = (12.0 * I2_req / (h2_m ** 3)) * 1000.0 if h2_m > 0.0 else 0.0

    cop_frac = calculate_cop_location(cp_text) if cp_text else 0.25

    return {
        "chord_mm": chord_mm,
        "span_mm": span_mm,
        "h1_mm": h1_mm,
        "h2_mm": h2_mm,
        "b1_mm": b1_mm,
        "b2_mm": b2_mm,
        "M_total_Nm": M_total,
        "cop_frac": cop_frac
    }
