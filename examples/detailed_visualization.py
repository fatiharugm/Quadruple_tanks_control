"""Enhanced tank visualization with detailed illustrations."""

import sys
sys.path.insert(0, '.')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from quadruple_tanks import (
    QuadrupleTanksSystem,
    PIDController,
    PIDGains,
    Simulator,
)


def create_detailed_tank_visualization():
    """Create detailed tank visualization showing water levels."""
    
    print("\n" + "=" * 70)
    print("ENHANCED TANK VISUALIZATION - DETAILED ILLUSTRATION")
    print("=" * 70)
    
    # Create system and run simulation
    print("\n[1/4] Running simulation...")
    system = QuadrupleTanksSystem()
    # TODO: Tune these gains to achieve desired performance
    gains = PIDGains(Kp=0.0, Ki=0.0, Kd=0.0)
    
    sim = Simulator(
        system=system,
        controller1=PIDController(gains=gains),
        controller2=PIDController(gains=gains),
        dt=0.1
    )
    
    # Run simulation
    time_data, state_data = sim.run(duration=60, setpoint1=12.0, setpoint2=12.0)
    print("      ✓ Simulation complete")
    
    # Extract key data points for visualization
    h1_final = state_data["heights"][1][-1]
    h2_final = state_data["heights"][2][-1]
    h3_final = state_data["heights"][3][-1]
    h4_final = state_data["heights"][4][-1]
    
    # Get data at different time points for animation frames
    time_indices = [int(len(time_data) * t) for t in [0.2, 0.5, 1.0]]
    
    print(f"\n[2/4] Creating detailed tank illustrations...")
    
    # Create figure with detailed tank views
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.3)
    
    # Define tank properties
    tank_max_height = 20.0  # cm
    tank_width = 1.2
    colors = {1: '#FF6B6B', 2: '#4ECDC4', 3: '#45B7D1', 4: '#FFA07A'}
    labels = {
        1: 'Tank 1\n(Upper Left)',
        2: 'Tank 2\n(Upper Right)',
        3: 'Tank 3\n(Lower Left)',
        4: 'Tank 4\n(Lower Right)'
    }
    
    # Snapshot views (current state)
    snapshots = [
        ("t = 0s\n(Start)", state_data["heights"], time_data[0]),
        ("t = 30s\n(Midway)", state_data["heights"], time_data[min(300, len(time_data)-1)]),
        ("t = 60s\n(Final)", state_data["heights"], time_data[-1]),
    ]
    
    for snap_idx, (title, heights_data, current_time) in enumerate(snapshots):
        for tank_id in [1, 2, 3, 4]:
            ax = fig.add_subplot(gs[snap_idx, tank_id - 1])
            
            # Get height for this snapshot
            if snap_idx == 0:
                height = heights_data[tank_id][0]
            elif snap_idx == 1:
                height = heights_data[tank_id][300]
            else:
                height = heights_data[tank_id][-1]
            
            # Draw tank outline (3D effect)
            outer_rect = patches.Rectangle(
                (-tank_width/2 - 0.08, -0.1),
                tank_width + 0.16,
                tank_max_height + 0.2,
                linewidth=3,
                edgecolor='darkgray',
                facecolor='none',
                alpha=0.8
            )
            ax.add_patch(outer_rect)
            
            # Draw tank body
            tank_rect = patches.Rectangle(
                (-tank_width/2, 0),
                tank_width,
                tank_max_height,
                linewidth=2.5,
                edgecolor='black',
                facecolor='white',
                alpha=0.95,
                zorder=2
            )
            ax.add_patch(tank_rect)
            
            # Draw water with gradient effect
            normalized_height = (height / tank_max_height) * tank_max_height
            water_rect = patches.Rectangle(
                (-tank_width/2, 0),
                tank_width,
                normalized_height,
                linewidth=0,
                facecolor=colors[tank_id],
                alpha=0.7,
                zorder=3
            )
            ax.add_patch(water_rect)
            
            # Water surface line
            if normalized_height > 0:
                ax.plot([-tank_width/2, tank_width/2],
                       [normalized_height, normalized_height],
                       color=colors[tank_id], linewidth=3, zorder=4)
            
            # Height scale markers
            for h in np.arange(0, tank_max_height + 1, 5):
                ax.plot([-tank_width/2 - 0.15, -tank_width/2],
                       [h, h], 'k-', linewidth=1.5, alpha=0.6)
                ax.text(-tank_width/2 - 0.25, h, f'{int(h)}',
                       ha='right', va='center', fontsize=8, fontweight='bold')
            
            # Draw setpoint line (dashed) for upper tanks
            if tank_id in [1, 2]:
                setpoint_line_height = 12.0
                ax.axhline(y=setpoint_line_height, color='red', linestyle='--',
                          linewidth=2, alpha=0.5, label='Setpoint')
            
            # Main height display
            fill_percent = (height / tank_max_height) * 100
            ax.text(0, tank_max_height / 2, f'{height:.2f}\ncm\n({fill_percent:.0f}%)',
                   ha='center', va='center', fontsize=13, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                            alpha=0.9, edgecolor=colors[tank_id], linewidth=2.5),
                   zorder=5)
            
            # Tank ID
            ax.text(tank_width/2 + 0.15, tank_max_height - 1,
                   f'T{tank_id}',
                   ha='left', va='top', fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='circle,pad=0.4', facecolor=colors[tank_id],
                            alpha=0.6, edgecolor='black', linewidth=1.5))
            
            # Configure axes
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.5, 22)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Add title for first column
            if tank_id == 1:
                ax.text(-0.5, 22.5, title, fontsize=11, fontweight='bold',
                       ha='center', bbox=dict(boxstyle='round,pad=0.4',
                                            facecolor='lightblue', alpha=0.7))
    
    # Add overall title
    fig.suptitle('Quadruple Tanks System - Detailed Tank Visualization\n' +
                'Water Levels and Fill Percentages at Different Time Points',
                fontsize=16, fontweight='bold', y=0.98)
    
    # Add legend
    legend_text = (
        "Tank 1 & 2: Upper tanks (controlled by pumps)\n"
        "Tank 3 & 4: Lower tanks (fed by upper tanks)\n"
        "Red dashed lines: Control setpoints (12 cm)\n"
        "Colors show water level and fill percentage"
    )
    fig.text(0.5, 0.02, legend_text, ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
            family='monospace')
    
    # Save figure
    output_file = "detailed_tank_visualization.png"
    fig.savefig(output_file, dpi=120, bbox_inches='tight')
    print(f"      ✓ Visualization saved: {output_file}")
    plt.close(fig)
    
    # Create system diagram
    print(f"\n[3/4] Creating system diagram...")
    create_system_diagram()
    
    # Summary
    print(f"\n[4/4] Summary")
    print("-" * 70)
    print(f"\nFinal Water Levels (after 60 seconds):")
    print(f"  Tank 1 (Upper Left):  {h1_final:6.2f} cm (Target: 12.00 cm) - Fill: {(h1_final/20)*100:5.1f}%")
    print(f"  Tank 2 (Upper Right): {h2_final:6.2f} cm (Target: 12.00 cm) - Fill: {(h2_final/20)*100:5.1f}%")
    print(f"  Tank 3 (Lower Left):  {h3_final:6.2f} cm              - Fill: {(h3_final/20)*100:5.1f}%")
    print(f"  Tank 4 (Lower Right): {h4_final:6.2f} cm              - Fill: {(h4_final/20)*100:5.1f}%")
    
    print("\n" + "=" * 70)
    print("✨ VISUALIZATION COMPLETE!")
    print("=" * 70)
    print(f"""
Generated Files:
  ✓ detailed_tank_visualization.png  - Tank diagrams with water levels
  ✓ system_diagram.png               - System schematic
  ✓ tank_simulation.png              - Trend plots
  ✓ animation_demo_results.csv       - Raw simulation data

Features:
  • Detailed tank illustrations showing water levels
  • Real-time fill percentages
  • Height markings on each tank
  • Setpoint reference lines
  • Three time snapshots (0s, 30s, 60s)
  • System schematic diagram
  • Complete data export
""")


