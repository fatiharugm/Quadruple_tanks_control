"""
Quadruple Tanks Control System Package

A comprehensive control system simulation package for the classic quadruple tanks system.
"""

from .models import Tank, QuadrupleTanksSystem
from .controllers import PIDController, SimpleLevelController, PIDGains
from .simulation import Simulator
from .animation import TankAnimator, animate_simulation

__version__ = "0.1.0"
__author__ = "Control Systems"

__all__ = [
    "Tank",
    "QuadrupleTanksSystem",
    "PIDController",
    "PIDGains",
    "SimpleLevelController",
    "Simulator",
    "TankAnimator",
    "animate_simulation",
]
