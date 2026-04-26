"""Single tank model for the quadruple tanks system."""

import numpy as np
from dataclasses import dataclass


@dataclass
class TankConfig:
    """Configuration parameters for a tank."""
    
    diameter: float = 10.0  # cm, diameter of the tank
    area: float = None  # cm^2, cross-sectional area
    height_max: float = 100.0  # cm, maximum tank height
    outflow_coefficient: float = 0.5  # dimensionless, outflow coefficient
    gravity: float = 981.0  # cm/s^2, acceleration due to gravity
    
    def __post_init__(self):
        """Calculate area from diameter if not provided."""
        if self.area is None:
            radius = self.diameter / 2.0
            self.area = np.pi * (radius ** 2)


class Tank:
    """
    Model of a single tank with inflow and outflow dynamics.
    
    The tank dynamics are described by:
    dh/dt = (Q_in - Q_out) / A
    
    Where:
    - h: liquid height in the tank [cm]
    - Q_in: inflow volumetric flow rate [cm^3/s]
    - Q_out: outflow volumetric flow rate [cm^3/s]
    - A: cross-sectional area of the tank [cm^2]
    """
    
    def __init__(self, tank_id: int, config: TankConfig = None):
        """
        Initialize a tank.
        
        Args:
            tank_id: Unique identifier for the tank
            config: TankConfig object with tank parameters
        """
        self.tank_id = tank_id
        self.config = config if config is not None else TankConfig()
        
        # State variables
        self.height = 0.0  # Current liquid height [cm]
        self.outflow_area = 1.25  # Effective outflow area [cm^2]
        
    def get_outflow_rate(self) -> float:
        """
        Calculate outflow rate based on current height using Torricelli's law.
        
        Q_out = C * a * sqrt(2 * g * h)
        
        Returns:
            Outflow rate [cm^3/s]
        """
        if self.height <= 0:
            return 0.0
        
        outflow = (
            self.config.outflow_coefficient
            * self.outflow_area
            * np.sqrt(2 * self.config.gravity * self.height)
        )
        return outflow
    
    def update(self, inflow_rate: float, dt: float, outflow_multiplier: float = 1.0) -> float:
        """
        Update tank state using Euler integration.
        
        Args:
            inflow_rate: Inflow rate to the tank [cm^3/s]
            dt: Time step [s]
            outflow_multiplier: Multiplier for outflow (e.g. valve opening)
            
        Returns:
            New height of the tank [cm]
        """
        outflow_rate = self.get_outflow_rate() * outflow_multiplier
        
        # Height differential equation
        dh_dt = (inflow_rate - outflow_rate) / self.config.area
        
        # Update height using Euler method
        self.height += dh_dt * dt
        
        # Enforce physical constraints
        self.height = np.clip(self.height, 0.0, self.config.height_max)
        
        return self.height
    
    def reset(self, initial_height: float = 0.0) -> None:
        """
        Reset tank to initial state.
        
        Args:
            initial_height: Initial liquid height [cm]
        """
        self.height = np.clip(initial_height, 0.0, self.config.height_max)
    
    def get_state(self) -> dict:
        """
        Get current tank state.
        
        Returns:
            Dictionary with tank state variables
        """
        return {
            "tank_id": self.tank_id,
            "height": self.height,
            "outflow_rate": self.get_outflow_rate(),
            "max_height": self.config.height_max,
        }
