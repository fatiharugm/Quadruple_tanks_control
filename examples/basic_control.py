"""Basic example of quadruple tanks system control."""

from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)
from quadruple_tanks.utils import plot_results, analyze_response


def main():
    """Run a basic control simulation."""
    
    print("=" * 60)
    print("Quadruple Tanks Control System - Basic Example")
    print("=" * 60)
    
    # Create the system
    system = QuadrupleTanksSystem()
    print("\n✓ System created")
    
    # Create PID controllers for both pumps
    gains1 = PIDGains(Kp=2.0, Ki=0.1, Kd=0.05)
    gains2 = PIDGains(Kp=2.0, Ki=0.1, Kd=0.05)
    
    controller1 = PIDController(gains=gains1)
    controller2 = PIDController(gains=gains2)
    print("✓ Controllers created")
    
    # Create simulator
    sim = Simulator(
        system=system,
        controller1=controller1,
        controller2=controller2,
        dt=0.1
    )
    print("✓ Simulator created")
    
    # Set control setpoints
    setpoint1 = 10.0  # cm
    setpoint2 = 10.0  # cm
    print(f"\n• Setpoint 1: {setpoint1} cm")
    print(f"• Setpoint 2: {setpoint2} cm")
    
    # Run simulation
    print("\nRunning simulation...")
    duration = 100.0  # seconds
    time_data, state_data = sim.run(duration=duration, 
                                    setpoint1=setpoint1, 
                                    setpoint2=setpoint2)
    print(f"✓ Simulation completed ({duration}s)")
    
    # Export results
    output_file = "results.csv"
    sim.export_data(output_file)
    print(f"✓ Results exported to {output_file}")
    
    # Analyze response for tank 1
    print("\n" + "=" * 60)
    print("Control Response Analysis - Tank 1")
    print("=" * 60)
    analysis1 = analyze_response(
        time_data,
        state_data["heights"][1],
        setpoint=setpoint1
    )
    print(analysis1)
    
    # Analyze response for tank 2
    print("\n" + "=" * 60)
    print("Control Response Analysis - Tank 2")
    print("=" * 60)
    analysis2 = analyze_response(
        time_data,
        state_data["heights"][2],
        setpoint=setpoint2
    )
    print(analysis2)
    
    # Plot results
    print("\nGenerating plots...")
    try:
        plot_results(
            time_data,
            state_data["heights"],
            state_data["pumps"],
            state_data["setpoints"],
            show=True
        )
        print("✓ Plots displayed")
    except ImportError:
        print("⚠ Matplotlib not installed - skipping plots")
        print("  Install with: pip install matplotlib")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
