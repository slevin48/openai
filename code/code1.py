import numpy as np
import matplotlib.pyplot as plt

# Generate some sample data
N = 100
x = np.linspace(0, 2*np.pi, N)
y = np.sin(x) + np.random.normal(scale=0.1, size=N)

# Perform linear regression
X = np.vstack((x, np.ones(N))).T
w = np.linalg.inv(X.T @ X) @ X.T @ y

# Plot results
plt.scatter(x, y)
plt.plot(x, w[0]*x + w[1], color='r')
plt.show()