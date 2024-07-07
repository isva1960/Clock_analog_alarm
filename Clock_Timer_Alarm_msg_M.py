from PyQt5.QtGui import QKeyEvent

from Clock_Timer_Alarm_msg import Ui_Clock_Timer_msg
import sys
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSettings, Qt
import locale
from PyQt5 import QtWidgets

ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


class Dlg_Msg(QDialog, Ui_Clock_Timer_msg):
    # def __init__(self, **kwargs):
    #    super().__init__(**kwargs, flags=Qt.WindowCloseButtonHint)
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs, flags=Qt.WindowCloseButtonHint)
        self.main = root
        self.setupUi(self)
        self.textEdit_msg.setText(self.main.msg_txt)
        self.textEdit_msg.setStyleSheet("color: red")
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Msg_Window"  # Секция параметров окна
        self.values_section = "Values"  # Секция параметров переменных
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна
        self.pushB_exit.clicked.connect(self.run_exit)

    def run_exit(self):
        self.close()

    def closeEvent(self, event):
        # Ваше действие при закрытии окна
        self.settings.setValue(self.window_section + "/geometry", self.saveGeometry())  # Сохранение размера окна

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            return
        else:
            return super().keyPressEvent(a0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Window = Dlg_Msg()
    Window.show()
    sys.exit(app.exec_())
