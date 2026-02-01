import numpy as np
import matplotlib.pyplot as plt

def plot_constraints(
    ws,
    CL_max,
    Cdmin,
    k,
    rho,
    S_G,
    V_stall,
    Vv
):
    """
    Plots T/W vs W/S constraints (takeoff, climb, cruise)
    """

    V_climb = 1.2 * V_stall
    V_cruise = 1.3 * V_stall

    q1 = 0.5 * rho * V_climb**2
    q2 = 0.5 * rho * V_cruise**2

    CD_TO = Cdmin
    CL_TO = CL_max

    TW_takeoff = (
        (0.123 / (rho * CL_max * S_G)) * ws
        + (0.605 / CL_max) * (CD_TO - 0.04 * CL_TO)
        + 0.04
    )

    TW_climb = (
        (Vv / V_climb)
        + (q1 / ws) * Cdmin
        + (k / q1) * ws
    )

    TW_cruise = (
        (q2 * Cdmin) / ws
        + (k / q2) * ws
    )

    plt.figure(figsize=(8,6))
    plt.plot(ws, TW_takeoff, label="Takeoff")
    plt.plot(ws, TW_climb, label="Climb")
    plt.plot(ws, TW_cruise, label="Cruise")

    plt.xlabel("Wing Loading W/S (N/m²)")
    plt.ylabel("Thrust-to-Weight T/W")
    plt.grid(True)
    plt.legend()
    plt.title("Constraint Diagram (T/W vs W/S)")
    plt.show()
