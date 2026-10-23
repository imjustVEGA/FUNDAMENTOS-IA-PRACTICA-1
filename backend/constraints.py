import numpy as np
from .geometry import angular

def violations(coords, scenario):
    issues=[]
    for z in scenario.zones:
        if z.active:
            for i in np.flatnonzero(angular(coords,[z.lat,z.lon]) <= z.radius_deg+1e-9):
                issues.append(f'S{i+1}: {z.name}')
    return issues

def valid_point(point, scenario):
    zones=[z for z in scenario.zones if z.active]
    if not zones: return True
    return not np.any(angular(point,[[z.lat,z.lon] for z in zones]) <= np.array([z.radius_deg for z in zones])+1e-9)
