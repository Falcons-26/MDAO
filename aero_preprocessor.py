# aero/aero_preprocessor.py

from aero.airfoil_2d import airfoil_2d_features
from aero.wing_3d import wing_3d_aero


def compute_aero(
    *,
    geometry,
    Re,
    airfoil_wing,
    airfoil_fuse
):
    """
    Level-3 aero model:
    - Wing airfoil: lift + drag
    - Fuselage airfoil: drag only
    """

    wingspan, wing_chord, _, _ = geometry
    AR = wingspan / wing_chord

    # -----------------------------
    # WING
    # -----------------------------
    wing_2d = airfoil_2d_features(airfoil_wing, Re)
    wing = wing_3d_aero(wing_2d, AR)

    # -----------------------------
    # FUSELAGE (drag only)
    # -----------------------------
    fuse_2d = airfoil_2d_features(airfoil_fuse, Re)
    fuselage = {
        "Cd0": fuse_2d["Cd0"]
    }

    return {
        "wing": wing,
        "fuselage": fuselage
    }
