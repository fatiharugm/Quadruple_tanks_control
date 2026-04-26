# Animation Module - Quadruple Tanks System

## Overview

The animation module provides real-time visualization of the quadruple tanks system during simulation. It creates professional animations showing tank levels, pump flows, and control setpoints with both visual tank representation and trend plots.

## Features

### Visual Elements
- **Tank Representation**: Real-time water level visualization in all 4 tanks
- **Color Coding**: Each tank has a unique color for easy identification
  - Tank 1: Red (#FF6B6B) - Upper Left
  - Tank 2: Teal (#4ECDC4) - Upper Right  
  - Tank 3: Blue (#45B7D1) - Lower Left
  - Tank 4: Orange (#FFA07A) - Lower Right

- **Live Height Display**: Numerical height value displayed in each tank
- **Trend Plots**: Real-time line plots showing:
  - Height trajectories for all tanks
  - Setpoint references (dashed lines for upper tanks)
  - Pump flow rates

- **System Annotations**: 
  - Pump locations with directional arrows
  - Tank interconnection indicators
  - Dynamic simulation time display

## Usage

### Method 1: Simple Animation (Recommended for Quick Demos)

```python
from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)
from quadruple_tanks.animation import animate_simulation

# Setup system and controllers
system = QuadrupleTanksSystem()
gains = PIDGains(Kp=2.0, Ki=0.1, Kd=0.05)
controller = PIDController(gains=gains)

# Create simulator
sim = Simulator(system=system, controller1=controller, dt=0.1)

# Run animated simulation
animator = animate_simulation(
    simulator=sim,
    duration=60.0,          # 60 seconds
    setpoint1=12.0,         # Target height for tank 1
    setpoint2=12.0,         # Target height for tank 2
    figsize=(14, 8),        # Window size
    interval=100,           # Update every 100ms (default)
    show_plot=True          # Display immediately
)
```

### Method 2: Advanced Animation (Full Control)

```python
from quadruple_tanks.animation import TankAnimator

# Create animator
animator = TankAnimator(simulator=sim, figsize=(14, 8))

# Create animation (doesn't start yet)
anim = animator.animate(
    duration=60.0,
    setpoint1=12.0,
    setpoint2=12.0,
    interval=100  # Update interval in milliseconds
)

# Show animation
animator.show()

# Or access collected data
time_data = animator.time_data
heights_data = animator.heights_data
```

## Animation Classes

### TankAnimator

Main class for creating and managing tank animations.

#### Methods

**`__init__(simulator, figsize=(14, 8))`**
- Initializes the animator
- Creates figure with tank visualization and trend plots

**`animate(duration, setpoint1=10.0, setpoint2=10.0, interval=100)`**
- Creates the animation
- Returns: FuncAnimation object

**`show()`**
- Displays the animation window
- Blocks until window is closed

**`save(filename, fps=10)`**
- Saves animation to file (requires ffmpeg)

#### Properties

- `time_data`: List of simulation times
- `heights_data`: Dictionary with height arrays for each tank
- `pump_data`: Dictionary with pump flow data

### Function: animate_simulation

Convenience function for quick animation setup.

```python
animator = animate_simulation(
    simulator,        # Simulator instance
    duration=60,      # Duration in seconds
    setpoint1=10,     # Tank 1 setpoint (cm)
    setpoint2=10,     # Tank 2 setpoint (cm)
    figsize=(14, 8),  # Figure size
    interval=100,     # Update interval (ms)
    show_plot=True    # Display animation
)
```

**Returns**: TankAnimator instance

## Examples

### Example 1: Basic Animation

```python
# examples/simple_animation.py
python examples/simple_animation.py
```

Creates a 60-second simulation with visualization and generates:
- `tank_simulation.png` - Static plot of results
- `animation_demo_results.csv` - Data export

### Example 2: Interactive Animation

```python
# examples/animation_demo.py
python examples/animation_demo.py
```

Creates a full interactive animation with:
- Real-time tank visualization
- Live trend monitoring
- Real-time controller adjustments

## Running Examples

### Quick Demo (No Display Required)
```bash
# Generates PNG image and CSV data
python examples/simple_animation.py
```

### Interactive Animation (Requires Display)
```bash
# Opens matplotlib window with animation
python examples/animation_demo.py
```

## Configuration Options

### Time Step (`dt`)
- Controls simulation accuracy and animation smoothness
- Default: 0.1 seconds
- Smaller = more accurate but slower
- Larger = faster but less accurate

```python
sim = Simulator(dt=0.05)  # Finer resolution
sim = Simulator(dt=0.2)   # Coarser resolution
```

### Animation Update Interval (`interval`)
- Controls how often the display updates
- Units: milliseconds
- Default: 100 ms (10 updates/second)
- Lower = smoother but more CPU intensive

```python
animator.animate(duration=60, interval=50)   # Very smooth (20 fps)
animator.animate(duration=60, interval=200)  # Slower (5 fps)
```

### Figure Size
- Control window dimensions
- Default: (14, 8) inches
- Recommended: 12-16 width for visibility

```python
animator = TankAnimator(simulator, figsize=(16, 9))
animator = TankAnimator(simulator, figsize=(10, 6))  # Smaller
```

## Performance Considerations

### Memory Usage
- Long simulations accumulate data in memory
- 10 minutes at 10 Hz = ~6000 data points per tank
- Typical memory: < 1 MB per 10 minutes

### CPU Usage
- Animation update rate affects CPU
- Smaller `interval` = higher CPU usage
- Consider system capabilities when choosing interval

### Recommended Settings

| Duration | dt   | interval | Purpose |
|----------|------|----------|---------|
| 10s      | 0.05 | 50       | Detailed analysis |
| 60s      | 0.1  | 100      | Demonstration |
| 5min     | 0.1  | 200      | Long-term study |
| 30min    | 0.2  | 500      | Extended simulation |

## Output Formats

### Static Image (PNG)
Generated by `plot_results()`:
- Resolution: 100 DPI (configurable)
- Size: ~100-150 KB
- Contains 4 subplots with all trends

### Animated GIF (requires Pillow)
```python
animator.save("animation.gif")
```

### MP4 Video (requires FFmpeg)
```bash
pip install ffmpeg-python
animator.save("animation.mp4", fps=10)
```

### CSV Data
```python
sim.export_data("results.csv")
```

Columns: Time, H1, H2, H3, H4, Pump1, Pump2, SP1, SP2

## Visualization Details

### Tank Panel (Left)
Shows real-time water levels:
- Tank outlines with current heights
- Color intensity indicates fill level
- Dynamic height values
- Pump indicators at top
- Interconnection diagram

### Trend Panel (Right)
Shows historical behavior:
- Line plot of all 4 tank heights
- Dashed setpoint reference lines
- Time on x-axis
- Height in cm on y-axis
- Legend for easy identification

## Advanced Usage

### Custom Controller Tuning with Animation

```python
# Compare different PID gains visually
for Kp in [1.0, 2.0, 3.0]:
    sim = Simulator(system=QuadrupleTanksSystem(),
                   controller1=PIDController(gains=PIDGains(Kp=Kp, Ki=0.1, Kd=0.05)))
    animate_simulation(sim, duration=60, setpoint1=12.0, show_plot=True)
```

### Monitoring Specific Events

```python
animator = TankAnimator(simulator=sim)
anim = animator.animate(duration=60)

# Access data during animation
for t, h1, h2 in zip(animator.time_data, 
                     animator.heights_data[1], 
                     animator.heights_data[2]):
    if h1 > 15:  # Check for overshoot
        print(f"Overshoot at t={t:.1f}s: h1={h1:.2f}")
```

### Custom Analysis Post-Animation

```python
animator = animate_simulation(sim, duration=60, show_plot=True)

# Get collected data
time = np.array(animator.time_data)
h1 = np.array(animator.heights_data[1])
h2 = np.array(animator.heights_data[2])

# Perform custom analysis
peak = np.max(h1)
settling_index = np.where(np.abs(h1 - 12.0) < 0.1)[0]
settling_time = time[settling_index[0]] if len(settling_index) > 0 else None

print(f"Peak height: {peak:.2f} cm")
print(f"Settling time: {settling_time:.1f} s")
```

## Troubleshooting

### Issue: Animation window doesn't appear

**Solutions:**
1. Check matplotlib backend:
   ```python
   import matplotlib
   matplotlib.use('TkAgg')  # Force TkAgg backend
   ```

2. Use simple_animation.py instead (doesn't require display)

3. Save to file instead:
   ```python
   animator.save("output.gif")
   ```

### Issue: Animation is slow

**Solutions:**
1. Increase `interval` (update less frequently)
2. Reduce `duration` (shorter simulation)
3. Increase `dt` (larger time step)
4. Decrease `figsize` (smaller window)

### Issue: Memory usage is high

**Solutions:**
1. Use longer time steps: `dt=0.2` instead of `0.05`
2. Run shorter simulations
3. Clear data periodically: `sim.reset()`
4. Use CSV export instead of keeping data in memory

### Issue: Static plot only, no animation

**Solutions:**
1. Use `examples/simple_animation.py` (generates static PNG)
2. Check for display availability
3. Use non-interactive backend: `matplotlib.use('Agg')`

## Dependencies

### Required
- `matplotlib` (for animation)
- `numpy` (for numerical operations)

### Optional
- `Pillow` (for GIF export)
- `ffmpeg` (for MP4 export)

### Installation
```bash
# With visualization
pip install matplotlib

# For animation export
pip install Pillow ffmpeg-python
```

## Performance Benchmarks

### Typical Simulation Times
| Duration | dt    | Time | CPU |
|----------|-------|------|-----|
| 10s      | 0.05  | 0.5s | Low |
| 60s      | 0.1   | 1.5s | Low |
| 300s     | 0.1   | 7s   | Low |
| 3600s    | 0.1   | 70s  | Low |

### Display Overhead
- Animation adds ~20-30% overhead
- Larger figures = more overhead
- Smaller `interval` = more overhead

## Integration with Control Design

### Parameter Tuning Workflow
1. Create controller with initial gains
2. Run animation to visualize behavior
3. Adjust gains based on observations
4. Repeat until satisfied

### Comparison Workflow
```python
scenarios = [
    {"name": "Conservative", "Kp": 1.0},
    {"name": "Moderate", "Kp": 2.0},
    {"name": "Aggressive", "Kp": 3.0},
]

for scenario in scenarios:
    sim = create_simulator(Kp=scenario['Kp'])
    animate_simulation(sim, duration=60, show_plot=True)
    # User can visually compare
```

## Best Practices

1. **Start with simple_animation.py** for quick results
2. **Use appropriate time scales** for the phenomena you're studying
3. **Export data** for post-processing and archiving
4. **Adjust visualization parameters** based on your needs
5. **Monitor CPU usage** for long simulations
6. **Use setpoints wisely** - realistic targets improve visualization

## Further Resources

- See [examples/](../examples/) for working code
- Check [README.md](../README.md) for full documentation
- Review [TIPS_AND_TRICKS.md](../TIPS_AND_TRICKS.md) for advanced usage

## Summary

The animation module provides an excellent way to:
- Visualize control system behavior
- Tune controller parameters intuitively
- Communicate results clearly
- Verify simulation correctness
- Understand system dynamics

Happy animating! 🎬
