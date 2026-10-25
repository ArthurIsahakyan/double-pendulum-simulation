import numpy as np


class DoublePendulumPhysics:

  def __init__(
      self,
      m1=1.0,
      m2=1.0,
      L1=1.0,
      L2=1.0,
      g=9.81,
      theta1_0=np.radians(120),
      theta2_0=np.radians(-20),
      omega1_0=0.0,
      omega2_0=0.0,
  ):
    self.m1 = m1
    self.m2 = m2
    self.L1 = L1
    self.L2 = L2
    self.g = g

    self.initial_state = [theta1_0, theta2_0, omega1_0, omega2_0]

  def derivatives(self, t, state):
    theta1, theta2, omega1, omega2 = state
    delta = theta1 - theta2

   
    M = np.array([
        [(self.m1 + self.m2) * self.L1**2, self.m2 * self.L1 * self.L2 * np.cos(delta)],
        [self.m2 * self.L1 * self.L2 * np.cos(delta), self.m2 * self.L2**2],
    ])

    
    F = np.array([
        -self.m2 * self.L1 * self.L2 * omega2**2 * np.sin(delta)
        - (self.m1 + self.m2) * self.g * self.L1 * np.sin(theta1),
        self.m2 * self.L1 * self.L2 * omega1**2 * np.sin(delta)
        - self.m2 * self.g * self.L2 * np.sin(theta2),
    ])

    alpha1, alpha2 = np.linalg.solve(M, F)
    return np.array([omega1, omega2, alpha1, alpha2])