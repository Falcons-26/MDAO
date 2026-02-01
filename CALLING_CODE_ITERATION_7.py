# CALLING_CODE_BATCH_RUN.py

import pandas as pd
import numpy as np
import importlib.util

# ==================================================
# HELPER: LOAD FUNCTION DIRECTLY FROM FILE PATH
# ==================================================
def load_function_from_file(file_path, function_name):
    spec = importlib.util.spec_from_file_location("loaded_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, function_name):
        raise RuntimeError(
            f"Function '{function_name}' not found in {file_path}.\n"
            f"Available: {dir(module)}"
        )

    return getattr(module, function_name)

# ==================================================
# USER INPUTS
# ==================================================
print("\n=== MDAO CALLING CODE (BATCH MODE) ===")

WING_CODE_PATH = input("Path to wing_analysis.py: ").strip()
FUSELAGE_CODE_PATH = input("Path to fuselage_analysis.py: ").strip()
TAIL_CODE_PATH = input("Path to tail_analysis.py: ").strip()

DIMENSIONS_CSV = input("Path to aircraft_dimensions.csv: ").strip()
AIRFOIL_CSV = input("Path to airfoil file (x y): ").strip()

OUTPUT_CSV = input("Output CSV name (e.g. run01_results.csv): ").strip()

# ==================================================
# FIXED ASSUMPTIONS (LOCKED)
# ==================================================
TW_MM = 6.0
X_BOT_MM = 10.0
BASEPLATE_GAP_MM = 2.0
K_MIN_MM = 1.0
K_STEP_MM = 0.2

TAIL_M_NMM = 8000.0
TAIL_T_NMM = 2000.0
TAIL_IY_MAX = 2e5
TAIL_E = 3000.0

DENSITY_DEFAULT = 140.0  # kg/m3

# ==================================================
# LOAD ANALYSIS FUNCTIONS
# ==================================================
wing_spar_sizing = load_function_from_file(WING_CODE_PATH, "wing_spar_sizing")
fuselage_moi_analysis = load_function_from_file(FUSELAGE_CODE_PATH, "fuselage_moi_analysis")
run_tail_structure = load_function_from_file(TAIL_CODE_PATH, "run_tail_structure")

# ==================================================
# READ FILES
# ==================================================
df = pd.read_csv(DIMENSIONS_CSV)

if "aircraft_id" not in df.columns:
    raise ValueError("CSV must contain aircraft_id")

airfoil_coords = np.loadtxt(AIRFOIL_CSV)

results_rows = []

# ==================================================
# MAIN LOOP — ALL AIRCRAFT
# ==================================================
for _, row in df.iterrows():
    aircraft_id = row["aircraft_id"]
    print(f"\n▶ Running aircraft: {aircraft_id}")

    # ---------------- WING ----------------
    wing_out = wing_spar_sizing(
        row=row,
        coords=airfoil_coords,
        cp_text=None
    )

    # ---------------- FUSELAGE ----------------
    fus_out = fuselage_moi_analysis(
        airfoil_csv=AIRFOIL_CSV,
        baseplate_gap=BASEPLATE_GAP_MM,
        w=row["fuse_rib_chord_mm"],
        tw=TW_MM,
        rt=row["fuse_rib_thickness_mm"],
        x_bot=X_BOT_MM,
        k_min=K_MIN_MM,
        step=K_STEP_MM,
        point_loads=[],
        output_csv=f"fuselage_{aircraft_id}.csv"
    )

    # ---------------- TAIL ----------------
    b = float(row["tail_flange_thickness_mm"])
    c = float(row["tail_web_thickness_mm"])

    density_map = {b: DENSITY_DEFAULT, c: DENSITY_DEFAULT}

    tail_df, tail_best, tail_ok = run_tail_structure(
        M_Nmm=TAIL_M_NMM,
        T_Nmm=TAIL_T_NMM,
        IY_max_mm4=TAIL_IY_MAX,
        L_mm=row["tail_boom_length_mm"],
        E_N_mm2=TAIL_E,
        density_map_kg_m3=density_map,
        b_values_mm=[b],
        c_values_mm=[c],
        a_range_mm=(10, 25),
        d_range_mm=(20, 40)
    )

    # ---------------- COLLECT ----------------
    results_rows.append({
        "aircraft_id": aircraft_id,
        "wing_b1_mm": wing_out["b1_mm"],
        "wing_b2_mm": wing_out["b2_mm"],
        "tail_feasible": tail_ok,
        "tail_mass_g_per_m": tail_best["mass_g_per_m"] if tail_ok else None,
        "fuselage_rows": len(fus_out)
    })

# ==================================================
# SAVE OUTPUT
# ==================================================
results_df = pd.DataFrame(results_rows)
results_df.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Batch run complete. Results saved to {OUTPUT_CSV}")
