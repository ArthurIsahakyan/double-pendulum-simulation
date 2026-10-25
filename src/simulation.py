import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from scipy.integrate import solve_ivp

from src.physics import DoublePendulumPhysics


def run_simulation(
    t_end=30.0, fps=60, save_energy_plot="assets/energy_conservation.png"
):
  physics = DoublePendulumPhysics()

  points = int(t_end * fps) + 1
  t_eval = np.linspace(0.0, t_end, points)

  # Numerical solution with high accuracy DOP853 method
  solution = solve_ivp(
      physics.derivatives,
      (0.0, t_end),
      physics.initial_state,
      t_eval=t_eval,
      method="DOP853",
      rtol=1e-10,
      atol=1e-10,
  )

  if not solution.success:
    raise RuntimeError(solution.message)

  theta1, theta2 = solution.y[0], solution.y[1]
  omega1, omega2 = solution.y[2], solution.y[3]

  # Cartesian coordinates
  x1 = physics.L1 * np.sin(theta1)
  y1 = -physics.L1 * np.cos(theta1)
  x2 = x1 + physics.L2 * np.sin(theta2)
  y2 = y1 - physics.L2 * np.cos(theta2)

  # Energy calculation
  kinetic_energy = (
      0.5 * (physics.m1 + physics.m2) * physics.L1**2 * omega1**2
      + 0.5 * physics.m2 * physics.L2**2 * omega2**2
      + physics.m2 * physics.L1 * physics.L2 * omega1 * omega2 * np.cos(theta1 - theta2)
  )

  potential_energy = -(physics.m1 + physics.m2) * physics.g * physics.L1 * np.cos(
      theta1
  ) - physics.m2 * physics.g * physics.L2 * np.cos(theta2)

  total_energy = kinetic_energy + potential_energy
  energy_error = np.max(np.abs(total_energy - total_energy[0]))

  print("Simulation completed successfully!")
  print(f"Initial energy: {total_energy[0]:.8f} J")
  print(f"Maximum absolute energy deviation: {energy_error:.3e} J")

  # Save energy conservation plot (создаем папку assets, если её нет)
  fig_energy, ax_energy = plt.subplots(figsize=(10, 5))
  ax_energy.plot(solution.t, kinetic_energy, label="Kinetic energy")
  ax_energy.plot(solution.t, potential_energy, label="Potential energy")
  ax_energy.plot(solution.t, total_energy, label="Total energy", linestyle="--")
  ax_energy.set_title("Energy Conservation (DOP853 Integrator)")
  ax_energy.set_xlabel("Time (s)")
  ax_energy.set_ylabel("Energy (J)")
  ax_energy.grid(True, alpha=0.3)
  ax_energy.legend()
  plt.tight_layout()

  if save_energy_plot:
    # Автоматически создаем директорию, если она отсутствует
    plot_dir = os.path.dirname(save_energy_plot)
    if plot_dir and not os.path.exists(plot_dir):
      os.makedirs(plot_dir)

    fig_energy.savefig(save_energy_plot, dpi=200, bbox_inches="tight")
    print(f"Energy graph saved as {save_energy_plot}")

  # Animation setup
  fig, ax = plt.subplots(figsize=(9, 9))
  limit = physics.L1 + physics.L2 + 0.3
  ax.set_xlim(-limit, limit)
  ax.set_ylim(-limit, limit)
  ax.set_aspect("equal")
  ax.grid(True, alpha=0.3)
  ax.set_title("Chaos in Double Pendulum Simulation", fontsize=16)
  ax.set_xlabel("x (m)")
  ax.set_ylabel("y (m)")

  rod, = ax.plot([], [], "o-", lw=2, markersize=8, color="darkblue")
  trail1, = ax.plot([], [], "-", lw=1, alpha=0.7, color="tab:orange")
  trail2, = ax.plot([], [], "-", lw=1, alpha=0.7, color="tab:green")

  time_text = ax.text(0.03, 0.95, "", transform=ax.transAxes, fontsize=12)
  trail_duration = 3.0

  def init():
    rod.set_data([], [])
    trail1.set_data([], [])
    trail2.set_data([], [])
    time_text.set_text("")
    return rod, trail1, trail2, time_text

  def update(frame):
    current_x = [0, x1[frame], x2[frame]]
    current_y = [0, y1[frame], y2[frame]]
    rod.set_data(current_x, current_y)

    current_time = solution.t[frame]
    start_time = max(0, current_time - trail_duration)
    start_frame = np.searchsorted(solution.t, start_time)

    trail1.set_data(x1[start_frame:frame + 1], y1[start_frame:frame + 1])
    trail2.set_data(x2[start_frame:frame + 1], y2[start_frame:frame + 1])
    time_text.set_text(f"Time: {current_time:.2f} s")

    return rod, trail1, trail2, time_text

  interval = 1000 / fps
  ani = FuncAnimation(
      fig,
      update,
      frames=len(solution.t),
      init_func=init,
      interval=interval,
      blit=True,
      repeat=True,
  )

  plt.tight_layout()
  plt.show()