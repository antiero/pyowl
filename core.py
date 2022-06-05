from sys import platform
from math import hypot
# Core Functions

def isMac():
    return platform.lower() == "darwin"

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Alt method for inside circle
# https://stackoverflow.com/questions/481144/equation-for-testing-if-a-point-is-inside-a-circle
def in_radius(c_x, c_y, r, x, y):
    return hypot(c_x-x, c_y-y) <= r

# Test if point inside circle
def in_circle(center_x, center_y, radius, x, y):
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2
