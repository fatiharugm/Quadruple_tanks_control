"""PID Controller implementation."""

import numpy as np
from dataclasses import dataclass


@dataclass
class PIDGains:
    """PID controller gains."""
    
    Kp: float = 1.0  # Proportional gain
    Ki: float = 0.1  # Integral gain
    Kd: float = 0.01  # Derivative gain


class PIDController:
    """
    PID (Proportional-Integral-Derivative) controller.
    
    The control law is:
    u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt
    
    Where:
    - e(t) = setpoint - measurement
    - u(t) = control input
    """
    
    def __init__(self, gains: PIDGains = None, output_limits: tuple = (0, 100)):
        """
        Initialize PID controller.
        
        Args:
            gains: PIDGains object with controller gains
            output_limits: (min, max) limits for controller output
        """
        self.gains = gains if gains is not None else PIDGains()
        self.output_limits = output_limits
        
        # State variables
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.previous_time = None
        
    def update(self, setpoint: float, measurement: float, time: float = None) -> float:
        """
        Compute control output based on error.
        
        Args:
            setpoint: Desired value
            measurement: Measured value
            time: Current time (for derivative calculation)
            
        Returns:
            Control output (clipped to output_limits)
        """
        # Calculate error
        error = setpoint - measurement
        
        # Proportional term
        p_term = self.gains.Kp * error
        
        # Integral term
        self.integral_error += error
        i_term = self.gains.Ki * self.integral_error
        
        # Derivative term
        d_term = 0.0
        if self.previous_time is not None and time is not None:
            dt = time - self.previous_time
            if dt > 0:
                d_term = self.gains.Kd * (error - self.previous_error) / dt
        
        # Compute output
        output = p_term + i_term + d_term
        
        # Apply output limits
        output = np.clip(output, self.output_limits[0], self.output_limits[1])
        
        # Update state
        self.previous_error = error
        self.previous_time = time
        
        return output
    
    def reset(self) -> None:
        """Reset controller state."""
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.previous_time = None
    
    def set_gains(self, Kp: float, Ki: float, Kd: float) -> None:
        """
        Update controller gains.
        
        Args:
            Kp: Proportional gain
            Ki: Integral gain
            Kd: Derivative gain
        """
        self.gains.Kp = Kp
        self.gains.Ki = Ki
        self.gains.Kd = Kd
