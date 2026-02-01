from battery_sizing import size_battery
from propulsion_mass import avionics_mass, non_battery_mass

battery = size_battery()

print("\n=== PHASE 3: BATTERY & PROPULSION ===")
print(f"Required Battery Capacity (mAh): {battery['required_capacity_mAh']:.0f}")
print(f"Selected Battery (mAh): {battery['selected_battery_mAh']}")
print(f"Battery Energy (Wh): {battery['battery_energy_Wh']:.1f}")
print(f"Battery Mass (kg): {battery['battery_mass_kg']:.3f}")
print(f"Avionics Mass (kg): {avionics_mass(battery['battery_mass_kg']):.3f}")
print(f"Non-battery Mass (kg): {non_battery_mass():.3f}")
