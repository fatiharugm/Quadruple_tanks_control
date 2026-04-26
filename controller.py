"""
STUDENT CONTROLLER TEMPLATE
---------------------------
PUMP-BASED CONTROL ARCHITECTURE (NEW)
Use this file to implement your own pump flow control algorithm for the Quadruple Tanks System.

SYSTEM OVERVIEW (PUMP CONTROL):
  - Pump 1 flow (u1): Variable pump feeding Tank 1 (0-300 cm³/s) [controlled]
  - Pump 2 flow (u2): Variable pump feeding Tank 2 (0-300 cm³/s) [controlled]
  - Upper-to-Lower coupling: Fixed at u14=0.7, u23=0.7 (creates passive coupling disturbances)
  - Lower tank drains: Fixed at u3=0.5, u4=0.5 (passive outlets)

KEY ADVANTAGES over valve control:
  - Simpler system: Only 2 control inputs instead of 4
  - Direct actuation: Pump flow directly controls upper tank levels
  - Decoupled channels: Pump 1 → Tank 1, Pump 2 → Tank 2 (no cross-interference)
  - Better tuning: Standard PID gains work well

CONTROL STRATEGY:
  - Pump controllers regulate UPPER tank heights (h1, h2) only
  - Lower tank heights (h3, h4) passively follow due to coupling
  - Much simpler than trying to regulate lower tanks with 4 valves

TUNING NOTES:
  - Pump flow error range: 0-100 cm (tank height target) maps to 0-300 cm³/s (pump flow)
  - Equilibrium pump flow at 75cm: approximately 200-250 cm³/s (depends on outflow rate)
  - A bias of 250 cm³/s is reasonable starting point for 75cm setpoint
  - Kp should be larger than valve control since output range is larger
  - Anti-windup clamps the integral to prevent saturation on startup
"""

import numpy as np


class PumpController:
    """
    PID controller for PUMP FLOW inputs.
    
    Regulates tank height by modulating pump flow (0 to max_flow cm³/s).
    This is MUCH SIMPLER than valve-based control!
    
    Positive error (tank too low) -> increase pump flow -> more inflow.
    Negative error (tank too high) -> decrease pump flow -> less inflow.
    
    Output range: [0.0, max_pump_flow] cm³/s
    """

    def __init__(self, max_pump_flow: float = 300.0):
        """
        Initialize pump controller.
        
        Args:
            max_pump_flow: Maximum pump capacity [cm³/s], default 300
        """
        self.max_pump_flow = max_pump_flow
        
        # --- Tune these gains! ---
        # For pump control, we can use larger gains since output range is large (0-300 cm³/s)
        self.Kp = 1.5           # proportional gain (larger than valve control)
        self.Ki = 0.15          # integral gain (accumulates correction)
        self.Kd = 0.5           # derivative gain (damps oscillations)
        
        # Equilibrium bias: pump flow at setpoint (assume linear dynamics near 75cm)
        # At 75cm with Torricelli: outflow ≈ Cd*A*sqrt(2*g*h) 
        # For typical tank: ~200-250 cm³/s at 75cm
        # Using 250 as a good starting point
        self.bias = 250.0       # cm³/s (equilibrium pump flow)
        
        self.integral_error = 0.0
        self.integral_max = 100.0  # anti-windup clamp (larger range than valve control)
        self.previous_error = 0.0
        self.previous_time = None

    def update(self, setpoint: float, measurement: float, time: float) -> float:
        """
        Compute pump flow command using PID.
        
        Args:
            setpoint: Desired tank height [cm]
            measurement: Current tank height [cm]
            time: Simulation time [s]
            
        Returns:
            Pump flow command [cm³/s], clipped to [0, max_pump_flow]
        """
        error = setpoint - measurement  # Positive when tank too low
        
        # Proportional term
        p_term = self.Kp * error
        
        # Integral term with anti-windup
        self.integral_error = np.clip(
            self.integral_error + error, 
            -self.integral_max / self.Ki, 
            self.integral_max / self.Ki
        )
        i_term = self.Ki * self.integral_error
        
        # Derivative term (with time-based calculation)
        d_term = 0.0
        if self.previous_time is not None:
            dt = time - self.previous_time
            if dt > 0:
                d_term = self.Kd * (error - self.previous_error) / dt
        
        self.previous_error = error
        self.previous_time = time
        
        # Compute pump flow command
        pump_flow = self.bias + p_term + i_term + d_term
        
        # Clip to valid range [0, max_pump_flow]
        return float(np.clip(pump_flow, 0.0, self.max_pump_flow))
    
    def reset(self):
        """Reset controller state."""
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.previous_time = None


# ============================================================================
# LEGACY VALVE-BASED CONTROLLERS (Deprecated - kept for backward compatibility)
# ============================================================================


class InletController:
    """
    PID controller for INLET valves (u13, u24).
    Positive error (tank too low) -> opens valve -> more inflow.
    Output range: [0.0, 1.0]
    """

    def __init__(self):
        # --- Tune these gains! ---
        self.Kp = 0.01         # strong proportional gain
        self.Ki = 0.0003       # integral gain
        self.Kd = 0.002        # derivative gain

        self.bias = 0.5        # equilibrium bias
        self.integral_error = 0.0
        self.integral_max = 0.3  # anti-windup clamp
        self.previous_error = 0.0
        self.previous_time = None

    def update(self, setpoint: float, measurement: float, time: float) -> float:
        error = setpoint - measurement

        p_term = self.Kp * error

        self.integral_error = np.clip(
            self.integral_error + error, -self.integral_max / self.Ki, self.integral_max / self.Ki
        )
        i_term = self.Ki * self.integral_error

        d_term = 0.0
        if self.previous_time is not None:
            dt = time - self.previous_time
            if dt > 0:
                d_term = self.Kd * (error - self.previous_error) / dt

        self.previous_error = error
        self.previous_time = time

        u = self.bias + p_term + i_term + d_term
        return float(np.clip(u, 0.0, 1.0))

    def reset(self):
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.previous_time = None


class DrainController:
    """
    PID controller for DRAIN/OUTLET valves (u3, u4).
    Positive error (tank too low) -> CLOSES valve -> less outflow -> level rises.
    Output range: [0.0, 1.0]
    """

    def __init__(self):
        # --- Tune these gains! ---
        self.Kp = 0.01         # strong proportional gain
        self.Ki = 0.0003       # integral gain
        self.Kd = 0.002        # derivative gain

        self.bias = 0.5        # equilibrium bias
        self.integral_error = 0.0
        self.integral_max = 0.3  # anti-windup clamp
        self.previous_error = 0.0
        self.previous_time = None

    def update(self, setpoint: float, measurement: float, time: float) -> float:
        error = setpoint - measurement  # positive when tank is too low

        p_term = self.Kp * error

        self.integral_error = np.clip(
            self.integral_error + error, -self.integral_max / self.Ki, self.integral_max / self.Ki
        )
        i_term = self.Ki * self.integral_error

        d_term = 0.0
        if self.previous_time is not None:
            dt = time - self.previous_time
            if dt > 0:
                d_term = self.Kd * (error - self.previous_error) / dt

        self.previous_error = error
        self.previous_time = time

        # INVERTED: subtract correction so low tank closes drain
        u = self.bias - (p_term + i_term + d_term)
        return float(np.clip(u, 0.0, 1.0))

    def reset(self):
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.previous_time = None


# Default alias — students start with InletController
StudentController = InletController
