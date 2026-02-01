import pandas as pd
import os
import numpy as np

# ------------------ Macaulay bending moment ------------------
def macaulay_bending_moment(point_loads, x):
    Mx = 0.0
    for P, a in point_loads:
        if x >= a:
            Mx += P * (x - a)
    return Mx


# ------------------ MOI sweep function ------------------
def sweep_centroid_inertia(h, w, tw, rt, x_bot, k_min, step, k_max_override=None):
    k_list = []
    centroid_list = []
    inertia_list = []

    A_f = w * tw
    y_f = tw / 2.0

    if k_max_override is not None:
        k_upper = float(k_max_override)
    else:
        k_upper = h / 2.0

    k_upper = min(k_upper, h / 2.0)

    if k_upper < k_min:
        return k_list, centroid_list, inertia_list

    k = float(k_min)
    eps = 1e-9

    while k <= k_upper + eps:
        A_b = 2.0 * rt * x_bot
        A_t = 2.0 * rt * k
        A_tot = A_f + A_b + A_t

        y_b = tw + x_bot / 2.0
        y_t = h - k / 2.0

        ybar = (A_f * y_f + A_b * y_b + A_t * y_t) / A_tot

        I_flange_cent = (w * tw**3) / 12.0
        I_flange = I_flange_cent + A_f * (ybar - y_f)**2

        I_strips_cent = (rt / 6.0) * (x_bot**3 + k**3)
        PA_strips = 2.0 * rt * (
            x_bot * (y_b - ybar)**2 +
            k * (y_t - ybar)**2
        )

        I_total = I_flange + I_strips_cent + PA_strips

        k_list.append(k)
        centroid_list.append(ybar)
        inertia_list.append(I_total)

        k += step

    return k_list, centroid_list, inertia_list


# ------------------ MAIN ANALYSIS ------------------
def fuselage_moi_analysis(
    airfoil_csv,
    baseplate_gap,
    w, tw, rt, x_bot,
    k_min, step,
    point_loads,
    output_csv="results_moi_with_M.csv"
):
    if not os.path.exists(airfoil_csv):
        raise FileNotFoundError("Airfoil file not found")

    df_raw = pd.read_csv(
        airfoil_csv,
        sep=r"\s+|,",
        header=None,
        usecols=[0, 1],
        engine="python"
    )
    df_raw.columns = ["x", "y"]

    df_raw["x"] = pd.to_numeric(df_raw["x"], errors="coerce")
    df_raw["y"] = pd.to_numeric(df_raw["y"], errors="coerce")
    df_raw = df_raw.dropna().reset_index(drop=True)

    air_x = df_raw["x"].values
    air_y = df_raw["y"].values

    forward_end = len(air_x)
    for i in range(1, len(air_x)):
        if air_x[i] >= air_x[i - 1]:
            forward_end = i
            break

    upper = df_raw.iloc[:forward_end].copy().reset_index(drop=True)
    lower = df_raw.iloc[forward_end:].copy().reset_index(drop=True)

    if upper["x"].iloc[0] > upper["x"].iloc[-1]:
        upper = upper.iloc[::-1].reset_index(drop=True)
    if lower["x"].iloc[0] > lower["x"].iloc[-1]:
        lower = lower.iloc[::-1].reset_index(drop=True)

    xp_upper, fp_upper = upper["x"].values, upper["y"].values
    xp_lower, fp_lower = lower["x"].values, lower["y"].values

    def y_top_at(xq):
        return float(np.interp(xq, xp_upper, fp_upper))

    results = []

    fixed_x = float(df_raw["x"].min())

    for _, row in upper.iterrows():
        x_val = float(row["x"])
        y_top = float(row["y"])

        idx = int(np.argmin(np.abs(xp_lower - x_val)))
        y_bot = float(fp_lower[idx])

        thickness = abs(y_top) + abs(y_bot)
        baseplate_line = y_bot + baseplate_gap
        h_eff = y_top - baseplate_line

        if h_eff <= 0:
            continue

        dist = max(0.0, x_val - fixed_x)
        M_val = macaulay_bending_moment(point_loads, dist)

        local_k_max = h_eff - (tw + x_bot)
        if local_k_max < k_min:
            continue

        k_vals, centroids, inertias = sweep_centroid_inertia(
            h_eff, w, tw, rt, x_bot,
            k_min, step,
            k_max_override=local_k_max
        )

        for k, ybar, I in zip(k_vals, centroids, inertias):
            results.append({
                "x": x_val,
                "y_top": y_top,
                "y_bottom": y_bot,
                "h_eff": h_eff,
                "k": k,
                "centroid": ybar,
                "I": I,
                "M": M_val,
                "baseplate_line": baseplate_line
            })

    df_out = pd.DataFrame(results)
    df_out.to_csv(output_csv, index=False)

    return df_out
