"""
STUDENT CONTROLLER TEMPLATE
---------------------------
MULTI-INPUT CONTROL ARCHITECTURE

SYSTEM OVERVIEW:
  - Pump 1 (u1): Variable pump feeding Tank 1 (0-300 cm³/s) [controlled]
  - Pump 2 (u2): Variable pump feeding Tank 2 (0-300 cm³/s) [controlled]
  - Drain Valve 3 (u3): Outlet valve for Tank 3 (0-1.0 normalized) [controlled]
  - Drain Valve 4 (u4): Outlet valve for Tank 4 (0-1.0 normalized) [controlled]

CONTROL INPUTS:
  1. Pump Controller (u1): Controls Tank 1 via pump flow
  2. Pump Controller (u2): Controls Tank 2 via pump flow
  3. Valve Controller (u3): Controls Tank 3 via drain valve
  4. Valve Controller (u4): Controls Tank 4 via drain valve

TUNING NOTES:
  - Each control input has its own set of gains (Kp, Ki, Kd, bias)
  - Pump outputs: [0, 300] cm³/s
  - Valve outputs: [0, 1.0] normalized position
  - Modify the gain values below to tune controller performance
"""

import numpy as np


class ControlGains:
    """Container for PID gain coefficients."""
    def __init__(self, Kp: float = 0.0, Ki: float = 0.0, Kd: float = 0.0, bias: float = 0.0):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.Kd = Kd  # Derivative gain
        self.bias = bias  # Equilibrium bias value


class MultiplexController:
    """
    Multi-input PID controller for quadruple tanks system.
    Manages 4 independent PID controllers (u1, u2 for pumps; u3, u4 for valves).
    """

    def __init__(self):
        """Initialize 4 independent PID controllers with individual gain sets."""
        
        # ============================================================
        # PUMP 1 (u1) - Controls Tank 1
        # ============================================================
        self.u1_gains = ControlGains(
            Kp=0.0,      # TODO: Tune pump 1 proportional gain
            Ki=0.0,      # TODO: Tune pump 1 integral gain
            Kd=0.0,      # TODO: Tune pump 1 derivative gain
            bias=0.0     # TODO: Set pump 1 equilibrium bias (cm³/s)
        )
        self.u1_max_flow = 300.0  # cm³/s
        self.u1_integral_error = 0.0
        self.u1_integral_max = 100.0
        self.u1_prev_error = 0.0
        self.u1_prev_time = None
        
        # ============================================================
        # PUMP 2 (u2) - Controls Tank 2
        # ============================================================
        self.u2_gains = ControlGains(
            Kp=0.0,      # TODO: Tune pump 2 proportional gain
            Ki=0.0,      # TODO: Tune pump 2 integral gain
            Kd=0.0,      # TODO: Tune pump 2 derivative gain
            bias=0.0     # TODO: Set pump 2 equilibrium bias (cm³/s)
        )
        self.u2_max_flow = 300.0  # cm³/s
        self.u2_integral_error = 0.0
        self.u2_integral_max = 100.0
        self.u2_prev_error = 0.0
        self.u2_prev_time = None
        
        # ============================================================
        # VALVE 3 (u3) - Drain valve for Tank 3
        # ============================================================
        self.u3_gains = ControlGains(
            Kp=0.0,      # TODO: Tune valve 3 proportional gain
            Ki=0.0,      # TODO: Tune valve 3 integral gain
            Kd=0.0,      # TODO: Tune valve 3 derivative gain
            bias=0.0     # TODO: Set valve 3 equilibrium bias (0-1)
        )
        self.u3_integral_error = 0.0
        self.u3_integral_max = 0.3
        self.u3_prev_error = 0.0
        self.u3_prev_time = None
        
        # ============================================================
        # VALVE 4 (u4) - Drain valve for Tank 4
        # ============================================================
        self.u4_gains = ControlGains(
            Kp=0.0,      # TODO: Tune valve 4 proportional gain
            Ki=0.0,      # TODO: Tune valve 4 integral gain
            Kd=0.0,      # TODO: Tune valve 4 derivative gain
            bias=0.0     # TODO: Set valve 4 equilibrium bias (0-1)
        )
        self.u4_integral_error = 0.0
        self.u4_integral_max = 0.3
        self.u4_prev_error = 0.0
        self.u4_prev_time = None

    def _pid_step(self, setpoint: float, measurement: float, time: float,
                  gains: ControlGains, integral_error: float, integral_max: float,
                  prev_error: float, prev_time: float, max_output: float) -> tuple:
        """
        Single PID step for one control channel.
        
        Returns: (output, integral_error)
        """
        error = setpoint - measurement
        
        # Proportional term
        p_term = gains.Kp * error
        
        # Integral term with anti-windup
        integral_error = np.clip(
            integral_error + error,
            -integral_max / (gains.Ki + 1e-9),  # Avoid division by zero
            integral_max / (gains.Ki + 1e-9)
        )
        i_term = gains.Ki * integral_error
        
        # Derivative term
        d_term = 0.0
        if prev_time is not None and time is not None:
            dt = time - prev_time
            if dt > 0:
                d_term = gains.Kd * (error - prev_error) / dt
        
        # Compute output
        output = gains.bias + p_term + i_term + d_term
        output = np.clip(output, 0.0, max_output)
        
        return float(output), integral_error, error, time

    def update(self, setpoint1: float, measurement1: float,
               setpoint2: float, measurement2: float,
               setpoint3: float, measurement3: float,
               setpoint4: float, measurement4: float,
               time: float) -> tuple:
        """
        Update all 4 controllers simultaneously.
        
        Args:
            setpoint1, measurement1: Tank 1 (controlled by pump u1)
            setpoint2, measurement2: Tank 2 (controlled by pump u2)
            setpoint3, measurement3: Tank 3 (controlled by valve u3)
            setpoint4, measurement4: Tank 4 (controlled by valve u4)
            time: Simulation time [s]
            
        Returns:
            (u1, u2, u3, u4) - tuple of control outputs
        """
        
        # Update pump u1
        u1, self.u1_integral_error, self.u1_prev_error, self.u1_prev_time = self._pid_step(
            setpoint1, measurement1, time,
            self.u1_gains, self.u1_integral_error, self.u1_integral_max,
            self.u1_prev_error, self.u1_prev_time, self.u1_max_flow
        )
        
        # Update pump u2
        u2, self.u2_integral_error, self.u2_prev_error, self.u2_prev_time = self._pid_step(
            setpoint2, measurement2, time,
            self.u2_gains, self.u2_integral_error, self.u2_integral_max,
            self.u2_prev_error, self.u2_prev_time, self.u2_max_flow
        )
        
        # Update valve u3
        u3, self.u3_integral_error, self.u3_prev_error, self.u3_prev_time = self._pid_step(
            setpoint3, measurement3, time,
            self.u3_gains, self.u3_integral_error, self.u3_integral_max,
            self.u3_prev_error, self.u3_prev_time, 1.0  # Valve range [0, 1]
        )
        
        # Update valve u4
        u4, self.u4_integral_error, self.u4_prev_error, self.u4_prev_time = self._pid_step(
            setpoint4, measurement4, time,
            self.u4_gains, self.u4_integral_error, self.u4_integral_max,
            self.u4_prev_error, self.u4_prev_time, 1.0  # Valve range [0, 1]
        )
        
        return u1, u2, u3, u4

    def reset(self):
        """Reset all controller states."""
        self.u1_integral_error = 0.0
        self.u1_prev_error = 0.0
        self.u1_prev_time = None
        
        self.u2_integral_error = 0.0
        self.u2_prev_error = 0.0
        self.u2_prev_time = None
        
        self.u3_integral_error = 0.0
        self.u3_prev_error = 0.0
        self.u3_prev_time = None
        
        self.u4_integral_error = 0.0
        self.u4_prev_error = 0.0
        self.u4_prev_time = None


