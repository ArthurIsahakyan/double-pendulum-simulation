from src.simulation import run_simulation


def main():
  print("Initializing Double Pendulum Simulation...")
  run_simulation(t_end=30.0, fps=60)


if __name__ == "__main__":
  main()