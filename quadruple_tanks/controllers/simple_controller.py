"""Simple level controller implementation."""

import numpy as np


class SimpleLevelController:
    """
    Simple proportional-based level controller.
    
    This controller adjusts pump flow based on the difference between
    the desired and actual tank levels using a simple proportional rule.
    
    Control law:
    flow = base_flow + gain * (setpoint - measurement)
    """
    
    def __init__(self, gain: float = 1.0, base_flow: float = 0.0, 
                 output_limits: tuple = (0, 100)):
        """
        Initialize simple level controller.
        
        Args:
            gain: Proportional gain for level error
            base_flow: Base flow rate when error is zero [cm^3/s]
            output_limits: (min, max) limits for pump flow
        """
        self.gain = gain
        self.base_flow = base_flow
        self.output_limits = output_limits
    
    def update(self, setpoint: float, measurement: float) -> float:
        """
        Compute pump flow based on level error.
        
        Args:
            setpoint: Desired tank level [cm]
            measurement: Measured tank level [cm]
            
        Returns:
            Pump flow rate [cm^3/s]
        """
        # Calculate error
        error = setpoint - measurement
        
        # Proportional control
        flow = self.base_flow + self.gain * error
        
        # Apply output limits
        flow = np.clip(flow, self.output_limits[0], self.output_limits[1])
        
        return flow
    
    def set_gain(self, gain: float) -> None:
        """
        Update controller gain.
        
        Args:
            gain: New proportional gain
        """
        self.gain = gain
    
    def set_base_flow(self, base_flow: float) -> None:
        """
        Update base flow rate.
        
        Args:
            base_flow: New base flow rate [cm^3/s]
        """
        self.base_flow = base_flow
