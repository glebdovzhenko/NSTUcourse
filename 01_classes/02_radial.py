import numpy as np
from matplotlib import pyplot as plt


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


# Задача:
# Создать объект класса RadialTransform с центром в (π/2, 0)
# Сделать преобразование координат (xs, ys)
# Вывести результаты на оси ax в полярных координатах
# Графики на двух осях должны визуально совпасть

xs = np.linspace(0., np.pi, 100)
ys = np.pi * np.sin(xs) / 2.

plt.plot(xs, ys)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
plt.show()
