import matplotlib
matplotlib.use('Agg')
from quadruple_tanks import QuadrupleTanksSystem, PIDController, PIDGains, Simulator
from quadruple_tanks.animation import TankAnimator

def main():
    print("Setting up system...")
    system = QuadrupleTanksSystem()
    # TODO: Tune these gains to achieve desired performance
    gains = PIDGains(Kp=0.0, Ki=0.0, Kd=0.0)
    controller1 = PIDController(gains=gains)
    controller2 = PIDController(gains=gains)
    
    sim = Simulator(
        system=system,
        controller1=controller1,
        controller2=controller2,
        dt=0.1
    )
    
    print("Creating animator...")
    animator = TankAnimator(simulator=sim, figsize=(12, 7))
    
    print("Animating for 30 seconds...")
    anim = animator.animate(
        duration=30.0,
        setpoint1=12.0,
        setpoint2=12.0,
        interval=100
    )
    
    print("Saving to GIF...")
    anim.save("quadruple_tanks_animation.gif", writer="pillow", fps=10)
    print("Done!")

if __name__ == "__main__":
    main()
