#!/usr/bin/env python

# Generates points on a circle with a given radius, x, and y values
# in kicad_pcb format

""" For example, insert points into the following to get a keepout zone:
(zone (net 0) (net_name "") (layer F.Cu) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance 0.508))
  (min_thickness 0.254)
  (keepout (tracks not_allowed) (vias not_allowed) (copperpour not_allowed))
  (fill yes (arc_segments 16) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
     (xy 0 0) (xy 1 0) (xy 1 1)
    )
  )
)
"""

import sys
import math
import numpy as np

if len(sys.argv) != 4:
  print "Usage: gen-circle.py <x> <y> <radius>"
  sys.exit()

try:
  x, y, radius = [float(a) for a in sys.argv[1:]]
except ValueError:
  print "Enter radius as float"
  sys.exit()

def pts_str(pts):
  return ' '.join(['(xy {0} {1})'.format(x, y) for (x, y) in pts])

def circle_pts(r, pointCount=100):
  return [(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, pointCount)]

def offset(pts, offsetX, offsetY):
  return [(offsetX + x, offsetY + y) for (x, y) in pts]

print pts_str(offset(circle_pts(radius, 32), x, y))

