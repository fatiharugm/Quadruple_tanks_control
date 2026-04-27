"""Quick start guide for quadruple tanks control system."""

import sys
import os

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)


def quick_example():
    """Quick example demonstrating basic usage."""
    
    print("\n" + "=" * 60)
    print("QUICK START: Quadruple Tanks Control System")
    print("=" * 60)
    
    # Step 1: Create the system
    print("\n[1/4] Creating quadruple tanks system...")
    system = QuadrupleTanksSystem()
    print("      ✓ System ready with 4 tanks")
    
    # Step 2: Create controllers
    print("\n[2/4] Creating PID controllers...")
    # TODO: Tune these gains to achieve desired performance
    gains = PIDGains(Kp=0.0, Ki=0.0, Kd=0.0)
    controller1 = PIDController(gains=gains)
    controller2 = PIDController(gains=gains)
    print("      ✓ Controllers configured")
    
    # Step 3: Create simulator
    print("\n[3/4] Setting up simulator...")
    sim = Simulator(
        system=system,
        controller_13=controller1,
        controller_24=controller2,
        dt=0.1
    )
    print("      ✓ Simulator ready")
    
    # Step 4: Run simulation
    print("\n[4/4] Running 50-second simulation...")
    time_data, state_data = sim.run(
        duration=50,
        setpoint1=10.0,
        setpoint2=10.0
    )
    print("      ✓ Simulation complete")
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    final_heights = {
        1: state_data["heights"][1][-1],
        2: state_data["heights"][2][-1],
        3: state_data["heights"][3][-1],
        4: state_data["heights"][4][-1],
    }
    
    print(f"\nFinal Tank Heights:")
    print(f"  Tank 1: {final_heights[1]:.2f} cm (setpoint: 10.00 cm)")
    print(f"  Tank 2: {final_heights[2]:.2f} cm (setpoint: 10.00 cm)")
    print(f"  Tank 3: {final_heights[3]:.2f} cm")
    print(f"  Tank 4: {final_heights[4]:.2f} cm")
    
    print(f"\nData points recorded: {len(time_data)}")
    print(f"Simulation time: {time_data[-1]:.1f} seconds")
    
    # Export results
    sim.export_data("quick_results.csv")
    print(f"\n✓ Results saved to 'quick_results.csv'")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Try running the basic example:
   python examples/basic_control.py

2. Try gain tuning:
   python examples/gain_tuning.py

3. Visualize results:
   pip install matplotlib
   python examples/basic_control.py

4. Run tests:
   pytest tests/

5. Check out the README for more information:
   - Model equations
   - Advanced usage
   - Parameter tuning
   """)
    
    print("=" * 60)


if __name__ == "__main__":
    quick_example()
