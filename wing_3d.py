import numpy as np

def wing_3d_aero(airfoil_2d, AR, e=0.85):
    Cl_max_3d = 0.9 * airfoil_2d["Cl_max_2d"]

    return {
        "Cl_max": Cl_max_3d,
        "Cd0": airfoil_2d["Cd0"]
    }
