from PyQt5.QtGui import QKeyEvent

from Clock_Timer_Alarm_dlg import \
    Ui_Clock_Timer_alarm  # Импортируем класс Ui_MainWindow из модуля Mainwindow созданного в дизайнере.
import Clock_Timer_Sound_dlg_M
import sys, os, datetime, time
from PyQt5.QtWidgets import QDialog, QCheckBox, QMessageBox, QFileDialog
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSettings, Qt
from Clock_Timer_m_utils import *
from Clock_Timer_Alarm_del_M import *
import locale
import operator

ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


class Dlg_Alarm(QDialog, Ui_Clock_Timer_alarm):
    #def __init__(self, **kwargs):
    #    super().__init__(**kwargs, flags=Qt.WindowCloseButtonHint)
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs, flags=Qt.WindowCloseButtonHint)
        self.main = root
        self.setupUi(self)
        self.tableWidget_alarm.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # !!!
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Alarm_Window"  # Секция параметров окна
        self.values_section = "Values"  # Секция параметров переменных
        self.type_act = ("Не активный", "Активный")
        self.fmove = False
        self.fcng = False
        self.fapp = False
        self.fsort = False
        self.soundnameA = ""
        self.dateEdit_d.setDate(datetime.datetime.now().date())

        self.alarm_dictionaries_file = self.main.alarm_dictionaries_file
        #self.alarm_dictionaries_file = "alarm_dictionaries.txt"
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна

        self.load_table()
        self.tableWidget_alarm.setFocus()
        self.changed_cell()
        self.set_blk()
        self.current_row=self.tableWidget_alarm.currentRow()

        self.tableWidget_alarm.itemSelectionChanged.connect(self.changed_cell)
        self.pushB_mov_up.clicked.connect(self.mov_up)
        self.pushB_mov_down.clicked.connect(self.mov_down)
        self.pushB_sort.clicked.connect(self.sort)
        self.pushB_save.clicked.connect(self.save)
        self.pushB_canc_chng.clicked.connect(self.canc_chng)
        self.pushB_chng.clicked.connect(self.chng)
        self.pushB_app.clicked.connect(self.app)
        self.pushB_del.clicked.connect(self.delet)
        self.pushB_del_old.clicked.connect(self.delet_old)
        self.radioB_evd.clicked.connect(self.chng_type)
        self.radioB_wd.clicked.connect(self.chng_type)
        self.radioB_date.clicked.connect(self.chng_type)
        self.pushB_soundA.clicked.connect(self.set_soundA)
        self.pushB_sound_resA.clicked.connect(self.res_soundA)
        self.pushB_sound_cA.clicked.connect(self.test_sound)
        self.pushB_exit.clicked.connect(self.run_exit)

    def run_exit(self):
        self.close()
    def delet_old(self):
        self.current_row= self.tableWidget_alarm.currentRow()
        dialog = Dlg_Del(self)
        #dialog.alarm_dictionaries_file = self.alarm_dictionaries_file
        dialog.exec()
        if dialog.delete_date is not None:
            with open(self.alarm_dictionaries_file, "r") as file:
                alarm_dictionaries = [eval(line) for line in file]
            lst_new=[]
            for alarm in alarm_dictionaries:
                if not (alarm['type'] == 2 and alarm['date'] < dialog.delete_date and alarm['activate'] == 1):
                    lst_new.append(alarm)
            with open(self.alarm_dictionaries_file, "w") as file:
                for dictionary in lst_new:
                    file.write(str(dictionary) + "\n")
            self.load_table()
        self.set_blk()

    def sort(self):
        self.pushB_chng.setEnabled(False)
        self.pushB_del.setEnabled(False)
        self.pushB_del_old.setEnabled(False)
        self.pushB_app.setEnabled(False)
        self.pushB_save.setEnabled(True)
        self.pushB_canc_chng.setEnabled(True)
        self.pushB_exit.setEnabled(False)
        self.alarm_dictionaries = sorted(self.alarm_dictionaries, key=operator.itemgetter('time', 'type','date'))
        self.chng_table()
        self.fsort = True

    def test_sound(self):
        obj = self.sender()
        dial = Clock_Timer_Sound_dlg_M.Dlg_Sound(self)
        dial.set_objnane()
        dial.exec()

    def res_soundA(self):
        row = self.tableWidget_alarm.currentRow()
        self.soundnameA = ""
        self.alarm_dictionaries[row]["sound"] = self.soundnameA
        self.label_soundA.setText("")

    def set_soundA(self):
        row = self.tableWidget_alarm.currentRow()
        soundf = QFileDialog.getOpenFileName(self, "Мелодии для будильника", self.alarm_dictionaries[row]["sound"],
                                             "Мелодии для будильника (*.wav *.mp3 *.mid)")[0]
        if soundf:
            self.soundnameA = soundf
            self.alarm_dictionaries[row]["sound"] = self.soundnameA
            self.label_soundA.setText(os.path.basename(self.soundnameA))

    def load_table(self):
        with open(self.alarm_dictionaries_file, "r") as file:
            self.alarm_dictionaries = [eval(line) for line in file]
        self.chng_table()

    def chng_table(self):
        self.tableWidget_alarm.setRowCount(0)
        for alarm in self.alarm_dictionaries:
            row = self.tableWidget_alarm.rowCount()
            self.tableWidget_alarm.insertRow(row)
            self.chg_row(alarm, row)
        self.tableWidget_alarm.setCurrentCell(0, 0)

    def chg_row(self, alarm, row):
        self.tableWidget_alarm.setItem(row, 0,
                                       QtWidgets.QTableWidgetItem((alarm['name'])))
        self.tableWidget_alarm.setItem(row, 1,
                                       QtWidgets.QTableWidgetItem(type_alarm[(alarm['type'])]))
        self.tableWidget_alarm.setItem(row, 2,
                                       QtWidgets.QTableWidgetItem(
                                           ret_priod(alarm['period'], alarm['date'], alarm['type'])))
        self.tableWidget_alarm.setItem(row, 3,
                                       QtWidgets.QTableWidgetItem(str(alarm['time'])))
        self.tableWidget_alarm.setItem(row, 4,
                                       QtWidgets.QTableWidgetItem(self.type_act[(alarm['activate'])]))

    def chng_type(self):
        if self.radioB_evd.isChecked():
            self.dateEdit_d.setEnabled(False)
            for checkBox in self.findChildren(QCheckBox):
                if checkBox.objectName()[0:10] == "checkBox_d":
                    checkBox.setEnabled(False)
        elif self.radioB_wd.isChecked():
            self.dateEdit_d.setEnabled(False)
            for checkBox in self.findChildren(QCheckBox):
                if checkBox.objectName()[0:10] == "checkBox_d":
                    checkBox.setEnabled(True)
        elif self.radioB_date.isChecked():
            if self.dateEdit_d.date().toPyDate() <= datetime.datetime(2000, 1, 1, 00, 00).date():
                self.dateEdit_d.setDate(datetime.datetime.now().date())
            self.dateEdit_d.setEnabled(True)
            for checkBox in self.findChildren(QCheckBox):
                if checkBox.objectName()[0:10] == "checkBox_d":
                    checkBox.setEnabled(False)

    def delet(self):
        self.pushB_chng.setEnabled(False)
        self.pushB_del.setEnabled(False)
        self.pushB_del_old.setEnabled(False)
        self.pushB_app.setEnabled(False)
        self.pushB_save.setEnabled(True)
        self.pushB_canc_chng.setEnabled(True)
        self.pushB_mov_up.setEnabled(False)
        self.pushB_mov_down.setEnabled(False)
        self.pushB_exit.setEnabled(False)
        row = self.tableWidget_alarm.currentRow()
        self.current_row= self.tableWidget_alarm.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Удалить")
            msgtxt = "Удалить сведения о звонке?"
            msgbox.setText(msgtxt)
            msgbox.setIcon(QMessageBox.Warning)
            iconw = QtGui.QIcon()
            iconw.addPixmap(QtGui.QPixmap(":/question_115172.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msgbox.setWindowIcon(iconw)
            msgbox.addButton('Да', QtWidgets.QMessageBox.YesRole)
            msgbox.addButton('Нет', QtWidgets.QMessageBox.NoRole)
            result = msgbox.exec_()
            if result == 0:
                self.tableWidget_alarm.removeRow(row)
                self.tableWidget_alarm.selectionModel().clearCurrentIndex()
                self.alarm_dictionaries.pop(row)
                self.save_dict()
                self.changed_cell()
                if self.current_row < self.tableWidget_alarm.rowCount():
                    self.tableWidget_alarm.setCurrentCell(self.current_row, 0)
                else:
                    self.tableWidget_alarm.setCurrentCell(self.tableWidget_alarm.rowCount() - 1, 0)
                self.set_blk()
            else:
                self.set_blk()

    def save(self):
        if self.fmove:
            self.fmove = False
            self.save_dict()
        if self.fcng:
            self.fcng = False
            self.set_chng()
            self.changed_cell()
        if self.fapp:
            self.fapp = False
            self.set_chng()
            self.changed_cell()
        if self.fsort:
            self.fsort = False
            self.save_dict()
        self.set_blk()

    def set_chng(self):
        row = self.tableWidget_alarm.currentRow()
        col = self.tableWidget_alarm.currentColumn()
        dt = datetime.datetime(2000, 1, 1, 00, 00)
        dt = dt.date()
        if self.radioB_evd.isChecked():
            self.alarm_dictionaries[row]["type"] = 0
            self.alarm_dictionaries[row]["period"] = "x"
            self.alarm_dictionaries[row]["date"] = dt
        elif self.radioB_wd.isChecked():
            period = "0000000"
            l_period = list(period)
            self.alarm_dictionaries[row]["type"] = 1
            for checkBox in self.findChildren(QCheckBox):
                if checkBox.objectName()[0:10] == "checkBox_d":
                    chk = int(checkBox.objectName()[-1])
                    if checkBox.isChecked():
                        l_period[chk] = "1"
            period = ''.join(l_period)
            self.alarm_dictionaries[row]["period"] = period
            self.alarm_dictionaries[row]["date"] = dt
        elif self.radioB_date.isChecked():
            self.alarm_dictionaries[row]["type"] = 2
            self.alarm_dictionaries[row]["period"] = "x"
            self.alarm_dictionaries[row]["date"] = self.dateEdit_d.date().toPyDate()
        self.alarm_dictionaries[row]["activate"] = 1 if self.checkB_act.isChecked() else 0
        self.alarm_dictionaries[row]["time"] = self.timeEdit_t.time().toPyTime()
        self.alarm_dictionaries[row]["name"] = self.lineE_alarm_name.text()
        self.save_dict()
        self.chg_row(self.alarm_dictionaries[row], row)
        self.tableWidget_alarm.setCurrentCell(row, col)

    def save_dict(self):
        current_row = self.tableWidget_alarm.currentRow()
        current_column = self.tableWidget_alarm.currentColumn()
        if current_column<0:
            current_column=0
        with open(self.alarm_dictionaries_file, "w") as file:
            for dictionary in self.alarm_dictionaries:
                file.write(str(dictionary) + "\n")
        if current_row >= 0:
            self.tableWidget_alarm.setCurrentCell(current_row, current_column)

    def canc_chng(self):
        #current_row = self.tableWidget_alarm.currentRow()
        current_column = self.tableWidget_alarm.currentColumn()
        if current_column<0:
            current_column=0
        self.tableWidget_alarm.setRowCount(0)
        self.load_table()
        self.set_blk()
        if self.fmove:
            self.fmove = False
            self.tableWidget_alarm.setCurrentCell(self.current_row, current_column)
        if self.fcng:
            self.fcng = False
            self.tableWidget_alarm.setCurrentCell(self.current_row, current_column)
        if self.fapp:
            self.tableWidget_alarm.setCurrentCell(self.current_row, current_column)
            self.fapp = False
        if self.fsort:
            self.fsort = False

        #if current_row >= 0:
        #    self.tableWidget_alarm.setCurrentCell(current_row, current_column)

    def chng(self):
        self.current_row=self.tableWidget_alarm.currentRow()
        self.set_edit()
        self.fcng = True

    def app(self):
        row = self.tableWidget_alarm.rowCount()
        self.current_row=self.tableWidget_alarm.currentRow()
        dt = datetime.datetime(2000, 1, 1, 00, 00)
        tm = dt.time()
        self.alarm_dictionaries.append(
            {"name": "", "type": 0, "period": "x", "date": dt, "time": tm, "activate": 1, "sound": ""})
        self.tableWidget_alarm.insertRow(row)
        row = self.tableWidget_alarm.rowCount() - 1
        self.chg_row(self.alarm_dictionaries[row], row)
        self.tableWidget_alarm.setCurrentCell(row, 0)
        self.set_edit()
        self.fapp = True

    def set_edit(self):
        self.tableWidget_alarm.setEnabled(False)
        self.pushB_chng.setEnabled(False)
        self.pushB_del.setEnabled(False)
        self.pushB_del_old.setEnabled(False)
        self.pushB_app.setEnabled(False)
        self.pushB_exit.setEnabled(False)
        self.pushB_save.setEnabled(True)
        self.pushB_canc_chng.setEnabled(True)
        self.pushB_mov_up.setEnabled(False)
        self.pushB_mov_down.setEnabled(False)
        self.lineE_alarm_name.setEnabled(True)
        self.radioB_evd.setEnabled(True)
        self.radioB_wd.setEnabled(True)
        self.radioB_date.setEnabled(True)
        self.checkB_act.setEnabled(True)
        self.pushB_soundA.setEnabled(True)
        self.pushB_sound_cA.setEnabled(True)
        self.pushB_sound_resA.setEnabled(True)
        self.pushB_sort.setEnabled(False)
        self.timeEdit_t.setEnabled(True)
        self.chng_type()

    def mov_up(self):
        self.pushB_chng.setEnabled(False)
        self.pushB_del.setEnabled(False)
        self.pushB_del_old.setEnabled(False)
        self.pushB_app.setEnabled(False)
        self.pushB_save.setEnabled(True)
        self.pushB_canc_chng.setEnabled(True)
        self.pushB_exit.setEnabled(False)
        self.pushB_sort.setEnabled(False)
        if not self.fmove:
            self.current_row=self.tableWidget_alarm.currentRow()
        self.fmove = True
        currert_row = self.tableWidget_alarm.currentRow()
        currert_column = self.tableWidget_alarm.currentColumn()
        column_count = self.tableWidget_alarm.columnCount()
        if currert_row > 0:
            for i in range(column_count):
                titem = self.tableWidget_alarm.takeItem(currert_row, i)
                pitem = self.tableWidget_alarm.takeItem(currert_row - 1, i)
                self.tableWidget_alarm.setItem(currert_row - 1, i, titem)
                self.tableWidget_alarm.setItem(currert_row, i, pitem)
                self.tableWidget_alarm.setCurrentCell(currert_row - 1, currert_column)
            self.alarm_dictionaries[currert_row], self.alarm_dictionaries[currert_row - 1] = self.alarm_dictionaries[
                currert_row - 1], self.alarm_dictionaries[currert_row]
            self.changed_cell()

    def mov_down(self):
        self.pushB_chng.setEnabled(False)
        self.pushB_del.setEnabled(False)
        self.pushB_del_old.setEnabled(False)
        self.pushB_app.setEnabled(False)
        self.pushB_save.setEnabled(True)
        self.pushB_canc_chng.setEnabled(True)
        self.pushB_exit.setEnabled(False)
        self.pushB_sort.setEnabled(False)
        if not  self.fmove:
            self.current_row=self.tableWidget_alarm.currentRow()
        self.fmove = True
        currert_row = self.tableWidget_alarm.currentRow()
        currert_column = self.tableWidget_alarm.currentColumn()
        column_count = self.tableWidget_alarm.columnCount()
        maxrow = self.tableWidget_alarm.rowCount()
        if currert_row < maxrow - 1:
            for i in range(column_count):
                titem = self.tableWidget_alarm.takeItem(currert_row, i)
                pitem = self.tableWidget_alarm.takeItem(currert_row + 1, i)
                self.tableWidget_alarm.setItem(currert_row + 1, i, titem)
                self.tableWidget_alarm.setItem(currert_row, i, pitem)
                self.tableWidget_alarm.setCurrentCell(currert_row + 1, currert_column)
            self.alarm_dictionaries[currert_row], self.alarm_dictionaries[currert_row + 1] = self.alarm_dictionaries[
                currert_row + 1], self.alarm_dictionaries[currert_row]
            self.changed_cell()

    def set_blk(self):
        self.tableWidget_alarm.setEnabled(True)
        self.pushB_app.setEnabled(True)
        self.pushB_exit.setEnabled(True)
        self.pushB_save.setEnabled(False)
        self.pushB_canc_chng.setEnabled(False)
        self.lineE_alarm_name.setEnabled(False)
        self.radioB_evd.setEnabled(False)
        self.radioB_wd.setEnabled(False)
        self.radioB_date.setEnabled(False)
        self.dateEdit_d.setEnabled(False)
        self.timeEdit_t.setEnabled(False)
        self.checkB_act.setEnabled(False)
        self.pushB_soundA.setEnabled(False)
        self.pushB_sound_resA.setEnabled(False)
        for checkBox in self.findChildren(QCheckBox):
            if checkBox.objectName()[0:10] == "checkBox_d":
                checkBox.setEnabled(False)
        if self.tableWidget_alarm.rowCount() == 0:
            self.pushB_chng.setEnabled(False)
            self.pushB_del.setEnabled(False)
            self.pushB_del_old.setEnabled(False)
            self.pushB_sound_cA.setEnabled(False)
            self.pushB_sort.setEnabled(False)

        else:
            self.pushB_chng.setEnabled(True)
            self.pushB_del.setEnabled(True)
            self.pushB_del_old.setEnabled(True)
            self.pushB_sound_cA.setEnabled(True)
            self.pushB_sort.setEnabled(True)

    def changed_cell(self):
        if self.tableWidget_alarm.currentRow() == 0 or self.tableWidget_alarm.rowCount() == 0:
            self.pushB_mov_up.setEnabled(False)
        else:
            self.pushB_mov_up.setEnabled(True)
        if self.tableWidget_alarm.currentRow() == self.tableWidget_alarm.rowCount() - 1:
            self.pushB_mov_down.setEnabled(False)
        else:
            self.pushB_mov_down.setEnabled(True)
        currert_row = self.tableWidget_alarm.currentRow()
        self.set_row()

    def set_row(self):
        if self.tableWidget_alarm.rowCount() == 0:
            for checkBox in self.findChildren(QCheckBox):
                if checkBox.objectName()[0:10] == "checkBox_d":
                    checkBox.setChecked(False)
        else:
            tdict = self.alarm_dictionaries[self.tableWidget_alarm.currentRow()]
            self.lineE_alarm_name.setText(tdict["name"])
            self.timeEdit_t.setTime(tdict["time"])
            self.checkB_act.setChecked(tdict["activate"] == 1)
            self.dateEdit_d.setDate(tdict["date"])
            self.soundnameA = tdict["sound"]
            self.label_soundA.setText(os.path.basename(self.soundnameA))
            if tdict["type"] == 0:
                self.radioB_evd.setChecked(True)
                for checkBox in self.findChildren(QCheckBox):
                    if checkBox.objectName()[0:10] == "checkBox_d":
                        checkBox.setChecked(False)

            elif tdict["type"] == 1:
                self.radioB_wd.setChecked(True)
                period = tdict["period"]
                for checkBox in self.findChildren(QCheckBox):
                    if checkBox.objectName()[0:10] == "checkBox_d":
                        chk = int(checkBox.objectName()[-1])
                        if period[chk] == "1":
                            checkBox.setChecked(True)
                        else:
                            checkBox.setChecked(False)
            elif tdict["type"] == 2:
                self.radioB_date.setChecked(True)
                for checkBox in self.findChildren(QCheckBox):
                    if checkBox.objectName()[0:10] == "checkBox_d":
                        checkBox.setChecked(False)

    def closeEvent(self, event):
        if self.pushB_exit.isEnabled():
            # Ваше действие при закрытии окна
            self.settings.setValue(self.window_section + "/geometry", self.saveGeometry())  # Сохранение размера окна
            event.accept()  # Закрываем окно
        else:
            event.ignore()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            return
        else:
            return super().keyPressEvent(a0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Window = Dlg_Alarm()
    Window.show()
    sys.exit(app.exec_())
