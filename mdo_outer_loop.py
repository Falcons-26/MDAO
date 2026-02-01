# mdo_outer_loop.py

from structural_surrogate.interface import get_structural_weight
from gpkit_inner_solver import run_gpkit_inner
from aero.aero_preprocessor import compute_aero


def evaluate_design(
    *,
    geometry,
    aero=None,          # kept for backward compatibility (unused)
    geom_limits,
    env_params
):
    # -----------------------------
    # GEOMETRY UNPACK
    # -----------------------------
    wingspan, wing_chord, fuse_chord, taper = geometry

    # -----------------------------
    # STRUCTURAL SURROGATE
    # -----------------------------
    W_struct_g, W_wing_g, W_fuse_g = get_structural_weight(
        wingspan=wingspan,
        wing_chord=wing_chord,
        fuse_chord=fuse_chord
    )

    g = 9.81
    W_struct_N = (W_struct_g / 1000.0) * g

    # ==========================================================
    # GPkit PASS 1 → sizing (no thrust constraint)
    # ==========================================================
    sol1 = run_gpkit_inner(
        W_struct_N=W_struct_N,
        geom_limits=geom_limits
    )

    WS = sol1["W_S"].to("N/m^2").magnitude

    # -----------------------------
    # ENVIRONMENT
    # -----------------------------
    rho = env_params["rho"]
    mu  = env_params["mu"]
    S_G = env_params["S_G"]
    V_stall = env_params["V_stall"]
    Vv = env_params["Vv"]

    V_climb  = 1.2 * V_stall
    V_cruise = 1.3 * V_stall

    # -----------------------------
    # REYNOLDS NUMBER (stall-based)
    # -----------------------------
    Re = rho * V_stall * wing_chord / mu

    # -----------------------------
    # AERO (LEVEL-3, MULTI-AIRFOIL)
    # -----------------------------
    aero = compute_aero(
        geometry=geometry,
        Re=Re,
        airfoil_wing=geom_limits["airfoil_wing"],
        airfoil_fuse=geom_limits["airfoil_fuse"]
    )

    CL_max = aero["wing"]["Cl_max"]

    # -----------------------------
    # FUSELAGE DRAG NORMALIZATION
    # -----------------------------

    Cd0_wing = aero["wing"]["Cd0"]
    Cd0_fuse = aero["fuselage"]["Cd0"]

    # Reference areas
    S_wing = sol1["S"].to("m^2").magnitude

    fuse_span = 0.15          # [m] FIXED fuselage span (given)
    S_fuse_ref = fuse_span * fuse_chord

    # Total parasite drag (wing-area referenced)
    Cdmin = Cd0_wing + Cd0_fuse * (S_fuse_ref / S_wing)


    k = geom_limits["k"]   # induced drag handled externally

    # -----------------------------
    # DYNAMIC PRESSURE
    # -----------------------------
    q1 = 0.5 * rho * V_climb**2
    q2 = 0.5 * rho * V_cruise**2

    # -----------------------------
    # REQUIRED T/W
    # -----------------------------
    TW_takeoff = (
        (0.123 / (rho * CL_max * S_G)) * WS
        + (0.605 / CL_max) * Cdmin
        + 0.04
    )

    TW_climb = (
        (Vv / V_climb)
        + (q1 / WS) * Cdmin
        + (k / q1) * WS
    )

    TW_cruise = (
        (q2 * Cdmin) / WS
        + (k / q2) * WS
    )

    TW_required = max(TW_takeoff, TW_climb, TW_cruise)

    # ==========================================================
    # GPkit PASS 2 → enforce thrust requirement
    # ==========================================================
    sol2 = run_gpkit_inner(
        W_struct_N=W_struct_N,
        geom_limits={**geom_limits, "TW_min": TW_required}
    )

    # -----------------------------
    # SAFE EXTRACTION
    # -----------------------------
    TW = sol2["T_W"].to("dimensionless").magnitude
    payload = sol2["W_payload"].to("N").magnitude
    S = sol2["S"].to("m^2").magnitude
    W = sol2["W"].to("N").magnitude

    feasible = TW >= TW_required

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "geometry": geometry,
        "feasible": feasible,
        "W_struct_g": W_struct_g,
        "W_wing_g": W_wing_g,
        "W_fuse_g": W_fuse_g,
        "payload_N": payload,
        "W": W,
        "S": S,
        "WS": WS,
        "TW": TW,
        "TW_required": TW_required,
        "TW_takeoff": TW_takeoff,
        "TW_climb": TW_climb,
        "TW_cruise": TW_cruise,
        "Re": Re,
        "Cl_max": CL_max,
        "Cd0_total": Cdmin
    }
