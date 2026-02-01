import numpy as np

def build_aircraft_aero(airfoil_aero, geometry):
    """
    Converts 2D airfoil aero → 3D aircraft-level aero
    This is the ONLY aero dict GPkit should ever see
    """

    b = geometry["wingspan"]
    S = geometry["wing_area"]

    AR = b**2 / S
    e  = geometry.get("oswald", 0.8)

    # 2D → 3D corrections
    Cl_max_3d = 0.9 * airfoil_aero["Cl_max_2d"]
    Cd0_3d    = 1.05 * airfoil_aero["Cd0"]
    k         = 1.0 / (np.pi * e * AR)

    return {
        "Cl_max": Cl_max_3d,
        "Cd0": Cd0_3d,
        "k": k
    }
