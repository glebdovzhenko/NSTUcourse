from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
import sys


class SimpleMW(QMainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = SimpleMW()
    main_window.show()

    sys.exit(app.exec_())
