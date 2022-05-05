from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np


class PlotWidget(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        # вызываем конструктор QWidget
        super().__init__(parent=parent, flags=flags)

        # создаём поля matplotlib: фигура, холст, оси, навигационный виджет
        # сохраняем их как поля класса
        self.mpl_fig = Figure()
        self.mpl_canvas = FigureCanvasQTAgg(self.mpl_fig)
        self.mpl_ax = self.mpl_fig.add_subplot(111)
        self.mpl_nt = NavigationToolbar2QT(self.mpl_canvas, parent=self)

        # создаём кнопку
        self.btn_sin = QPushButton('Sin', parent=self)

        # создаём и заполняем компоновку
        # важно: это просто переменная! компоновку затем нужно установить на виджет
        layout = QGridLayout()
        layout.addWidget(self.mpl_canvas, 1, 1, 1, 1)
        layout.addWidget(self.mpl_nt, 2, 1, 1, 1)
        layout.addWidget(self.btn_sin, 2, 2, 1, 1)

        # устанавливаем компоновку на виджет
        self.setLayout(layout)

        # взаимодействие между объектами QT происходит через сигналы и слоты
        # элементы (например, кнопка) отправляют сигналы когда с ними
        # происходят какие-то действия (например, нажатие)
        # здесь мы подписываемся на сигнал идущий от кнопки self.btn_sin когда она нажата
        # и регистрируем метод self.on_btn_sin_pressed который должен в этой ситуации вызываться
        self.btn_sin.pressed.connect(self.on_btn_sin_pressed)

    def on_btn_sin_pressed(self):
        xs = np.linspace(0, 2. * np.pi, 100)
        ys = np.sin(xs)
        # очищаем оси
        self.mpl_ax.clear()
        # строим график
        self.mpl_ax.plot(xs, ys)
        # обновляем холст
        self.mpl_canvas.draw()


class SimpleMW(QMainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.cw = PlotWidget(parent=self)
        self.setCentralWidget(self.cw)

        self.setWindowTitle('Чудо-программа')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = SimpleMW()
    main_window.show()

    sys.exit(app.exec_())
