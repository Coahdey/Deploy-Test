# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 14:07:45 2025

@author: yangshin.liu
"""

import numpy as np
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args

# Constants
NUM_WAFERS = 3
NUM_ZONES = 8
TARGET_MEAN_PRESSURE = 207.0

def flatten_objective(zone_pressures, polish_profiles, tunability):
    """
    For each wafer, compute the expected polish rate profile given zone_pressures,
    measured profile, and tunability. Then, measure non-uniformity (STD).
    """
    total_std = 0.0
    for w in range(NUM_WAFERS):
        # Get this wafer's zone setting
        wafer_zone_pressures = zone_pressures[w * NUM_ZONES: (w + 1) * NUM_ZONES]
        wafer_profile = polish_profiles[w]
        # Model: next profile ~ current + tunability * (zone_pressure_change)
        # Since the zone pressures are only provided every 8 zones and profile is 147 points,
        # assign each profile point to a zone:
        expected_profile = wafer_profile.copy()
        zone_indices = [25, 52, 78, 105, 123, 133, 142, 149]
        profile_zone_map = np.zeros_like(wafer_profile)
        for zi in range(NUM_ZONES):
            profile_zone_map[(0 if zi == 0 else zone_indices[zi-1]):zone_indices[zi]] = zi
        # For demonstration, apply simple expected change from zone pressure difference and tunability
        for pi in range(len(wafer_profile)):
            zone_id = profile_zone_map[pi]
            # delta pressure from previous run assumed to be tunability effect on flatness
            # NOTE: for first optimization, assume target is uniform profile
            expected_profile[pi] -= tunability[zone_id] * (wafer_zone_pressures[zone_id] - TARGET_MEAN_PRESSURE)
        # Flatness metric: std deviation from mean
        total_std += np.std(expected_profile)
    return total_std / NUM_WAFERS

# Define bounds for each zone's pressure on each wafer
pressure_bounds = [Real(172, 207, name=f'w{w}_z{z}') for w in range(NUM_WAFERS) for z in range(NUM_ZONES)]

# Dummy example: input arrays
previous_pressures = np.array([
    [207, 207, 207, 207, 207, 207, 207, 207],  # Wafer 1
    [207, 172, 207, 172, 207, 172, 207, 172],  # Wafer 2
    [172, 207, 172, 207, 172, 207, 172, 207],  # Wafer 3
])
polish_profiles = [np.random.normal(loc=0.5, scale=0.1, size=147) for _ in range(NUM_WAFERS)]
tunability = np.array([0.5, 0.6, 0.5, 0.4, 0.4, 0.3, 0.4, 0.5]) # Example numbers

# Constraints (mean pressure per wafer = TARGET_MEAN_PRESSURE)
def pressure_constraint(zone_pressures):
    for w in range(NUM_WAFERS):
        wafer_pressures = zone_pressures[w * NUM_ZONES: (w + 1) * NUM_ZONES]
        if not np.isclose(np.mean(wafer_pressures), TARGET_MEAN_PRESSURE, atol=1):
            return False
    return True

# Bayesian optimization
@use_named_args(pressure_bounds)
def objective(**pressures):
    # Flatten the input into an array
    zone_pressures = np.array(list(pressures.values()))
    if not pressure_constraint(zone_pressures):
        # Penalize infeasible suggestions
        return 1000.0
    score = flatten_objective(zone_pressures, polish_profiles, tunability)
    return score

res = gp_minimize(
    objective,
    dimensions=pressure_bounds,
    n_calls=30,
    random_state=42,
)

# Output best zone settings for next run
best_pressures = np.array(res.x).reshape(NUM_WAFERS, NUM_ZONES)
for i, wafer_pressures in enumerate(best_pressures):
    print(f'Next Run Suggestion - Wafer {i+1}:')
    print(', '.join(f'{p:.1f}' for p in wafer_pressures))
