from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QPushButton, QFileDialog, QTabWidget, QLineEdit
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np


class FFTWorker:
    """
    Класс-фильтр высоких частот
    """
    def __init__(self):
        # создаём поля: исходные данные
        self.xs = np.array([])
        self.ys = np.array([])
        self.yerrs = np.array([])

        # фурье-образ и фильтрованные данные
        self.fft_xs = np.array([])
        self.fft_ys = np.array([])
        self.ys_filtered = np.array([])

        # частота фильтра ВЧ
        self.max_freq = np.inf

    def set_data(self, data):
        # заполняем поля данных из переданного массива
        self.xs, self.ys, self.yerrs = data.T

        # вычисляем Фурье-образ и фильтрованные данные без обрезания по частоте
        self.max_freq = np.inf
        self.set_ys_fft()

        # устанавливаем границу фильтра на максимальную частоту вычисленную из данных
        self.max_freq = np.max(self.fft_xs)

    def set_ys_fft(self, max_freq=None):
        if max_freq is not None:
            self.max_freq = max_freq

        # np.fft.rfft ломается если массив пустой, исключаем этот случай
        if self.ys.shape[0] == 0:
            return

        # вычисляем Фурье-образ
        self.fft_ys = np.fft.rfft(self.ys)
        self.fft_xs = np.fft.rfftfreq(self.ys.shape[0], d=np.mean(self.xs[1:] - self.xs[:-1]))

        # считаем результат фильтрации:
        # копируем Фурье-образ, заполняем нулями высокие частоты (выше чем self.max_freq),
        # делаем обратное преобразование
        pass


