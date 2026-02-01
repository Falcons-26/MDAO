"""
Battery sizing module based on mission current draw.
Compatible with later OpenConcept and OpenMDAO integration.
"""

# -------------------------------
# Imports
# -------------------------------
from mission_profile import MISSION_SEGMENTS

# -------------------------------
# Battery assumptions
# -------------------------------
BATTERY_NOMINAL_VOLTAGE = 14.8      # Volts (6S LiPo)
USABLE_FRACTION = 0.8               # 80% depth of discharge
BATTERY_ENERGY_DENSITY = 200.0      # Wh/kg (conservative LiPo)

# Standard RC battery capacities (mAh)
AVAILABLE_BATTERIES_MAH = [
    1000, 1300, 1500, 1800, 2300, 2600, 2800, 3000
]

# -------------------------------
# Core calculations
# -------------------------------

def compute_required_capacity_Ah():
    """
    Computes total required battery capacity (Ah)
    based on mission current draw.
    """
    total_Ah = 0.0

    for seg in MISSION_SEGMENTS:
        Ah = seg["current_A"] * seg["duration_s"] / 3600.0
        total_Ah += Ah

    return total_Ah / USABLE_FRACTION


def compute_required_capacity_mAh():
    """
    Returns required battery capacity in mAh.
    """
    return compute_required_capacity_Ah() * 1000.0


def compute_battery_energy_Wh(required_Ah):
    """
    Computes total battery energy in Wh.
    """
    return required_Ah * BATTERY_NOMINAL_VOLTAGE


def select_battery_capacity(required_mAh):
    """
    Selects the nearest higher standard battery capacity (mAh).
    """
    for cap in AVAILABLE_BATTERIES_MAH:
        if cap >= required_mAh:
            return cap

    raise ValueError("Required capacity exceeds available battery range.")


def compute_battery_mass(energy_Wh):
    """
    Computes battery mass from energy using energy density.
    """
    return energy_Wh / BATTERY_ENERGY_DENSITY


# -------------------------------
# High-level sizing interface
# -------------------------------

def size_battery():
    """
    High-level battery sizing interface.
    Returns a dictionary of battery sizing results.
    """

    required_Ah = compute_required_capacity_Ah()
    required_mAh = required_Ah * 1000.0
    energy_Wh = compute_battery_energy_Wh(required_Ah)
    selected_mAh = select_battery_capacity(required_mAh)
    battery_mass = compute_battery_mass(energy_Wh)

    return {
        "required_capacity_mAh": required_mAh,
        "selected_battery_mAh": selected_mAh,
        "battery_energy_Wh": energy_Wh,
        "battery_mass_kg": battery_mass
    }


# -------------------------------
# Standalone test
# -------------------------------
if __name__ == "__main__":
    results = size_battery()

    print("\n=== BATTERY SIZING RESULTS ===")
    print(f"Required Capacity (mAh): {results['required_capacity_mAh']:.0f}")
    print(f"Selected Battery (mAh): {results['selected_battery_mAh']}")
    print(f"Battery Energy (Wh): {results['battery_energy_Wh']:.1f}")
    print(f"Battery Mass (kg): {results['battery_mass_kg']:.3f}")
