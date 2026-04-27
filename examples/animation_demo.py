"""Animation example for quadruple tanks system."""

from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
    animate_simulation,
)


def main():
    """Run an animated control simulation."""
    
    print("\n" + "=" * 70)
    print("QUADRUPLE TANKS ANIMATION - LIVE VISUALIZATION")
    print("=" * 70)
    
    # Create system
    print("\n[1/3] Setting up system and controllers...")
    system = QuadrupleTanksSystem()
    
    # Create controllers with tuned gains
    # TODO: Tune these gains to achieve desired performance
    gains = PIDGains(Kp=0.0, Ki=0.0, Kd=0.0)
    controller1 = PIDController(gains=gains)
    controller2 = PIDController(gains=gains)
    
    # Create simulator
    sim = Simulator(
        system=system,
        controller1=controller1,
        controller2=controller2,
        dt=0.1
    )
    print("      ✓ System ready")
    
    # Set control targets
    setpoint1 = 12.0  # cm
    setpoint2 = 12.0  # cm
    print(f"      ✓ Setpoints: Tank 1 = {setpoint1} cm, Tank 2 = {setpoint2} cm")
    
    # Create animation
    print("\n[2/3] Creating animated visualization...")
    print("      ✓ Animation window will open shortly...")
    
    try:
        import matplotlib
        matplotlib.use('TkAgg')  # Better interactivity
        import matplotlib.pyplot as plt
    except:
        pass
    
    # Run animation (60 second simulation)
    duration = 60.0  # seconds
    print(f"      ✓ Running {duration}s simulation with live animation")
    
    animator = animate_simulation(
        simulator=sim,
        duration=duration,
        setpoint1=setpoint1,
        setpoint2=setpoint2,
        figsize=(14, 8),
        interval=100,  # Update every 100ms
        show_plot=True
    )
    
    print("\n[3/3] Animation complete!")
    
    # Display results
    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)
    
    time_array = animator.time_data
    heights = animator.heights_data
    
    if len(time_array) > 0:
        print(f"\nSimulation Duration: {time_array[-1]:.1f} seconds")
        print(f"Data Points Recorded: {len(time_array)}")
        
        print(f"\nFinal Tank Heights:")
        print(f"  Tank 1: {heights[1][-1]:6.2f} cm (Setpoint: {setpoint1:.2f} cm)")
        print(f"  Tank 2: {heights[2][-1]:6.2f} cm (Setpoint: {setpoint2:.2f} cm)")
        print(f"  Tank 3: {heights[3][-1]:6.2f} cm")
        print(f"  Tank 4: {heights[4][-1]:6.2f} cm")
        
        # Calculate tracking errors
        error1 = abs(heights[1][-1] - setpoint1)
        error2 = abs(heights[2][-1] - setpoint2)
        print(f"\nTracking Errors:")
        print(f"  Tank 1: {error1:.4f} cm")
        print(f"  Tank 2: {error2:.4f} cm")
    
    print("\n" + "=" * 70)
    print("Visualization Features:")
    print("=" * 70)
    print("""
✓ LEFT PANEL: Real-time tank water levels
  - 4 tanks shown with current heights
  - Water fills from bottom up
  - Color intensity indicates fill level
  
✓ RIGHT PANEL: System trends
  - Height trajectories for all tanks
  - Setpoint lines (dashed) for upper tanks
  - Real-time plotting as simulation runs
  
✓ PUMP INDICATORS: Green arrows showing pump locations
✓ INTERCONNECTIONS: Dashed lines showing tank connections

Try these variations:
  1. Increase setpoints for higher tank levels
  2. Modify PID gains for different response characteristics
  3. Run longer simulations (change duration parameter)
  4. Adjust time step for faster/slower animation
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
