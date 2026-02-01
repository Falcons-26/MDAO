import numpy as np

def evaluate_wing_constraints(
    wingspan,
    fuselage_span,
    W_kg,
    S_G,
    V_stall,
    Vv,
    aero,
    geom_params,
    rho=1.225
):
    """
    Returns wing-loading based T/W constraints.
    """

    # ------------------------
    # Unpack
    # ------------------------
    X   = geom_params["X"]
    T   = geom_params["T"]
    X1  = geom_params["X1"]
    T1  = geom_params["T1"]
    o   = geom_params["sweep_deg"]
    j   = geom_params["taper"]

    Cl2_w = geom_params["Cl2_w"]
    Cl2_f = geom_params["Cl2_f"]

    a0_w = geom_params["a0_w"]
    am_w = geom_params["am_w"]
    a0_f = geom_params["a0_f"]
    am_f = geom_params["am_f"]

    Cdmin = aero["Cd0"]
    CL_max = aero["Cl_max_2d"]

    # ------------------------
    # Wing loading range
    # ------------------------
    ws = np.linspace(5, 250, 400)  # N/m²
    W = W_kg * 9.81

    # ------------------------
    # Geometry
    # ------------------------
    S = W / ws
    A_w = wingspan**2 / S
    A_f = fuselage_span**2 / S

    # ------------------------
    # Oswald efficiency
    # ------------------------
    f = 0.005 * (1 + 1.5*(j - 0.6)**2)

    e_w = 1 / (1 + ((0.142 + f*A_w*(10*T)**0.33)/(np.cos(np.deg2rad(o))**2))
                 + (0.1/((4 + A_w)**0.8)))

    k_w = 1 / (np.pi * e_w * A_w)

    # ------------------------
    # Speeds
    # ------------------------
    V_climb  = 1.2 * V_stall
    V_cruise = 1.3 * V_stall

    q1 = 0.5 * rho * V_climb**2
    q2 = 0.5 * rho * V_cruise**2

    CL_TO = CL_max
    CD_TO = Cdmin + k_w*(CL_TO**2)

    # ------------------------
    # Constraints (YOUR equations)
    # ------------------------
    TW_takeoff = ((0.123/(rho*CL_max*S_G))*ws) \
               + ((0.605/CL_max)*(CD_TO - 0.04*CL_TO)) \
               + 0.04

    TW_climb = (Vv/V_climb) + (q1/ws)*Cdmin + (k_w/q1)*ws
    TW_cruise = (q2*Cdmin)/ws + (k_w/q2)*ws

    TW_required = np.maximum.reduce([TW_takeoff, TW_climb, TW_cruise])

    # ------------------------
    # Thrust available
    # ------------------------
    V_t = np.sqrt((2*W*A_w)/(rho*wingspan**2*CL_max))
    TW_avail = 2*((0.00892907/W)*(V_t**2)
                + (-0.370615/W)*V_t
                + (5.66688/W))

    return {
        "ws": ws,
        "TW_required": TW_required,
        "TW_avail": TW_avail
    }
