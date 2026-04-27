"""Test suite for quadruple tanks control system."""

import pytest
import numpy as np
from quadruple_tanks.models import Tank, QuadrupleTanksSystem, TankConfig
from quadruple_tanks.simulation import Simulator


class TestTank:
    """Test cases for Tank model."""
    
    def test_tank_creation(self):
        """Test tank creation with default config."""
        tank = Tank(tank_id=1)
        assert tank.tank_id == 1
        assert tank.height == 0.0
    
    def test_tank_with_custom_config(self):
        """Test tank with custom configuration."""
        config = TankConfig(diameter=15.0, height_max=25.0)
        tank = Tank(tank_id=2, config=config)
        assert tank.config.height_max == 25.0
    
    def test_tank_update(self):
        """Test tank height update."""
        tank = Tank(tank_id=1)
        initial_height = tank.height
        tank.update(inflow_rate=50.0, dt=1.0)
        assert tank.height > initial_height
    
    def test_tank_height_constraint(self):
        """Test that tank height is constrained."""
        config = TankConfig(height_max=20.0)
        tank = Tank(tank_id=1, config=config)
        tank.update(inflow_rate=1000.0, dt=1.0)
        assert tank.height <= config.height_max
    
    def test_tank_outflow_rate(self):
        """Test outflow rate calculation."""
        tank = Tank(tank_id=1)
        tank.height = 0.0
        assert tank.get_outflow_rate() == 0.0
        
        tank.height = 10.0
        outflow = tank.get_outflow_rate()
        assert outflow > 0.0


class TestPIDController:
    """Test cases for PID controller."""
    
    def test_pid_creation(self):
        """Test PID controller creation."""
        gains = PIDGains(Kp=2.0, Ki=0.1, Kd=0.05)
        controller = PIDController(gains=gains)
        assert controller.gains.Kp == 2.0
    
    def test_pid_update(self):
        """Test PID update step."""
        controller = PIDController()
        output = controller.update(setpoint=10.0, measurement=5.0, time=0.0)
        assert isinstance(output, (int, float))
    
    def test_pid_output_limits(self):
        """Test PID output limiting."""
        controller = PIDController(output_limits=(0, 100))
        output = controller.update(setpoint=100.0, measurement=0.0, time=0.0)
        assert output <= 100.0
    
    def test_pid_reset(self):
        """Test PID controller reset."""
        controller = PIDController()
        controller.update(setpoint=10.0, measurement=0.0, time=0.0)
        controller.reset()
        assert controller.integral_error == 0.0
        assert controller.previous_error == 0.0


class TestSimpleLevelController:
    """Test cases for simple level controller."""
    
    def test_simple_controller_creation(self):
        """Test simple controller creation."""
        controller = SimpleLevelController(gain=1.0, base_flow=10.0)
        assert controller.gain == 1.0
        assert controller.base_flow == 10.0
    
    def test_simple_controller_update(self):
        """Test simple controller update."""
        controller = SimpleLevelController(gain=1.0)
        flow = controller.update(setpoint=10.0, measurement=5.0)
        assert flow > 0.0


class TestQuadrupleTanksSystem:
    """Test cases for quadruple tanks system."""
    
    def test_system_creation(self):
        """Test system creation."""
        system = QuadrupleTanksSystem()
        assert len(system.tanks) == 4
    
    def test_system_pump_inputs(self):
        """Test setting pump inputs."""
        system = QuadrupleTanksSystem()
        system.set_pump_inputs(50.0, 75.0)
        assert system.pump1_flow == 50.0
        assert system.pump2_flow == 75.0
    
    def test_system_pump_limits(self):
        """Test pump input limiting."""
        system = QuadrupleTanksSystem()
        system.set_pump_inputs(200.0, -50.0)
        assert system.pump1_flow <= system.pump1_max_flow
        assert system.pump2_flow >= 0.0
    
    def test_system_update(self):
        """Test system update."""
        system = QuadrupleTanksSystem()
        system.set_pump_inputs(50.0, 50.0)
        heights_before = system.get_heights()
        system.update(dt=1.0)
        heights_after = system.get_heights()
        assert heights_after[1] > heights_before[1]
    
    def test_system_reset(self):
        """Test system reset."""
        system = QuadrupleTanksSystem()
        system.set_pump_inputs(50.0, 50.0)
        system.update(dt=1.0)
        system.reset()
        assert system.get_height(1) == 0.0
        assert system.pump1_flow == 0.0


class TestSimulator:
    """Test cases for simulator."""
    
    def test_simulator_creation(self):
        """Test simulator creation."""
        system = QuadrupleTanksSystem()
        controller1 = PIDController()
        sim = Simulator(system=system, controller1=controller1)
        assert sim.dt == 0.1
    
    def test_simulator_setpoints(self):
        """Test setting simulator setpoints."""
        sim = Simulator()
        sim.set_setpoints(15.0, 12.0)
        assert sim.setpoint1 == 15.0
        assert sim.setpoint2 == 12.0
    
    def test_simulator_step(self):
        """Test single simulator step."""
        sim = Simulator()
        state_before = sim.current_time
        sim.step()
        assert sim.current_time > state_before
    
    def test_simulator_run(self):
        """Test simulator run."""
        sim = Simulator()
        time_data, state_data = sim.run(duration=10.0)
        assert len(time_data) > 0
        assert len(state_data["heights"][1]) > 0
    
    def test_simulator_reset(self):
        """Test simulator reset."""
        sim = Simulator()
        sim.run(duration=5.0)
        sim.reset()
        assert sim.current_time == 0.0
        assert len(sim.time_data) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
