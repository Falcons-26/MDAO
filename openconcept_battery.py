"""
Minimal OpenConcept battery sizing test.
This replaces manual battery mass estimation.
"""

import openmdao.api as om
from openconcept.energy_storage.battery import Battery


class BatteryTest(om.Group):
    def setup(self):

        self.add_subsystem(
            "battery",
            Battery(
                num_nodes=1,
                efficiency=0.97,
                specific_energy=200.0  # Wh/kg (LiPo)
            ),
            promotes=["*"]
        )

        self.set_input_defaults("battery_energy", 35.0, units="W*h")
        self.set_input_defaults("battery_voltage", 22.2, units="V")


if __name__ == "__main__":
    prob = om.Problem()
    prob.model = BatteryTest()
    prob.setup()

    prob.run_model()

    print("\n=== OpenConcept Battery Sanity Check ===")
    print(f"Battery Energy (Wh): {prob.get_val('battery_energy')[0]:.2f}")
    print(f"Battery Mass (kg): {prob.get_val('battery_weight')[0]:.3f}")