# ============================================================================
# LEGACY PUMP CONTROLLER (Deprecated - kept for backward compatibility)
# ============================================================================


class PumpController:
    """
    DEPRECATED: Use MultiplexController instead.
    
    Legacy PID controller for PUMP FLOW inputs.
    Regulates tank height by modulating pump flow (0 to max_flow cm³/s).
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
        self.Kp = 0.0           # TODO: proportional gain
        self.Ki = 0.0           # TODO: integral gain
        self.Kd = 0.0           # TODO: derivative gain
        
        # Equilibrium bias: pump flow at setpoint
        self.bias = 0.0         # TODO: cm³/s (equilibrium pump flow)
        
        self.integral_error = 0.0
        self.integral_max = 100.0  # anti-windup clamp
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
            -self.integral_max / (self.Ki + 1e-9), 
            self.integral_max / (self.Ki + 1e-9)
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
    DEPRECATED: Use MultiplexController instead.
    
    PID controller for INLET valves (u13, u24).
    Positive error (tank too low) -> opens valve -> more inflow.
    Output range: [0.0, 1.0]
    """

    def __init__(self):
        # --- Tune these gains! ---
        self.Kp = 0.0         # strong proportional gain
        self.Ki = 0.0         # integral gain
        self.Kd = 0.0         # derivative gain

        self.bias = 0.0        # equilibrium bias
        self.integral_error = 0.0
        self.integral_max = 0.3  # anti-windup clamp
        self.previous_error = 0.0
        self.previous_time = None

    def update(self, setpoint: float, measurement: float, time: float) -> float:
        error = setpoint - measurement

        p_term = self.Kp * error
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
