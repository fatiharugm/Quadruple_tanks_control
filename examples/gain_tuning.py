"""Advanced example with gain tuning."""

from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)
from quadruple_tanks.utils import calculate_metrics
import numpy as np


def run_simulation_with_gains(Kp, Ki, Kd, duration=100):
    """Run simulation with specified PID gains."""
    
    system = QuadrupleTanksSystem()
    
    gains = PIDGains(Kp=Kp, Ki=Ki, Kd=Kd)
    controller1 = PIDController(gains=gains)
    controller2 = PIDController(gains=gains)
    
    sim = Simulator(
        system=system,
        controller1=controller1,
        controller2=controller2,
        dt=0.1
    )
    
    setpoint = 10.0
    time_data, state_data = sim.run(duration=duration, 
                                    setpoint1=setpoint, 
                                    setpoint2=setpoint)
    
    metrics1 = calculate_metrics(time_data, state_data["heights"][1], setpoint)
    metrics2 = calculate_metrics(time_data, state_data["heights"][2], setpoint)
    
    return metrics1, metrics2, time_data, state_data


def main():
    """Run parameter tuning study."""
    
    print("=" * 70)
    print("Quadruple Tanks - PID Gain Tuning Study")
    print("=" * 70)
    
    # Test different gain combinations
    gain_sets = [
        {"name": "Conservative", "Kp": 1.0, "Ki": 0.05, "Kd": 0.02},
        {"name": "Moderate", "Kp": 2.0, "Ki": 0.1, "Kd": 0.05},
        {"name": "Aggressive", "Kp": 3.0, "Ki": 0.2, "Kd": 0.1},
    ]
    
    results = []
    
    for gain_set in gain_sets:
        print(f"\n{gain_set['name']} Gains:")
        print(f"  Kp={gain_set['Kp']}, Ki={gain_set['Ki']}, Kd={gain_set['Kd']}")
        print("  Running simulation...", end=" ")
        
        m1, m2, _, _ = run_simulation_with_gains(
            gain_set['Kp'],
            gain_set['Ki'],
            gain_set['Kd']
        )
        
        print("Done")
        print(f"  Tank 1 - Overshoot: {m1['overshoot_percent']:6.2f}%, "
              f"Settling: {m1['settling_time']:6.2f}s, "
              f"IAE: {m1['integral_absolute_error']:8.2f}")
        print(f"  Tank 2 - Overshoot: {m2['overshoot_percent']:6.2f}%, "
              f"Settling: {m2['settling_time']:6.2f}s, "
              f"IAE: {m2['integral_absolute_error']:8.2f}")
        
        results.append({
            "name": gain_set['name'],
            "metrics_1": m1,
            "metrics_2": m2
        })
    
    print("\n" + "=" * 70)
    print("Summary: Best Overshoot Control")
    print("=" * 70)
    
    best_overshoot = min(results, 
                        key=lambda r: r['metrics_1']['overshoot_percent'])
    print(f"\n{best_overshoot['name']}: "
          f"{best_overshoot['metrics_1']['overshoot_percent']:.2f}%")
    
    print("\n" + "=" * 70)
    print("Study completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
