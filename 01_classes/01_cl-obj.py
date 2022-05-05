import numpy as np


class RadialTransform:
    def __init__(self, center_x, center_y):
        self.cx = center_x
        self.cy = center_y

    def transform(self, pt_x, pt_y):
        rad = ((pt_x - self.cx) ** 2 +
               (pt_y - self.cy) ** 2) ** 0.5
        ph = np.arccos(
            (pt_x - self.cx) / rad)
        return ph, rad


tr = RadialTransform(1., 2.)
phi, r = tr.transform(3., 4.)
print('(x, y) → (φ, r): (%f, %f) → (%f, %f)' % (3., 4., phi, r))
