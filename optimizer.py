# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 23:45:18 2025

@author: yangshin.liu
"""

import numpy as np
from skopt import gp_minimize
from skopt.space import Integer

# Suppose you have 8 zones
zone_names = ['A1','A2','A3','A4','A5','A6','A7','A8']

# -------------------------
# 1. Define Pressure Ranges
# -------------------------
zone_bounds = [(100, 600)] * 8   # Example: 100 to 600 hPa for each zone
search_space = [
    Integer(low, high, name=f'p_{zn}') for (low, high), zn in zip(zone_bounds, zone_names)
]

# -------------------------
# 2. Tunability Parameters (example values)
#    Use your calculated slopes from previous step for each zone!
# -------------------------
tunabilities = np.array([0.8, 1.2, 2.0, 2.5, 0.5, 1.7, 2.2, 0.9])
# Higher value = more sensitive to pressure tweaks

# -------------------------
# 3. Simulated Objective Function
#    Replace this with your real model or measurement!
# -------------------------
def run_process_and_get_CV(pressures):
    # Simple fake model: uniformity improves near center pressures (e.g. 350)
    # and worsens with high zone differences, add some randomness
    uniformity_metric = 10 - 0.002 * np.sum(350 - np.abs(np.array(pressures) - 350))
    # Add random noise to simulate measurement error
    noise = np.random.normal(0, 0.05)
    return uniformity_metric + noise

last_pressures = None  # Track previous step for penalty

def objective(pressures):
    global last_pressures
    uniformity = run_process_and_get_CV(pressures)
    penalty = 0
    # --- Tunability penalty ---
    # Penalize large pressure changes in sensitive (high tunability) zones
    if last_pressures is not None:
        delta = np.array(pressures) - np.array(last_pressures)
        penalty = np.sum(np.abs(delta) * tunabilities) * 0.02  # 0.02 is hyperparameter
    last_pressures = pressures.copy()
    # --- Combine uniformity and penalty ---
    return uniformity + penalty

# -------------------------
# 4. Run Bayesian Optimization
# -------------------------
result = gp_minimize(
    func=objective,
    dimensions=search_space,
    n_calls=40,
    n_initial_points=10,
    random_state=42,
    verbose=True
)

# -------------------------
# 5. Print Results
# -------------------------
print("\nBest Pressures Found (hPa):")
for zn, p in zip(zone_names, result.x):
    print(f"{zn}: {p} hPa")
print("Minimum Uniformity Metric Value:", result.fun)

# Optional: View optimization history
import matplotlib.pyplot as plt
plt.plot(result.func_vals, marker='o')
plt.xlabel('Iteration')
plt.ylabel('Uniformity Metric + Penalty')
plt.show()
