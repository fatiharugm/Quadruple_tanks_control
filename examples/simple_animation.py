"""Simple animation demo - visual tank simulation."""

import sys
from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)
from quadruple_tanks.utils import plot_results


def demo():
    """Run a simple animation demo with visualization."""
    
    print("\n" + "🚀 " + "=" * 66)
    print("  QUADRUPLE TANKS - SIMPLE ANIMATION DEMO")
    print("=" * 68)
    
    # Step 1: Create system
    print("\n[STEP 1] Initializing Control System")
    print("-" * 68)
    system = QuadrupleTanksSystem()
    print("✓ System created with 4 tanks")
    print("  - Upper tanks: Tank 1 (Red) and Tank 2 (Teal)")
    print("  - Lower tanks: Tank 3 (Blue) and Tank 4 (Orange)")
    
    # Step 2: Create controllers
    print("\n[STEP 2] Configuring PID Controllers")
    print("-" * 68)
    # TODO: Tune these gains to achieve desired performance
    gains = PIDGains(Kp=0.0, Ki=0.0, Kd=0.0)
    controller1 = PIDController(gains=gains)
    controller2 = PIDController(gains=gains)
    print(f"✓ Controllers configured")
    print(f"  - Kp (Proportional): {gains.Kp}")
    print(f"  - Ki (Integral):     {gains.Ki}")
    print(f"  - Kd (Derivative):   {gains.Kd}")
    
    # Step 3: Setup simulator
    print("\n[STEP 3] Setting up Simulator")
    print("-" * 68)
    sim = Simulator(
        system=system,
        controller1=controller1,
        controller2=controller2,
        dt=0.1
    )
    print("✓ Simulator ready")
    print(f"  - Time step: {sim.dt}s")
    print(f"  - Controllers: Pump 1 and Pump 2")
    
    # Step 4: Run simulation
    print("\n[STEP 4] Running 60-second Simulation")
    print("-" * 68)
    print("⏱️  Simulating... ", end="", flush=True)
    
    setpoint1 = 12.0
    setpoint2 = 12.0
    duration = 60.0
    
    time_data, state_data = sim.run(
        duration=duration,
        setpoint1=setpoint1,
        setpoint2=setpoint2
    )
    
    print(f"Done! ✓")
    print(f"  - Duration: {time_data[-1]:.1f} seconds")
    print(f"  - Data points: {len(time_data)}")
    print(f"  - Sampling rate: {1/sim.dt:.1f} Hz")
    
    # Step 5: Display results
    print("\n[STEP 5] Final System State")
    print("-" * 68)
    
    h1_final = state_data["heights"][1][-1]
    h2_final = state_data["heights"][2][-1]
    h3_final = state_data["heights"][3][-1]
    h4_final = state_data["heights"][4][-1]
    
    print(f"\nWater Levels in Tanks:")
    print(f"┌─ Upper Tanks ──────────────────────────────────────┐")
    print(f"│  Tank 1 (Target: {setpoint1:5.1f} cm) ─→ {h1_final:6.2f} cm  ", end="")
    error1 = setpoint1 - h1_final
    if abs(error1) < 1.0:
        print("✓ [Good Control]")
    else:
        print(f"⚠ [Error: {error1:+.2f}]")
    
    print(f"│  Tank 2 (Target: {setpoint2:5.1f} cm) ─→ {h2_final:6.2f} cm  ", end="")
    error2 = setpoint2 - h2_final
    if abs(error2) < 1.0:
        print("✓ [Good Control]")
    else:
        print(f"⚠ [Error: {error2:+.2f}]")
    
    print(f"└────────────────────────────────────────────────────┘")
    
    print(f"┌─ Lower Tanks ──────────────────────────────────────┐")
    print(f"│  Tank 3 ────────────────────────→ {h3_final:6.2f} cm")
    print(f"│  Tank 4 ────────────────────────→ {h4_final:6.2f} cm")
    print(f"└────────────────────────────────────────────────────┘")
    
    # Step 6: Plot results
    print("\n[STEP 6] Generating Plots")
    print("-" * 68)
    print("📊 Creating visualization... ", end="", flush=True)
    
    try:
        import matplotlib
        # Use non-interactive backend for better compatibility
        matplotlib.use('Agg')
        
        fig = plot_results(
            time_data,
            state_data["heights"],
            state_data["pumps"],
            state_data["setpoints"],
            show=False
        )
        
        # Save figure
        output_file = "tank_simulation.png"
        fig.savefig(output_file, dpi=100, bbox_inches='tight')
        print(f"Done! ✓")
        print(f"  - Chart saved: {output_file}")
        print(f"  - Resolution: 100 DPI")
        
        import matplotlib.pyplot as plt
        plt.close('all')
        
    except Exception as e:
        print(f"⚠ Could not generate plots: {str(e)}")
    
    # Step 7: Export data
    print("\n[STEP 7] Exporting Data")
    print("-" * 68)
    
    csv_file = "animation_demo_results.csv"
    sim.export_data(csv_file)
    print(f"✓ Data exported to: {csv_file}")
    print(f"  - Columns: Time, H1, H2, H3, H4, Pump1, Pump2, SP1, SP2")
    print(f"  - Format: Comma-separated values")
    
    # Summary
    print("\n" + "=" * 68)
    print("✨ SIMULATION COMPLETE!")
    print("=" * 68)
    
    print(f"""
📁 Output Files:
   ✓ tank_simulation.png  - Visual charts of tank levels
   ✓ animation_demo_results.csv  - Complete simulation data

📊 Key Results:
   • Upper Tank Levels: {h1_final:.2f}cm (Tank 1), {h2_final:.2f}cm (Tank 2)
   • Lower Tank Levels: {h3_final:.2f}cm (Tank 3), {h4_final:.2f}cm (Tank 4)
   • Control Error T1: {abs(error1):.4f}cm
   • Control Error T2: {abs(error2):.4f}cm

💡 Next Steps:
   1. View the generated image: tank_simulation.png
   2. Analyze the CSV data in Excel or Python
   3. Try different PID gains for comparison
   4. Run examples/animation_demo.py for interactive animation
      (requires display/matplotlib backend)

📖 Learn More:
   - python quick_start.py
   - python examples/basic_control.py
   - python examples/gain_tuning.py
   - Check README.md for full documentation
""")
    
    print("=" * 68 + "\n")


if __name__ == "__main__":
    demo()
