# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 15:25:36 2025

@author: yangshin.liu
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# Wafer radius
wafer_radius = 300 / 2  # mm

# Zone radii
zone_radii = [25, 52, 78, 105, 123, 133, 142, 149]

# Wafer center
center = (0, 0)

# Colors for each zone
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', 
          '#ff7f00', '#ffff33', '#a65628', '#f781bf']

fig, ax = plt.subplots(figsize=(8,8))

# Draw zones (from inner to outer)
for i in range(len(zone_radii)):
    inner_radius = zone_radii[i-1] if i > 0 else 0
    outer_radius = zone_radii[i]
    wedge = Wedge(center=center, r=outer_radius, theta1=0, theta2=360,
                  width=outer_radius-inner_radius, facecolor=colors[i],
                  edgecolor='black', label=f"A{i+1}")
    ax.add_patch(wedge)

# Draw wafer outline
wafer_circle = plt.Circle(center, wafer_radius, fill=False, color='black', linewidth=2)
ax.add_patch(wafer_circle)

# Formatting
ax.set_aspect('equal')
plt.xlim(-wafer_radius-10, wafer_radius+10)
plt.ylim(-wafer_radius-10, wafer_radius+10)
plt.title("300mm Wafer Zone Map (Radius)")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.show()
