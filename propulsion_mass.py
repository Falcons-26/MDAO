"""
Temporary propulsion + structure mass model.
Structure mass will be replaced by Phase 2 outputs later.
"""

STRUCTURE_MASS_KG = 0.4   # placeholder
MOTOR_MASS_KG = 0.06 * 3  # 3 motors
ESC_MASS_KG = 0.02 * 3

def avionics_mass(battery_mass):
    return battery_mass + MOTOR_MASS_KG + ESC_MASS_KG

def non_battery_mass(structure_mass=0.4):
    return structure_mass + MOTOR_MASS_KG + ESC_MASS_KG