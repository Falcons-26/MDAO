# gpkit_inner_solver.py
import gpkit as gp

def run_gpkit_inner(
    *,
    W_struct_N,     # numeric [N]
    geom_limits     # dict
):
    g = 9.81

    # -----------------------------
    # VARIABLES (GPkit owns sizing)
    # -----------------------------
    W = gp.Variable("W", "N")
    W_payload = gp.Variable("W_payload", "N")
    W_S = gp.Variable("W_S", "N/m^2")
    S = gp.Variable("S", "m^2")
    T_W = gp.Variable("T_W", "-")

    # -----------------------------
    # CONSTANTS
    # -----------------------------
    W_struct = W_struct_N * gp.units.N
    W_max = geom_limits["W_max"] * g * gp.units.N

    WS_max = geom_limits.get("WS_max", 200.0)
    S_max = geom_limits.get("S_max", 2.0)
    TW_max = geom_limits.get("TW_max", 7.0)
    TW_min = geom_limits.get("TW_min", 1e-3)

    # -----------------------------
    # CONSTRAINTS
    # -----------------------------
    constraints = [
        # Weight bookkeeping
        W >= W_struct + W_payload,
        W <= W_max,

        # Geometry definition
        W == W_S * S,

        # Positivity (GP-safe)
        W_payload >= 1e-3 * gp.units.N,
        W_S >= 40 * gp.units("N/m^2"),
        S >= 1e-3 * gp.units("m^2"),
        T_W >= TW_min,

        # Bounds
        W_S <= WS_max * gp.units("N/m^2"),
        S <= S_max * gp.units("m^2"),
        T_W <= TW_max,
    ]

    # -----------------------------
    # OBJECTIVE
    # -----------------------------
    model = gp.Model(1 / W_payload, constraints)
    sol = model.solve(verbosity=0)

    return {
        "feasible": True,
        "W": sol(W),
        "W_payload": sol(W_payload),
        "W_S": sol(W_S),
        "S": sol(S),
        "T_W": sol(T_W),
    }
