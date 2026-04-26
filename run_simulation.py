"""
SIMULATION RUNNER
-----------------
This script sets up the Quadruple Tanks "Plant" and connects it to your
controller from `controller.py`. It also handles the animation/scope
for visualization.

Students: You do not need to modify this file unless you want to change
the setpoints or simulation duration.
"""

import sys
import matplotlib

# Try to use TkAgg for interactive window, otherwise fallback
try:
    matplotlib.use('TkAgg')
except Exception:
    pass

from quadruple_tanks import QuadrupleTanksSystem, Simulator
from quadruple_tanks.animation import animate_simulation

# Import the student's controller
try:
    from controller import PumpController
except ImportError:
    print("Error: Could not find 'PumpController' in controller.py. Please make sure it exists.")
    sys.exit(1)


def main():
    print("=" * 60)
    print(" QUADRUPLE TANKS SYSTEM - SIMULATION RUNNER")
    print("=" * 60)
    
    # 1. Setup the Plant (Quadruple Tanks System)
    print("\n[1/3] Initializing the Plant...")
    system = QuadrupleTanksSystem()
    
    # 2. Setup the Controllers (from controller.py)
    print("[2/3] Loading your pump-based controllers...")
    controller_pump1 = PumpController(max_pump_flow=300.0)  # Pump 1: regulates Tank 1
    controller_pump2 = PumpController(max_pump_flow=300.0)  # Pump 2: regulates Tank 2
    
    # 3. Create the Simulator to tie Plant and Controllers together
    # NEW ARCHITECTURE: Pump-based control (simpler, more effective)
    sim = Simulator(
        system=system,
        controller_pump1=controller_pump1,
        controller_pump2=controller_pump2,
        dt=0.1
    )
    
    # --- SIMULATION PARAMETERS ---
    duration = 300.0    # Simulation time in seconds (5 minutes)
    setpoint1 = 40.0   # Target height for Tank 1 (UPPER tank, directly controlled by Pump 1)
    setpoint2 = 60.0   # Target height for Tank 2 (UPPER tank, directly controlled by Pump 2)
    setpoint3 = 70.0   # Target height for Tank 3 (LOWER tank, passively follows coupling)
    setpoint4 = 80.0   # Target height for Tank 4 (LOWER tank, passively follows coupling)
    
    # Update simulator setpoints
    sim.set_setpoints(setpoint1, setpoint2, setpoint3, setpoint4)
    
    print(f"\nSimulation Parameters (PUMP-BASED CONTROL):")
    print(f" - Duration:      {duration} seconds")
    print(f" - Target T1 (controlled by Pump1): {setpoint1} cm")
    print(f" - Target T2 (controlled by Pump2): {setpoint2} cm")
    print(f" - Target T3 (passive, follows coupling): {setpoint3} cm")
    print(f" - Target T4 (passive, follows coupling): {setpoint4} cm")
    
    # 4. Run the Animation (The Scope)
    print("\n[3/3] Starting visualization (Scope)...")
    print("      Please wait for the window to appear.")
    
    try:
        animator = animate_simulation(
            simulator=sim,
            duration=duration,
            setpoint1=setpoint1,
            setpoint2=setpoint2,
            setpoint3=setpoint3,
            setpoint4=setpoint4,
            figsize=(14, 8),
            interval=100,
            show_plot=True
        )
        print("\nSimulation complete!")
        
        # --- AUTOMATIC SCORING ---
        print("\n" + "=" * 60)
        print(" AUTOMATIC SCORING RESULTS")
        print("=" * 60)
        
        import numpy as np
        time_data = np.array(animator.time_data)
        heights_data = animator.heights_data
        
        # NEW: Use per-tank setpoints instead of hardcoded target
        setpoints = {
            1: setpoint1,
            2: setpoint2,
            3: setpoint3,
            4: setpoint4
        }
        
        max_duration = 300.0  # seconds
        sustain_window = 30.0 # tank must stay in band for last 30s to count
        
        tanks_at_steady_state = 0
        t_last_ss = 0.0

        print(f"Individual Tank Setpoints & Tolerances (±5%):")
        print("-" * 60)
        
        # Print setpoints and tolerances first
        for tank_id in range(1, 5):
            sp = setpoints[tank_id]
            tol = sp * 0.05
            print(f"Tank {tank_id}: Target {sp:.1f} cm  |  Tolerance: ±{tol:.2f} cm")
        
        print("-" * 60)
        
        for tank_id in range(1, 5):
            h_data = np.array(heights_data[tank_id])
            if len(h_data) == 0:
                continue

            # Get this tank's setpoint and tolerance
            target = setpoints[tank_id]
            tolerance = target * 0.05  # ±5% of its setpoint
            
            # A tank counts as settled only if it remains within ±tolerance
            # of ITS OWN target for the final sustain_window seconds
            last_n = int(sustain_window / 0.1)
            recent = h_data[-last_n:]
            stayed_in_band = bool(np.all(np.abs(recent - target) <= tolerance))

            if stayed_in_band:
                tanks_at_steady_state += 1
                # Find first entry into the ±tolerance band
                indices = np.where(np.abs(h_data - target) <= tolerance)[0]
                first_time = float(time_data[indices[0]]) if len(indices) > 0 else max_duration
                t_last_ss = max(t_last_ss, first_time)
                print(f"Tank {tank_id}: \u2713 Settled at {first_time:.1f}s  (final: {h_data[-1]:.1f} cm)")
            else:
                print(f"Tank {tank_id}: \u2717 Not settled  (final: {h_data[-1]:.1f} cm)")

        # NEW SCORING FORMULA: Sum individual tank scores
        # Each tank that settles contributes (300 - t_settle) to total score
        final_score = 0.0
        individual_scores = {}
        
        print("-" * 60)
        print("Individual Tank Scores:")
        print("-" * 60)
        
        for tank_id in range(1, 5):
            h_data = np.array(heights_data[tank_id])
            if len(h_data) == 0:
                continue

            target = setpoints[tank_id]
            tolerance = target * 0.05  # ±5% of its setpoint
            last_n = int(sustain_window / 0.1)
            recent = h_data[-last_n:]
            stayed_in_band = bool(np.all(np.abs(recent - target) <= tolerance))

            if stayed_in_band:
                indices = np.where(np.abs(h_data - target) <= tolerance)[0]
                first_time = float(time_data[indices[0]]) if len(indices) > 0 else max_duration
                tank_score = max_duration - first_time
                individual_scores[tank_id] = tank_score
                final_score += tank_score
                print(f"Tank {tank_id}: Settled at {first_time:.1f}s → Score = 300 - {first_time:.1f} = {tank_score:.1f}")
            else:
                individual_scores[tank_id] = 0.0
                print(f"Tank {tank_id}: Did not settle → Score = 0")

        print("-" * 60)
        print(f"FINAL SCORE = Sum of all tank contributions = {final_score:.1f}")
        print("=" * 60 + "\n")
        print("Scoring formula: Score = Σ(300 - T_settle_i) for all tanks that settle")
        print("Max possible score = 1200  (all 4 tanks settled at t=0)")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nError during animation: {e}")
        print("Note: If you are running without a display, the interactive window cannot open.")

if __name__ == "__main__":
    main()