class PlotWidget(QWidget, FFTWorker):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        # наследование идёт от двух классов, поэтому нужно вызывать конструкторы обоих предков
        super(QWidget, self).__init__(parent=parent, flags=flags)
        super(FFTWorker, self).__init__()

        # создаём виджет с вкладками
        self.tabs = QTabWidget(parent=self)

        # создаём виджеты-вкладки и заполняем их полями matplotlib: фигура, холст, оси, навигационный виджет
        self.mpl_fig1 = Figure()
        self.mpl_canvas1 = FigureCanvasQTAgg(self.mpl_fig1)
        self.mpl_ax1 = self.mpl_fig1.add_subplot(111)
        self.mpl_nt1 = NavigationToolbar2QT(self.mpl_canvas1, parent=self)
        self.mpl_w1 = QWidget()
        w1_layout = QGridLayout()
        w1_layout.addWidget(self.mpl_canvas1, 1, 1, 1, 1)
        w1_layout.addWidget(self.mpl_nt1, 2, 1, 1, 1)
        self.mpl_w1.setLayout(w1_layout)

        # сделать для второго виджета то же самое что и для self.mpl_w1
        self.mpl_w2 = QWidget()
        pass

        # поля хранящие ссылки на линии на графиках matplotlib
        self.line_data = None
        self.line_data_filtered = None
        self.line_data_fft1 = None
        self.line_data_fft2 = None

        # вставляем виджеты с фигурами в виджет со вкладками
        self.tabs.addTab(self.mpl_w1, 'Real space')
        self.tabs.addTab(self.mpl_w2, 'Fourier space')

        # создаём кнопку
        self.btn_open = QPushButton('Open', parent=self)

        # создаём поле для ввода текста, задаём ему валидатор,
        # чтобы оно принимало только числа между 0 и 10
        self.max_freq_edit = QLineEdit(parent=self)
        self.max_freq_edit.setValidator(
            QDoubleValidator(0, 10, 2, parent=self.max_freq_edit, notation=QDoubleValidator.StandardNotation)
        )

        # создаём и заполняем компоновку
        # важно: это просто переменная! компоновку затем нужно установить на виджет
        layout = QGridLayout()
        layout.addWidget(self.tabs, 1, 1, 3, 1)
        layout.addWidget(self.max_freq_edit, 2, 2, 1, 1)
        layout.addWidget(self.btn_open, 1, 2, 1, 1)

        # устанавливаем компоновку на виджет
        self.setLayout(layout)

        # взаимодействие между объектами QT происходит через сигналы и слоты
        # элементы (например, кнопка) отправляют сигналы когда с ними
        # происходят какие-то действия (например, нажатие)
        # здесь мы подписываемся на сигнал идущий от кнопки self.btn_sin когда она нажата
        # и регистрируем метод self.on_btn_sin_pressed который должен в этой ситуации вызываться
        self.btn_open.pressed.connect(self.on_btn_open_pressed)
        self.max_freq_edit.returnPressed.connect(self.on_mfe_r_pressed)

    def upd_plot(self):
        # перерисовываем линии:
        # если линия ещё не существует (инициализируется как None) создаём её,
        # если существует, то обновляем данные
        if self.line_data is None:
            self.line_data = self.mpl_ax1.errorbar(self.xs, self.ys, yerr=self.yerrs, linestyle='', marker='.').lines[0]
        else:
            self.line_data.set_data(self.xs, self.ys)

        # по аналогии с предыдущей линией
        if self.line_data_filtered is None:
            self.line_data_filtered = self.mpl_ax1.plot(self.xs, self.ys_filtered, linestyle='-', marker='')[0]
        else:
            self.line_data_filtered.set_data(self.xs, self.ys_filtered)

        # заполняем текст на осях
        self.mpl_ax1.set_xlabel(r'$2\Theta$, $[^{\circ}$]')
        self.mpl_ax1.set_ylabel(r'Intensity [cts]')

        # метод draw() необходимо вызвать чтобы холст обновился
        self.mpl_canvas1.draw()

        # ещё две линии на вторых осях по аналогии
        if self.line_data_fft1 is None:
            self.line_data_fft1 = self.mpl_ax2.semilogy(self.fft_xs[self.fft_xs < self.max_freq],
                                                        (np.abs(self.fft_ys) ** 2)[self.fft_xs < self.max_freq],
                                                        linestyle='-', marker='')[0]
        else:
            self.line_data_fft1.set_data(self.fft_xs[self.fft_xs < self.max_freq],
                                         (np.abs(self.fft_ys) ** 2)[self.fft_xs < self.max_freq])

        if self.line_data_fft2 is None:
            self.line_data_fft2 = self.mpl_ax2.semilogy(self.fft_xs[self.fft_xs >= self.max_freq],
                                                        (np.abs(self.fft_ys) ** 2)[self.fft_xs >= self.max_freq],
                                                        linestyle='--', marker='')[0]
        else:
            self.line_data_fft2.set_data(self.fft_xs[self.fft_xs >= self.max_freq],
                                         (np.abs(self.fft_ys) ** 2)[self.fft_xs >= self.max_freq])

        self.mpl_ax2.set_xlabel(r'Frequency, $[1/^{\circ}$]')
        self.mpl_ax2.set_ylabel(r'Intensity [cts]')
        self.mpl_canvas2.draw()

    def on_btn_open_pressed(self):
        #  получить имя файла с помощью QFileDialog
        pass

        try:
            # тут нужно попытаться прочитать файл и заполнить поля класса
            pass
        except Exception:
            # тут ничего делать не нужно, этот pass содержательный
            pass
        else:
            # сюда попадаем только если удалось прочитать файл без ошибок
            # удаляем старые линии, заполняем ссылки на них как None
            self.mpl_ax1.clear()
            self.mpl_ax2.clear()

            self.line_data = None
            self.line_data_filtered = None
            self.line_data_fft1 = None
            self.line_data_fft2 = None

            # отрисовываем прочитанные данные
            self.upd_plot()

            # устанавливаем минимальную и максимальную возможные частоты которые можно ввести в текстовое поле
            # исходя из прочитанных данных
            self.max_freq_edit.setValidator(
                QDoubleValidator(np.min(self.fft_xs), np.max(self.fft_xs), 2,
                                 parent=self.max_freq_edit, notation=QDoubleValidator.StandardNotation)
            )
            # по умолчанию фильтр ВЧ ничего не делает с частотой обреза на верхней границе данных
            self.max_freq_edit.setText('%.02f' % np.max(self.fft_xs))

    def on_mfe_r_pressed(self):
        # если вводится новая частота, нужно пересчитать результаты фильтрации
        self.set_ys_fft(max_freq=float(self.max_freq_edit.text()))
        # выводим обновлённые фильтрованные данные на график
        self.upd_plot()


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
