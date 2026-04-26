"""Helper functions for analysis and visualization."""

import numpy as np
from typing import Dict, Tuple


def calculate_metrics(time_data: np.ndarray, 
                      response_data: np.ndarray,
                      setpoint: float) -> Dict:
    """
    Calculate performance metrics for a control response.
    
    Args:
        time_data: Time array
        response_data: System response data
        setpoint: Target setpoint
        
    Returns:
        Dictionary with performance metrics
    """
    # Steady-state error
    ss_error = abs(response_data[-1] - setpoint)
    
    # Overshoot
    max_response = np.max(response_data)
    if setpoint > 0:
        overshoot = max(0, (max_response - setpoint) / setpoint) * 100
    else:
        overshoot = 0
    
    # Settling time (within 2% of setpoint)
    threshold = 0.02 * setpoint
    settling_idx = np.where(
        np.abs(response_data - setpoint) <= threshold
    )[0]
    
    if len(settling_idx) > 0:
        settling_time = time_data[settling_idx[0]]
    else:
        settling_time = float('inf')
    
    # Rise time (10% to 90%)
    lower_threshold = 0.1 * setpoint
    upper_threshold = 0.9 * setpoint
    
    rise_start = np.where(response_data >= lower_threshold)[0]
    rise_end = np.where(response_data >= upper_threshold)[0]
    
    if len(rise_start) > 0 and len(rise_end) > 0:
        rise_time = time_data[rise_end[0]] - time_data[rise_start[0]]
    else:
        rise_time = float('inf')
    
    # Integral of Absolute Error (IAE)
    iae = np.trapz(
        np.abs(response_data - setpoint), 
        time_data
    )
    
    return {
        "steady_state_error": ss_error,
        "overshoot_percent": overshoot,
        "settling_time": settling_time,
        "rise_time": rise_time,
        "integral_absolute_error": iae,
        "final_value": response_data[-1],
    }


def analyze_response(time_data: np.ndarray,
                     response_data: np.ndarray,
                     setpoint: float) -> str:
    """
    Generate text analysis of control response.
    
    Args:
        time_data: Time array
        response_data: System response data
        setpoint: Target setpoint
        
    Returns:
        Analysis text string
    """
    metrics = calculate_metrics(time_data, response_data, setpoint)
    
    analysis = f"""
Control Response Analysis
==========================
Setpoint: {setpoint:.2f} cm
Final Value: {metrics['final_value']:.2f} cm
Steady-State Error: {metrics['steady_state_error']:.4f} cm
Overshoot: {metrics['overshoot_percent']:.2f}%
Rise Time: {metrics['rise_time']:.3f} s
Settling Time: {metrics['settling_time']:.3f} s
Integral Absolute Error: {metrics['integral_absolute_error']:.4f}
"""
    return analysis.strip()


def plot_results(time_data: np.ndarray,
                 heights_data: Dict[int, np.ndarray],
                 pump_data: Dict[str, np.ndarray],
                 setpoint_data: Dict[str, np.ndarray],
                 show: bool = True) -> None:
    """
    Plot simulation results.
    
    Args:
        time_data: Time array
        heights_data: Dictionary with tank heights {1: array, 2: array, ...}
        pump_data: Dictionary with pump flows {"pump1": array, "pump2": array}
        setpoint_data: Dictionary with setpoints {"tank1": array, "tank2": array}
        show: Whether to display the plot
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed. Install it with: pip install matplotlib")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot tank heights
    ax = axes[0, 0]
    ax.plot(time_data, heights_data[1], 'b-', label='Tank 1', linewidth=2)
    ax.plot(time_data, heights_data[2], 'r-', label='Tank 2', linewidth=2)
    ax.plot(time_data, setpoint_data["tank1"], 'b--', alpha=0.5, label='Setpoint 1')
    ax.plot(time_data, setpoint_data["tank2"], 'r--', alpha=0.5, label='Setpoint 2')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Height (cm)')
    ax.set_title('Upper Tank Levels')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Plot lower tank heights
    ax = axes[0, 1]
    ax.plot(time_data, heights_data[3], 'g-', label='Tank 3', linewidth=2)
    ax.plot(time_data, heights_data[4], 'm-', label='Tank 4', linewidth=2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Height (cm)')
    ax.set_title('Lower Tank Levels')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Plot pump flows
    ax = axes[1, 0]
    ax.plot(time_data, pump_data["pump1"], 'b-', label='Pump 1', linewidth=2)
    ax.plot(time_data, pump_data["pump2"], 'r-', label='Pump 2', linewidth=2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Flow Rate (cm³/s)')
    ax.set_title('Pump Flows')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Plot all tank heights
    ax = axes[1, 1]
    ax.plot(time_data, heights_data[1], 'b-', label='Tank 1', linewidth=1.5)
    ax.plot(time_data, heights_data[2], 'r-', label='Tank 2', linewidth=1.5)
    ax.plot(time_data, heights_data[3], 'g-', label='Tank 3', linewidth=1.5)
    ax.plot(time_data, heights_data[4], 'm-', label='Tank 4', linewidth=1.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Height (cm)')
    ax.set_title('All Tank Levels')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig
