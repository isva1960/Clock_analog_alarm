from PyQt5.QtGui import QKeyEvent

from Clock_Timer_Alarm_del import Ui_Clock_Timer_del
import sys, datetime
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QSettings, Qt
import locale
from PyQt5 import QtWidgets, QtGui
from Clock_Timer_m_utils import *

ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


class Dlg_Del(QDialog, Ui_Clock_Timer_del):
    # def __init__(self, **kwargs):
    #    super().__init__(**kwargs, flags=Qt.WindowCloseButtonHint)
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs, flags=Qt.WindowCloseButtonHint)
        self.main = root
        self.setupUi(self)
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Del_old_Window"  # Секция параметров окна
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна
        # self.alarm_dictionaries_file = "alarm_dictionaries.txt"
        self.alarm_dictionaries_file = self.main.alarm_dictionaries_file
        self.pushB_exit.clicked.connect(self.run_exit)
        self.pushB_del.clicked.connect(self.del_exit)
        self.spinB_kol_d.valueChanged.connect(self.chng_day)
        self.tableWidget_day_alarm.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # !!!
        self.delete_date = None
        self.chng_day()

    def chng_day(self):
        with open(self.alarm_dictionaries_file, "r") as file:
            alarm_dictionaries = [eval(line) for line in file]
        curent_date_time = datetime.datetime.now()
        curent_date = curent_date_time.date()
        self.delete_date = curent_date - datetime.timedelta(days=self.spinB_kol_d.value())
        self.tableWidget_day_alarm.setRowCount(0)
        for alarm in alarm_dictionaries:
            if alarm['type'] == 2 and alarm['date'] < self.delete_date and alarm['activate']==1:
                row = self.tableWidget_day_alarm.rowCount()
                self.tableWidget_day_alarm.insertRow(row)
                self.tableWidget_day_alarm.setItem(row, 0,
                                                   QtWidgets.QTableWidgetItem(alarm['name']))
                self.tableWidget_day_alarm.setItem(row, 1,
                                                   QtWidgets.QTableWidgetItem(type_alarm[alarm['type']]))
                self.tableWidget_day_alarm.setItem(row, 2,
                                                   QtWidgets.QTableWidgetItem(
                                                       ret_priod(alarm['period'], alarm['date'], alarm['type'])))
                self.tableWidget_day_alarm.setItem(row, 3,
                                                   QtWidgets.QTableWidgetItem(str(alarm['time'])))

    def run_exit(self):
        self.delete_date = None
        self.close()

    def del_exit(self):
        if self.tableWidget_day_alarm.rowCount() > 0:
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Удалить")
            msgtxt = "Удалить сведения о звонках?"
            msgbox.setText(msgtxt)
            msgbox.setIcon(QMessageBox.Warning)
            iconw = QtGui.QIcon()
            iconw.addPixmap(QtGui.QPixmap(":/question_115172.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msgbox.setWindowIcon(iconw)
            msgbox.addButton('Да', QtWidgets.QMessageBox.YesRole)
            msgbox.addButton('Нет', QtWidgets.QMessageBox.NoRole)
            result = msgbox.exec_()
            if result == 1:
                self.delete_date = None
        else:
            self.delete_date = None
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
    Window = Dlg_Del()
    Window.show()
    sys.exit(app.exec_())