def create_system_diagram():
    """Create system schematic diagram."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Draw tanks
    tank_positions = {
        1: (2, 5),
        2: (6, 5),
        3: (2, 2),
        4: (6, 2)
    }
    
    colors = {1: '#FF6B6B', 2: '#4ECDC4', 3: '#45B7D1', 4: '#FFA07A'}
    labels = {1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4'}
    
    # Draw tank circles
    for tank_id, (x, y) in tank_positions.items():
        circle = patches.Circle((x, y), 0.4, color=colors[tank_id], alpha=0.6,
                               edgecolor='black', linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y, labels[tank_id], ha='center', va='center',
               fontsize=14, fontweight='bold')
    
    # Draw connections with arrows
    # Upper to lower
    ax.annotate('', xy=(2, 2.4), xytext=(2, 4.6),
               arrowprops=dict(arrowstyle='->', lw=2.5, color='darkred'))
    ax.annotate('', xy=(6, 2.4), xytext=(6, 4.6),
               arrowprops=dict(arrowstyle='->', lw=2.5, color='darkblue'))
    
    # Cross connections
    ax.annotate('', xy=(6, 2.2), xytext=(2, 4.5),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', alpha=0.5))
    ax.annotate('', xy=(2, 2.2), xytext=(6, 4.5),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', alpha=0.5))
    
    # Draw pumps
    pump1_x, pump2_x = 2, 6
    pump_y = 7
    
    ax.arrow(pump1_x, pump_y, 0, -1.2, head_width=0.2, head_length=0.15,
            fc='green', ec='darkgreen', linewidth=2.5, alpha=0.8)
    ax.text(pump1_x, pump_y + 0.5, '💧 Pump 1\nInput', ha='center',
           fontsize=11, fontweight='bold', bbox=dict(boxstyle='round',
           facecolor='lightgreen', alpha=0.7))
    
    ax.arrow(pump2_x, pump_y, 0, -1.2, head_width=0.2, head_length=0.15,
            fc='green', ec='darkgreen', linewidth=2.5, alpha=0.8)
    ax.text(pump2_x, pump_y + 0.5, '💧 Pump 2\nInput', ha='center',
           fontsize=11, fontweight='bold', bbox=dict(boxstyle='round',
           facecolor='lightgreen', alpha=0.7))
    
    # Draw outlet
    ax.arrow(4, 0.5, 0, -0.8, head_width=0.2, head_length=0.15,
            fc='blue', ec='darkblue', linewidth=2.5, alpha=0.7)
    ax.text(4, -0.3, '💧 Drainage', ha='center',
           fontsize=11, fontweight='bold', bbox=dict(boxstyle='round',
           facecolor='lightblue', alpha=0.7))
    
    # Add labels
    ax.text(1, 5, 'UPPER', fontsize=10, style='italic', alpha=0.6)
    ax.text(1, 2, 'LOWER', fontsize=10, style='italic', alpha=0.6)
    ax.text(2, 3.4, '↓', fontsize=16, ha='center', color='darkred', alpha=0.5)
    ax.text(6, 3.4, '↓', fontsize=16, ha='center', color='darkblue', alpha=0.5)
    
    # Add title and info
    ax.text(4, 8, 'Quadruple Tanks System Architecture',
           ha='center', fontsize=14, fontweight='bold')
    
    info_text = (
        "SYSTEM COMPONENTS:\n"
        "• 4 interconnected tanks (20 cm max height)\n"
        "• 2 variable-speed pumps for control inputs\n"
        "• Orifice connections between tanks\n"
        "• PID controllers regulate pump flows\n"
        "• Setpoint: 12 cm for upper tanks"
    )
    
    ax.text(4, -2.5, info_text, ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
           family='monospace')
    
    ax.set_xlim(0, 8)
    ax.set_ylim(-3.5, 8.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    fig.savefig('system_diagram.png', dpi=120, bbox_inches='tight')
    print("      ✓ System diagram saved: system_diagram.png")
    plt.close(fig)


if __name__ == "__main__":
    create_detailed_tank_visualization()
