"""Main entry point for quadruple tanks package."""

from quadruple_tanks import (
    Tank,
    QuadrupleTanksSystem,
    PIDController,
    SimpleLevelController,
    Simulator,
    TankAnimator,
    animate_simulation,
)

if __name__ == "__main__":
    print("Quadruple Tanks Control System Package")
    print("=====================================\n")
    
    print("Available Classes:")
    print("  - Tank: Single tank model")
    print("  - QuadrupleTanksSystem: 4-tank system")
    print("  - PIDController: PID control algorithm")
    print("  - SimpleLevelController: Simple proportional controller")
    print("  - Simulator: Main simulation framework")
    print("  - TankAnimator: Real-time tank visualization")
    
    print("\nAvailable Functions:")
    print("  - animate_simulation(): Quick animation setup")
    
    print("\nTo run examples:")
    print("  python examples/quick_start.py         - Quick overview")
    print("  python examples/basic_control.py       - Basic control demo")
    print("  python examples/gain_tuning.py         - Parameter tuning")
    print("  python examples/simple_animation.py    - Animation with plots")
    print("  python examples/animation_demo.py      - Interactive animation")
    
    print("\nDocumentation:")
    print("  - README.md              - Full package documentation")
    print("  - ANIMATION_GUIDE.md     - Animation features guide")
    print("  - TIPS_AND_TRICKS.md     - Advanced usage patterns")
    print("  - PROJECT_OVERVIEW.md    - Project structure")

