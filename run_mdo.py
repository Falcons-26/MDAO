# run_mdo.py

from mdo_outer_loop import evaluate_design
from structural_surrogate.interface import initialize_structural_surrogates
import numpy as np


def main():

    # -----------------------------
    # INITIALIZE STRUCTURAL MODELS
    # -----------------------------
    initialize_structural_surrogates()

    # -----------------------------
    # GEOMETRY DESIGN SPACE
    # -----------------------------
    wingspans = np.linspace(0.8, 1.3, 5)
    wing_chords = np.linspace(0.15, 0.20, 5)
    fuse_chords = np.linspace(0.28, 0.32, 5)
    tapers = np.linspace(1.0, 1.0, 5)

    # -----------------------------
    # CONSTANT DATA
    # -----------------------------
    geom_limits = {
        "W_max": 1.5875,          # kg
        "WS_max": 200.0,          # N/m^2
        "S_max": 0.3,             # m^2
        "TW_max": 5.0,
        "k": 0.045,
        "airfoil_wing": "s1223",
        "airfoil_fuse": "e858"
    }

    env_params = {
        "rho": 1.225,
        "S_G": 30.0,
        "V_stall": 10.0,
        "Vv": 2.0,
        "mu": 1.81e-5
    }

    best = None

    # -----------------------------
    # GEOMETRY SEARCH
    # -----------------------------
    for b in wingspans:
        for c in wing_chords:
            for fc in fuse_chords:
                for t in tapers:

                    geometry = (b, c, fc, t)

                    res = evaluate_design(
                        geometry=geometry,
                        geom_limits=geom_limits,
                        env_params=env_params
                    )

                    if not res["feasible"]:
                        continue

                    if best is None or res["payload_N"] > best["payload_N"]:
                        best = res
                        print("New best:", best)

    print("\n================ FINAL BEST ================")
    print(best)


if __name__ == "__main__":
    main()
