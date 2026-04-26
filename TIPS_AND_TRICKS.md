# Tips & Tricks for Quadruple Tanks Control System

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Optional: Visualization
For plots and graphs:
```bash
pip install matplotlib
```

### Optional: Testing
To run the test suite:
```bash
pip install pytest pytest-cov
pytest tests/
```

## Common Usage Patterns

### Pattern 1: Simple Control Run
```python
from quadruple_tanks import QuadrupleTanksSystem, PIDController, Simulator, PIDGains

# Create components
system = QuadrupleTanksSystem()
controller = PIDController(gains=PIDGains(Kp=2.0, Ki=0.1, Kd=0.05))
sim = Simulator(system=system, controller1=controller)

# Run and export
time_data, state = sim.run(duration=50, setpoint1=10.0)
sim.export_data("results.csv")
```

### Pattern 2: Multi-Setpoint Control
```python
# Run in phases with different setpoints
for setpoint in [5.0, 10.0, 15.0]:
    sim.set_setpoints(setpoint, setpoint)
    for _ in range(100):  # 10 seconds at dt=0.1
        sim.step()
```

### Pattern 3: Performance Comparison
```python
from quadruple_tanks.utils import calculate_metrics

gains_list = [
    PIDGains(Kp=1.0, Ki=0.05, Kd=0.02),
    PIDGains(Kp=2.0, Ki=0.1, Kd=0.05),
    PIDGains(Kp=3.0, Ki=0.2, Kd=0.1),
]

for gains in gains_list:
    controller = PIDController(gains=gains)
    sim = Simulator(system=QuadrupleTanksSystem(), controller1=controller)
    time_data, state = sim.run(duration=50, setpoint1=10.0)
    
    metrics = calculate_metrics(time_data, state["heights"][1], 10.0)
    print(f"Kp={gains.Kp}: Overshoot={metrics['overshoot_percent']:.1f}%")
```

## PID Tuning Tips

### Starting Gains
```python
# Conservative (good stability, slow response)
Kp = 1.0, Ki = 0.05, Kd = 0.02

# Moderate (balanced)
Kp = 2.0, Ki = 0.1, Kd = 0.05

# Aggressive (fast response, may overshoot)
Kp = 3.0, Ki = 0.2, Kd = 0.1
```

### Tuning Strategy
1. **Start with Kp only** (Ki=0, Kd=0)
   - Increase until oscillation appears
   - Back off to ~70% of that value

2. **Add Ki for steady-state error**
   - Small value first (1/10 of Kp)
   - Increase until error removed in reasonable time

3. **Add Kd for stability**
   - Start at 10% of Kp
   - Adjust to eliminate oscillation

### Performance Metrics
```python
from quadruple_tanks.utils import calculate_metrics

metrics = calculate_metrics(time_data, response, setpoint=10.0)

# Check these:
# - overshoot_percent: Should be < 20% for good control
# - settling_time: Lower is better (usually < 30s)
# - steady_state_error: Should approach 0
# - integral_absolute_error: Lower is better overall
```

## Simulation Tips

### Time Step Selection
```python
# Smaller dt = more accuracy, slower simulation
sim = Simulator(dt=0.01)  # Fine resolution

# Larger dt = faster, less accurate
sim = Simulator(dt=0.5)   # Coarse resolution

# Sweet spot for this system
sim = Simulator(dt=0.1)   # Default, good balance
```

### Simulation Duration
```python
# Quick test: 10-20 seconds
sim.run(duration=20)

# Typical analysis: 50-100 seconds
sim.run(duration=100)

# Long-term behavior: 200+ seconds
sim.run(duration=300)
```

### Data Export
```python
# Export to CSV for post-processing
sim.export_data("my_results.csv")

# Process in Excel, Python, MATLAB, etc.
import pandas as pd
data = pd.read_csv("my_results.csv")
```

## Advanced Techniques

