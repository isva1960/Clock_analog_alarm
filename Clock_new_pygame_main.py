# Данные не изменяются в tableWidget.
import os
from PyQt5 import QtGui
from Clock_new_p import Ui_Clock_Window
from PyQt5.QtGui import QPainter, QPolygon, QFont, QPen, QColor
from PyQt5.QtCore import QPoint, QTimer, QLockFile, QDir, QTime
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog, QMenu, QAction, QSystemTrayIcon
# - Внутри pygame.pkgdata используется модуль pkg_resources из пакета setuptools.
# - Начиная с версии setuptools>=81, pkg_resources считается устаревшим и будет удалён к концу 2025 года.
# - Поэтому при import pygame ты видишь предупреждение UserWarning.
import warnings
import pygame

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("default", category=UserWarning)

import shutil
from My_utils import date_to_str

from Clock_Timer_m_utils import *
from Clock_Timer_Alarm_dlg_pygame_M import Dlg_Alarm
from Clock_Timer_Alarm_msg_M import *
from RGB_Clock_M import RGB_Window

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"
pygame.init()


class WindowClock(QtWidgets.QMainWindow, Ui_Clock_Window):
    def __init__(self):
        super().__init__()
        self.msg_txt = None
        self.alarm_date_time_start = None
        self.setupUi(self)
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Main_Window"  # Секция параметров окна
        self.values_section = "Values"  # Секция параметров переменных
        self.colors_section = "Colors"  #
        self.tableWidget_day_alarm.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # !!!
        self.tableWidget_day_alarm.setColumnHidden(5, True)
        self.pushButton_exit.clicked.connect(self.close)
        self.pushB_alarm_setting.clicked.connect(self.alarm_setting)
        self.pushB_save_alarm.clicked.connect(self.save_alarm)
        self.pushB_alarm_dictionaries_f.clicked.connect(self.set_alarm_dictionaries_f)
        self.checkB_yes_alarm.stateChanged.connect(self.blk_yes_alarm)
        self.pushB_alarm_stop.clicked.connect(self.alarm_stop)
        self.pushB_clface.clicked.connect(self.cl_face)
        self.pushB_alarm_stop.setEnabled(False)
        self.start_alarm = False
        self.wnd_act = False
        self.rgb_win = None
        self.kol_alarm = 0
        self.current_index = 0
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна
        if self.settings.contains(self.window_section + "/windowState"):
            self.restoreState(
                self.settings.value(self.window_section + "/windowState"))  # Восстановление состояния окна
        self.tab_Clock.setCurrentIndex(0)
        self.alarm_dictionaries_file = self.settings.value(self.values_section + "/Alarm_dictionaries_file", "",
                                                           type=str)
        self.spinB_alarm_int.setValue(self.settings.value(self.values_section + "/Alarm_int", 0, type=int))
        self.spinB_repeat_int.setValue(self.settings.value(self.values_section + "/Alarm_repeat_int", 0, type=int))
        self.spinB_repeat_kol.setValue(self.settings.value(self.values_section + "/Alarm_repeat_kol", 0, type=int))
        self.checkB_tray.setChecked(
            self.settings.value(self.window_section + "/Is_tray", False, type=bool))
        self.checkB_yes_alarm.setChecked(
            self.settings.value(self.values_section + "/Alarm_yes", False, type=bool))
        self.tray_icon = QSystemTrayIcon(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Clock_31089.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tray_icon.setIcon(icon)
        show_action = QAction("Показать", self)
        quit_action = QAction("Выйти", self)
        hide_action = QAction("Скрыть", self)
        show_action.triggered.connect(self.window_active)  # type: ignore
        hide_action.triggered.connect(self.hide)  # type: ignore
        quit_action.triggered.connect(self.close)  # type: ignore

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.blk_yes_alarm2()
        self.clock = Clock(self, self)
        self.gridLayout_2.addWidget(self.clock, 0, 0)

    def cl_face(self):
        self.rgb_win = RGB_Window(self)
        self.rgb_win.show()

    def blk_yes_alarm(self):
        self.blk_yes_alarm2()
        self.set_alarm()

    def blk_yes_alarm2(self):
        if self.checkB_yes_alarm.isChecked():
            self.spinB_alarm_int.setEnabled(True)
            self.spinB_repeat_int.setEnabled(True)
            self.spinB_repeat_kol.setEnabled(True)
            self.pushB_alarm_dictionaries_f.setEnabled(True)
            self.pushB_alarm_setting.setEnabled(True)
            self.label_alarm_dictionaries.setText(os.path.basename(self.alarm_dictionaries_file))
        else:
            self.spinB_alarm_int.setEnabled(False)
            self.spinB_repeat_int.setEnabled(False)
            self.spinB_repeat_kol.setEnabled(False)
            self.pushB_alarm_dictionaries_f.setEnabled(False)
            self.pushB_alarm_setting.setEnabled(False)
            self.label_alarm_dictionaries.setText("")

    def chk_set_alarm(self):
        f_cont = True
        if self.checkB_yes_alarm.isChecked():
            if self.alarm_dictionaries_file:
                self.label_alarm_dictionaries.setText(os.path.basename(self.alarm_dictionaries_file))
                if not os.path.exists(self.alarm_dictionaries_file):
                    self.msg_error("ОШИБКА!",
                                   "Не найден файл параметров звонков: " + self.alarm_dictionaries_file + "\nНа закладке Настройка будильников и параметров задайте другое имя этого файла (кнопка Файл параметров звонков).\nИначе программа будет работать без будильников!",
                                   QMessageBox.Critical,
                                   ":/Error.ico")
                    f_cont = False
            else:
                self.label_alarm_dictionaries.setText("")
                self.msg_error("ОШИБКА!",
                               "Не задан файл параметров звонков!\nНа закладке Настройка будильников и параметров задайте имя этого файла (кнопка Файл параметров звонков).\nИначе программа будет работать без будильников!",
                               QMessageBox.Warning, ":/warning.ico")
                f_cont = False
        # else:
        #    f_cont=False
        return f_cont

    def save_alarm(self):
        self.settings.setValue(self.values_section + "/Alarm_int", (self.spinB_alarm_int.value()))
        self.settings.setValue(self.values_section + "/Alarm_repeat_int", (self.spinB_repeat_int.value()))
        self.settings.setValue(self.values_section + "/Alarm_repeat_kol", (self.spinB_repeat_kol.value()))
        self.settings.setValue(self.values_section + "/Alarm_yes", str(self.checkB_yes_alarm.isChecked()))
        if self.chk_set_alarm():
            self.set_alarm()

    def set_alarm_dictionaries_f(self):
        old_alarm_dictionaries_file = self.alarm_dictionaries_file
        if old_alarm_dictionaries_file:
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Внимание!!!")
            msg_txt = "Файл параметров звонков:\n" + old_alarm_dictionaries_file + "\nВыбрать новый?"
            msgbox.setText(msg_txt)
            msgbox.setIcon(QMessageBox.Warning)
            icon_w = QtGui.QIcon()
            icon_w.addPixmap(QtGui.QPixmap(":/question_115172.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msgbox.setWindowIcon(icon_w)
            msgbox.addButton('Да', QtWidgets.QMessageBox.YesRole)
            bt_no = msgbox.addButton('Нет', QtWidgets.QMessageBox.NoRole)
            msgbox.setDefaultButton(bt_no)
            result = msgbox.exec_()
            if result == 0:
                new_alarm_dictionaries_file = \
                    QFileDialog.getSaveFileName(self, "Файл параметров звонков ", old_alarm_dictionaries_file)[0]
                if new_alarm_dictionaries_file:
                    if old_alarm_dictionaries_file != new_alarm_dictionaries_file:
                        self.alarm_dictionaries_file = new_alarm_dictionaries_file
                        if os.path.exists(old_alarm_dictionaries_file):
                            shutil.copy2(old_alarm_dictionaries_file, new_alarm_dictionaries_file)
                            os.remove(old_alarm_dictionaries_file)
                        else:
                            open(self.alarm_dictionaries_file, "w").close()
        else:
            new_alarm_dictionaries_file = \
                QFileDialog.getSaveFileName(self, "Файл параметров звонков ", old_alarm_dictionaries_file)[0]
            self.alarm_dictionaries_file = new_alarm_dictionaries_file
            open(self.alarm_dictionaries_file, "w").close()
        self.settings.setValue(self.values_section + "/Alarm_dictionaries_file", self.alarm_dictionaries_file)
        if self.alarm_dictionaries_file:
            self.label_alarm_dictionaries.setText(os.path.basename(self.alarm_dictionaries_file))

    def alarm_setting(self):
        if not self.chk_set_alarm():
            return
        dialog = Dlg_Alarm(self)
        dialog.alarm_dictionaries_file = self.alarm_dictionaries_file
        dialog.exec()
        self.set_alarm()

    def update_clock(self):
        current_date_time = datetime.datetime.now()
        if not self.start_alarm:
            if self.tableWidget_day_alarm.rowCount() > 0:
                t_date_time = datetime.datetime.strptime(self.tableWidget_day_alarm.item(0, 0).text(), '%d.%m.%Y %H:%M')
                if t_date_time <= current_date_time:
                    self.tab_Clock.setCurrentIndex(1)
                    self.alarm_date_time_start = current_date_time
                    self.pushB_alarm_stop.setEnabled(True)
                    self.pushB_alarm_setting.setEnabled(False)
                    self.start_alarm = True
                    self.tableWidget_day_alarm.setItem(0, 4,
                                                       QtWidgets.QTableWidgetItem("Будильник сработал"))
                    sound = self.tableWidget_day_alarm.item(0, 5).text()
                    if sound:
                        if not os.path.exists(sound):
                            self.msg_txt = "Не найден файл звонка!!!\n" + sound
                            self.show_message_tray(self.msg_txt)
                            dialog = Dlg_Msg(self)
                            dialog.show()
                        else:
                            pygame.mixer.music.load(sound)
                            pygame.mixer.music.play()
                    else:
                        self.msg_txt = "Будильник сработал! Не задана мелодия!"
                        self.show_message_tray(self.msg_txt)
                        dialog = Dlg_Msg(self)
                        dialog.show()
                    self.window_active()
        else:
            cur_int = int((current_date_time - self.alarm_date_time_start).total_seconds() / 60)
            if cur_int >= self.spinB_repeat_int.value():
                self.kol_alarm += 1
                if self.kol_alarm > self.spinB_repeat_kol.value():
                    strerror = f"Остановлен будильник\n{self.tableWidget_day_alarm.item(0, 1).text()}\nДата и время: {self.tableWidget_day_alarm.item(0, 0).text()}\nПериодичность: {self.tableWidget_day_alarm.item(0, 2).text()}\nПериод: {self.tableWidget_day_alarm.item(0, 3).text()}"
                    self.msg_txt = strerror
                    self.show_message_tray(self.msg_txt)
                    dialog = Dlg_Msg(self)
                    dialog.show()
                    self.alarm_stop()
                    self.tab_Clock.setCurrentIndex(1)
                else:
                    self.alarm_date_time_start = current_date_time
                    self.tab_Clock.setCurrentIndex(1)
                    self.tableWidget_day_alarm.setItem(0, 4,
                                                       QtWidgets.QTableWidgetItem(f"Повтор {self.kol_alarm}"))
                    sound = self.tableWidget_day_alarm.item(0, 5).text()
                    if sound:
                        if not os.path.exists(sound):
                            self.msg_txt = "Не найден файл звонка!!!\n" + sound
                            self.show_message_tray(self.msg_txt)
                            dialog = Dlg_Msg(self)
                            dialog.show()
                        else:
                            pygame.mixer.music.load(sound)
                            pygame.mixer.music.play()

    def window_active(self):
        self.wnd_act = True
        self.setWindowState(Qt.WindowMinimized)
        self.setWindowState(Qt.WindowActive)
        self.show()
        self.raise_()
        self.setFocus()
        self.wnd_act = False

    def alarm_stop(self):
        row_count = self.tableWidget_day_alarm.rowCount()
        current_date_time = datetime.datetime.now()
        strerror = ""
        for i in range(1, row_count):
            t = self.tableWidget_day_alarm.item(i, 0).text()
            t_date_time = datetime.datetime.strptime(t, '%d.%m.%Y %H:%M')
            if t_date_time < current_date_time:
                strerror = strerror + f"Пропущен будильник!!!!!!!!!!!!!\n{self.tableWidget_day_alarm.item(i, 1).text()}\nДата и время: {self.tableWidget_day_alarm.item(i, 0).text()}\nПериодичность: {self.tableWidget_day_alarm.item(i, 2).text()}\nПериод: {self.tableWidget_day_alarm.item(i, 3).text()}\n\n"
        if strerror:
            self.msg_txt = strerror
            self.show_message_tray(self.msg_txt)
            dialog = Dlg_Msg(self)
            dialog.show()
        try:
            pygame.mixer.music.stop()
        except (Exception,):
            pass
        self.pushB_alarm_stop.setEnabled(False)
        self.pushB_alarm_setting.setEnabled(True)
        self.start_alarm = False
        self.kol_alarm = 0
        self.set_alarm()

    def set_alarm(self):
        if not self.chk_set_alarm():
            return
        lst_time = []
        interval = 0
        current_date_time = datetime.datetime.now()
        if self.checkB_yes_alarm.isChecked():
            with open(self.alarm_dictionaries_file, "r") as file:
                alarm_dictionaries = [eval(line) for line in file]
            current_date = current_date_time.date()
            current_time = current_date_time.time()
            current_weekday = current_date_time.date().weekday()
            next_date_time = current_date_time + datetime.timedelta(days=1)
            next_date = next_date_time.date()
            next_weekday = next_date_time.date().weekday()
            j = 0
            interval: int = self.spinB_alarm_int.value()
            for alarm in alarm_dictionaries:
                # 'name'
                # 'type'
                # 'period'
                # 'date'
                # 'time'
                # 'activate'
                # 'sound'
                if alarm['activate'] == 1:
                    if alarm['time'] >= current_time:
                        current_alarm = ""
                        if alarm['type'] == 0:
                            current_alarm = alarm['time']
                        elif alarm['type'] == 1:
                            period = alarm["period"]
                            i = 0
                            for c in period:
                                if c == "1":
                                    if current_weekday == i:
                                        current_alarm = alarm['time']
                                i += 1
                        elif alarm['type'] == 2:
                            if alarm["date"] == current_date:
                                current_alarm = alarm['time']
                        if current_alarm:
                            x2 = current_date.strftime("%Y.%m.%d") + " " + str(current_alarm)[0:5]
                            lst_time.append(
                                f"{x2}~{str(j).zfill(4)}~{alarm['name']}~{type_alarm[alarm['type']]}~{ret_priod(alarm['period'], alarm['date'], alarm['type'])}~{alarm['sound']}")
                            j += 1
                    elif alarm['time'] < current_time:
                        current_alarm = ""
                        if alarm['type'] == 0:
                            current_alarm = alarm['time']
                        elif alarm['type'] == 1:
                            period = alarm["period"]
                            i = 0
                            for c in period:
                                if c == "1":
                                    if next_weekday == i:
                                        current_alarm = alarm['time']
                                i += 1
                        elif alarm['type'] == 2:
                            if alarm["date"] == next_date:
                                current_alarm = alarm['time']
                        if current_alarm:
                            x2 = next_date.strftime("%Y.%m.%d") + " " + str(current_alarm)[0:5]
                            lst_time.append(
                                f"{x2}~{str(j).zfill(4)}~{alarm['name']}~{type_alarm[alarm['type']]}~{ret_priod(alarm['period'], alarm['date'], alarm['type'])}~{alarm['sound']}")

                            j += 1
        lst_time.sort(key=get_key_alarm)
        self.tableWidget_day_alarm.setRowCount(0)
        p_date_time = current_date_time + datetime.timedelta(days=-1)
        for alarm in lst_time:
            lst_alarm = alarm.split("~")
            row = self.tableWidget_day_alarm.rowCount()
            t_date_time = datetime.datetime.strptime(lst_alarm[0], '%Y.%m.%d %H:%M')
            raz = (t_date_time - p_date_time).total_seconds() / 60
            self.tableWidget_day_alarm.insertRow(row)
            f_date_time = t_date_time.strftime('%d.%m.%Y %H:%M')
            self.tableWidget_day_alarm.setItem(row, 0,
                                               QtWidgets.QTableWidgetItem(f_date_time))
            self.tableWidget_day_alarm.setItem(row, 1,
                                               QtWidgets.QTableWidgetItem(lst_alarm[2]))
            self.tableWidget_day_alarm.setItem(row, 2,
                                               QtWidgets.QTableWidgetItem(lst_alarm[3]))
            self.tableWidget_day_alarm.setItem(row, 3,
                                               QtWidgets.QTableWidgetItem(lst_alarm[4]))
            if raz < interval:
                self.tableWidget_day_alarm.setItem(row, 4,
                                                   QtWidgets.QTableWidgetItem("Будет пропущен"))
            else:
                p_date_time = t_date_time
            self.tableWidget_day_alarm.setItem(row, 5,
                                               QtWidgets.QTableWidgetItem(lst_alarm[5]))
        self.tableWidget_day_alarm.setCurrentCell(0, 0)

    def changeEvent(self, event):
        if self.isMinimized():
            if self.checkB_tray.isChecked():
                if not self.wnd_act:
                    self.hide()
                    self.show_message_tray("Приложение свернуто в трей")

    def show_message_tray(self, msg_txt):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/clock_time_time_6970.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tray_icon.showMessage(
            self.windowTitle(),
            msg_txt,
            icon,
            2000
        )

    def closeEvent(self, event):
        # Ваше действие при закрытии окна
        self.settings.setValue(self.window_section + "/geometry", self.saveGeometry())  # Сохранение размера окна
        self.settings.setValue(self.window_section + "/windowState", self.saveState())  # Сохранение состояния окна
        self.settings.setValue(self.window_section + "/Is_tray", str(self.checkB_tray.isChecked()))

        try:
            pygame.mixer.music.stop()
            pygame.quit()
        except (Exception,):
            pass
        finally:
            pygame.quit()
        if self.rgb_win is not None:
            self.rgb_win.close()
        event.accept()  # Закрываем окно

    def msg_error(self, title, txt_err, icon, icon_w):
        error = QMessageBox()
        error.setWindowTitle(title)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(icon_w), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        error.setWindowIcon(icon1)
        error.setText(txt_err)
        error.setIcon(icon)
        error.setStandardButtons(QMessageBox.Ok)
        if self.settings.contains(self.window_section + "/msg_geometry"):
            error.restoreGeometry(
                self.settings.value(self.window_section + "/msg_geometry"))  # Восстановление размера окна
        error.exec_()
        self.settings.setValue(self.window_section + "/msg_geometry", error.saveGeometry())  # Сохранение размера окна


class Clock(QWidget):
    # def __init__(self):
    #    super().__init__()
    def __init__(self, root, parent=None):
        super(Clock, self).__init__(parent)
        self.secondHand = None
        self.minuteHand = None
        self.hourHand = None
        self.type_clock = None
        self.dic_colors = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update1)  # type: ignore
        self.setting = False
        self.timer_int = (1000000 if self.setting else 1000)
        self.timer.start(self.timer_int)
        self.main = root
        self.ellipseColor = QColor(250, 255, 255)
        self.hourColor = Qt.darkGreen  # black
        self.minuteColor = Qt.blue
        self.secondColor = Qt.red
        self.hourScale = Qt.darkGreen  # black
        self.minuteScale = Qt.blue
        self.center = Qt.yellow
        self.digitColor = Qt.darkRed
        self.dateColor = Qt.darkBlue
        self.set_dict_colors()
        self.set_type_clock()
        self.set_color_clock()

    def set_dict_colors(self):
        self.dic_colors = {"bg_r": 255, "bg_g": 255, "bg_b": 255,  # Фон циферблата
                           "hh_r": 0, "hh_g": 0, "hh_b": 0,  # Часовая стрелка
                           "mh_r": 0, "mh_g": 255, "mh_b": 0,  # Минутная стрелка
                           "sh_r": 255, "sh_g": 0, "sh_b": 0,  # Секундная стрелка
                           "hs_r": 0, "hs_g": 0, "hs_b": 0,  # Часовая шкала
                           "ms_r": 0, "ms_g": 255, "ms_b": 0,  # Минутная шкала
                           "cc_r": 0, "cc_g": 255, "cc_b": 255,  # Центр циферблата
                           "dc_r": 0, "dc_g": 0, "dc_b": 0,  # Цифры
                           "cd_r": 0, "cd_g": 0, "cd_b": 255  # Текущая дата
                           }

    def set_color_clock(self):
        for elm in self.dic_colors:
            colors = self.main.settings.value(self.main.colors_section + "/" + elm, defaultValue=-1)
            if colors > -1:
                self.dic_colors[elm] = colors
        self.change_color_clock()

    def change_color_clock(self):
        self.ellipseColor = QColor(self.dic_colors["bg_r"], self.dic_colors["bg_g"], self.dic_colors["bg_b"])
        self.hourColor = QColor(self.dic_colors["hh_r"], self.dic_colors["hh_g"], self.dic_colors["hh_b"])
        self.minuteColor = QColor(self.dic_colors["mh_r"], self.dic_colors["mh_g"], self.dic_colors["mh_b"])
        self.secondColor = QColor(self.dic_colors["sh_r"], self.dic_colors["sh_g"], self.dic_colors["sh_b"])
        self.hourScale = QColor(self.dic_colors["hs_r"], self.dic_colors["hs_g"], self.dic_colors["hs_b"])
        self.minuteScale = QColor(self.dic_colors["ms_r"], self.dic_colors["ms_g"], self.dic_colors["ms_b"])
        self.center = QColor(self.dic_colors["cc_r"], self.dic_colors["cc_g"], self.dic_colors["cc_b"])
        self.digitColor = QColor(self.dic_colors["dc_r"], self.dic_colors["dc_g"], self.dic_colors["dc_b"])
        self.dateColor = QColor(self.dic_colors["cd_r"], self.dic_colors["cd_g"], self.dic_colors["cd_b"])

    def set_type_clock(self):
        self.type_clock = self.main.settings.value(self.main.colors_section + "/size", defaultValue=0)
        self.change_type_clock()

    def change_type_clock(self):
        if self.type_clock == 0:
            self.hourHand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -60)])
            self.minuteHand = QPolygon([QPoint(4, 6), QPoint(-4, 6), QPoint(0, -75)])
            self.secondHand = QPolygon([QPoint(2, 2), QPoint(-2, 2), QPoint(0, -90)])
        elif self.type_clock == 1:
            self.hourHand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)])
            self.minuteHand = QPolygon([QPoint(4, 6), QPoint(-4, 6), QPoint(0, -55)])
            self.secondHand = QPolygon([QPoint(2, 2), QPoint(-2, 2), QPoint(0, -70)])
        return self.type_clock

    def update1(self):
        self.main.update_clock()
        self.update()

    # метод для рисования часов
    def paintEvent(self, event):
        # получаем текущее время
        time = QTime.currentTime()
        # получаем минимальный размер окна
        size = min(self.width(), self.height())
        # создаем объект QPainter
        painter = QPainter(self)
        # устанавливаем антиалиасинг
        painter.setRenderHint(QPainter.Antialiasing)
        # перемещаем начало координат в центр окна
        painter.translate(self.width() / 2, self.height() / 2.2)
        # масштабируем рисование в соответствии с размером окна
        painter.scale(size / 250, size / 250)
        # рисуем циферблат
        painter.setPen(Qt.NoPen)
        # painter.setPen(QPen(Qt.cyan, 0, Qt.SolidLine))
        # painter.setBrush(Qt.green)
        painter.setBrush(self.ellipseColor)
        # painter.setBrush(QColor(240, 255, 255))
        if self.type_clock == 0:
            painter.drawEllipse(-90, -90, 180, 180)
        elif self.type_clock == 1:
            painter.drawEllipse(-70, -70, 140, 140)
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 12))
        # for i in range(1, 13):
        #    text_width = painter.fontMetrics().width(str(i))
        #    text_height = painter.fontMetrics().height()
        #    print((text_width,text_width))
        #    x=int(80 * math.cos(-i * 30 * math.pi / 180 + math.pi / 2))  - 8 # -int(text_width/2)
        #    y=int(-80 * math.sin(-30 * i * math.pi / 180 + math.pi / 2))  -5 # -int(text_height/2)
        #    print(x,y)
        #    painter.drawText(x, y, 16, 14, Qt.AlignCenter, str(i))

        painter.setPen(self.digitColor)
        painter.setFont(QFont("Arial", 12))
        if self.type_clock == 0:
            painter.drawText(-8, -105, 16, 14, Qt.AlignCenter, str(12))
            painter.drawText(43, -92, 11, 14, Qt.AlignCenter, str(1))
            painter.drawText(81, -55, 11, 14, Qt.AlignCenter, str(2))
            painter.drawText(92, -7, 11, 14, Qt.AlignCenter, str(3))
            painter.drawText(80, 41, 11, 14, Qt.AlignCenter, str(4))
            painter.drawText(40, 80, 11, 14, Qt.AlignCenter, str(5))
            painter.drawText(-5, 92, 11, 14, Qt.AlignCenter, str(6))
            painter.drawText(-55, 81, 11, 14, Qt.AlignCenter, str(7))
            painter.drawText(-92, 41, 11, 14, Qt.AlignCenter, str(8))
            painter.drawText(-103, -6, 11, 14, Qt.AlignCenter, str(9))
            painter.drawText(-100, -55, 20, 14, Qt.AlignCenter, str(10))
            painter.drawText(-58, -92, 20, 12, Qt.AlignCenter, str(11))
        if self.type_clock == 1:
            painter.drawText(-8, -85, 16, 14, Qt.AlignCenter, str(12))
            painter.drawText(31, -74, 11, 14, Qt.AlignCenter, str(1))
            painter.drawText(61, -45, 11, 14, Qt.AlignCenter, str(2))
            painter.drawText(71, -5, 11, 14, Qt.AlignCenter, str(3))
            painter.drawText(59, 32, 11, 14, Qt.AlignCenter, str(4))
            painter.drawText(31, 63, 11, 14, Qt.AlignCenter, str(5))
            painter.drawText(-6, 72, 11, 14, Qt.AlignCenter, str(6))
            painter.drawText(-46, 62, 11, 14, Qt.AlignCenter, str(7))
            painter.drawText(-73, 31, 11, 14, Qt.AlignCenter, str(8))
            painter.drawText(-82, -5, 11, 14, Qt.AlignCenter, str(9))
            painter.drawText(-78, -46, 20, 14, Qt.AlignCenter, str(10))
            painter.drawText(-48, -74, 20, 12, Qt.AlignCenter, str(11))

        painter.setFont(QFont("Arial", 10))
        painter.setPen(self.dateColor)
        current_date = datetime.datetime.now()
        today = date_to_str(current_date) + ", " + datetime.datetime.strftime(current_date, '%A')
        text_width = painter.fontMetrics().width(today)
        text_height = painter.fontMetrics().height()
        if self.type_clock == 0:
            painter.drawText(-int(text_width / 2), 115, text_width, text_height, Qt.AlignCenter, today)
        elif self.type_clock == 1:
            painter.drawText(-int(text_width / 2), 95, text_width, text_height, Qt.AlignCenter, today)

        # рисуем часовую стрелку
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.hourColor)
        painter.save()
        if not self.setting:
            painter.rotate(30 * (time.hour() + time.minute() / 60))
        else:
            painter.rotate(30 * (10 + 15 / 60))  # ????
        painter.drawConvexPolygon(self.hourHand)
        painter.restore()
        # рисуем минутную стрелку
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.minuteColor)
        painter.save()
        if not self.setting:
            painter.rotate(6 * (time.minute() + time.second() / 60))
        else:
            painter.rotate(6 * (15 + 45 / 60))  # ????
        painter.drawConvexPolygon(self.minuteHand)
        painter.restore()
        # рисуем секундную стрелку
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.secondColor)
        painter.save()
        if not self.setting:
            painter.rotate(6 * time.second())
        else:
            painter.rotate(6 * 45)  # ????
        painter.drawConvexPolygon(self.secondHand)
        painter.restore()
        # рисуем центральную точку
        painter.setPen(self.secondColor)
        # painter.setBrush(Qt.green)
        painter.setBrush(self.center)
        painter.drawEllipse(-3, -3, 6, 6)
        painter.setPen(self.minuteScale)
        if self.type_clock == 0:
            for j in range(60):
                if (j % 5) != 0:
                    painter.drawLine(86, 0, 89, 0)  # markings for minute hand
                painter.rotate(6.0)
        elif self.type_clock == 1:
            for j in range(60):
                if (j % 5) != 0:
                    painter.drawLine(66, 0, 69, 0)  # markings for minute hand
                painter.rotate(6.0)
        painter.setPen(QPen(self.hourScale, 2))
        if self.type_clock == 0:
            for i in range(12):
                painter.drawLine(85, 0, 89, 0)  # markings for hour hand
                painter.rotate(30.0)
        elif self.type_clock == 1:
            for i in range(12):
                painter.drawLine(65, 0, 69, 0)  # markings for hour hand
                painter.rotate(30.0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Window = WindowClock()
    lockfile = QLockFile(QDir.tempPath() + r'\~Clock_Alarm_Application')
    if not lockfile.tryLock(100):
        Window.msg_error("ОШИБКА!", "Приложение уже запущено!", QMessageBox.Critical, ":/Error.ico")
        sys.exit(16)
    Window.show()
    sys.exit(app.exec_())