### Custom System Parameters
```python
from quadruple_tanks.models import TankConfig

# Modify tank properties
custom_config = TankConfig(
    diameter=15.0,      # Larger tank
    height_max=25.0,    # Taller tank
    outflow_coefficient=0.6  # More efficient outflow
)

system = QuadrupleTanksSystem(tank_config=custom_config)
```

### Monitoring During Simulation
```python
# Step-by-step with monitoring
sim = Simulator()
for i in range(1000):
    sim.step()
    
    if i % 100 == 0:  # Every 10 seconds
        state = sim.get_current_state()
        print(f"Time: {state['time']:.1f}s, "
              f"H1: {state['heights'][1]:.2f}cm")
```

### Batch Simulations
```python
# Compare multiple scenarios
scenarios = [
    {"name": "Low gain", "Kp": 1.0},
    {"name": "High gain", "Kp": 3.0},
]

for scenario in scenarios:
    controller = PIDController(
        gains=PIDGains(Kp=scenario['Kp'], Ki=0.1, Kd=0.05)
    )
    sim = Simulator(system=QuadrupleTanksSystem(), 
                   controller1=controller)
    time_data, state = sim.run(duration=50, setpoint1=10.0)
    sim.export_data(f"results_{scenario['name']}.csv")
```

## Troubleshooting

### Issue: Controllers not responding
```python
# Check controller gains are set
controller.set_gains(Kp=2.0, Ki=0.1, Kd=0.05)

# Verify controller is passed to simulator
sim = Simulator(system=system, controller1=controller1, 
               controller2=controller2)  # Don't forget!
```

### Issue: Tanks not filling
```python
# Increase pump flow or controller gain
system.pump1_max_flow = 150  # Increase from 100
# OR
controller.set_gains(Kp=3.0, Ki=0.2, Kd=0.1)  # More aggressive
```

### Issue: Oscillations/Instability
```python
# Reduce controller gain
controller.set_gains(Kp=1.0, Ki=0.05, Kd=0.02)

# Or increase derivative term
controller.set_gains(Kp=2.0, Ki=0.1, Kd=0.1)
```

### Issue: Memory issues with long simulations
```python
# Run shorter simulations and export frequently
for hour in range(24):
    sim = Simulator()
    sim.run(duration=3600)  # 1 hour
    sim.export_data(f"hour_{hour}.csv")
    sim.reset()
```

## Visualization Tips

### Basic Plotting
```python
from quadruple_tanks.utils import plot_results

time_data, state = sim._get_simulation_data()
plot_results(time_data, state["heights"], 
            state["pumps"], state["setpoints"])
```

### Custom Analysis
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(time_data, state["heights"][1], label="Tank 1")
ax.axhline(y=10.0, color='r', linestyle='--', label="Setpoint")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Height (cm)")
ax.legend()
plt.show()
```

## Performance Optimization

### For Real-Time Simulation
```python
# Use larger time step for speed
sim = Simulator(dt=0.5)

# Reduce frequency of data recording
# (by stepping multiple times before recording)
for _ in range(10):
    sim.step()
```

### For Accuracy
```python
# Use smaller time step
sim = Simulator(dt=0.01)

# Run longer simulations
duration = 200  # seconds
```

## Resources

- **README.md**: Full documentation
- **examples/**: Working code examples
- **tests/**: Test cases showing usage
- **Quick start**: `python quick_start.py`

## Common Parameters to Adjust

| Parameter | Effect | Typical Range |
|-----------|--------|----------------|
| Kp (Proportional) | Response speed | 0.5 - 5.0 |
| Ki (Integral) | Steady-state error | 0.01 - 0.5 |
| Kd (Derivative) | Oscillation damping | 0.01 - 0.2 |
| dt (Time step) | Accuracy vs speed | 0.01 - 0.5 |
| Pump max flow | System capability | 50 - 200 cm³/s |
| Tank height max | Physical limits | 10 - 30 cm |

## Getting Help

1. Check docstrings: `help(QuadrupleTanksSystem)`
2. Run examples: `python examples/basic_control.py`
3. Review tests: `cat tests/test_quadruple_tanks.py`
4. Check README: `cat README.md`

Happy controlling! 🚀
