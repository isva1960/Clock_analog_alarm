from RGB_Clock import Ui_Rgb_Clock
import sys
from PyQt5 import QtWidgets, Qt , QtGui
from PyQt5.QtWidgets import  QMessageBox
from PyQt5.QtCore import QSettings

ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"


class RGB_Window(QtWidgets.QMainWindow, Ui_Rgb_Clock):  # Создаем свой класс на базе класса Ui_MainWindow
    def __init__(self, root):
        super().__init__()
        self.mainw = root
        # def __init__(self):
        #    super().__init__()
        self.setupUi(self)
        self.mainw.clock.setting = True
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Colors_Window"  # Секция параметров окна
        self.values_section = "Values"  # Секция параметров переменных
        self.colors_section = "Colors"  #
        self.pushB_colors_exit.clicked.connect(self.run_exit)
        self.pushB_colors_save.clicked.connect(self.run_save)
        self.pushB_colors_canc.clicked.connect(self.set_color)
        self.pushB_colors_reset.clicked.connect(self.reset_color)
        self.pushB_colors_canc.clicked.connect(self.canc_color)
        self.radioB_ssize.clicked.connect(self.chng_size)
        self.radioB_bsize.clicked.connect(self.chng_size)
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна
        if self.settings.contains(self.window_section + "/windowState"):
            self.restoreState(
                self.settings.value(self.window_section + "/windowState"))  # Восстановление состояния окна
        self.mainw.tab_Clock.setCurrentIndex(0)
        self.set_color()

    def chng_size(self):
        if self.radioB_bsize.isChecked():
            self.mainw.clock.type_clock = 0
        else:
            self.mainw.clock.type_clock = 1
        self.mainw.clock.chng_type_clock()
        self.mainw.clock.update()

    def canc_color(self):
        self.set_color()
        self.mainw.clock.set_color_clock()
        self.mainw.clock.set_type_clock()
        self.mainw.clock.update()

    def set_color(self):
        for slider in self.findChildren(Qt.QSlider):
            xx_c = slider.objectName()[6:]
            colors = self.settings.value(self.colors_section + "/" + xx_c, defaultValue=-1)
            if colors > -1:
                slider.setValue(colors)
            slider.valueChanged.connect(self.chng_color)
            val = "self.Lblv_" + xx_c + ".setText(str(slider.value()))"
            eval(val)
        size = self.mainw.clock.chng_type_clock()
        if size == 0:
            self.radioB_bsize.setChecked(True)
            self.radioB_ssize.setChecked(False)
        else:
            self.radioB_bsize.setChecked(False)
            self.radioB_ssize.setChecked(True)
        self.mainw.clock.update()

    def reset_color(self):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Внимание!!!")
        msgtxt = "Настройки будут установлены на основе параметров заданных в программе\nпутем удаления ветки реестра.\nПосле устновки данное окно будет закрыто.\nУстанавливать первоначальные значения?"
        msgbox.setText(msgtxt)
        msgbox.setIcon(QMessageBox.Warning)
        iconw = QtGui.QIcon()
        iconw.addPixmap(QtGui.QPixmap(":/question_115172.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        msgbox.setWindowIcon(iconw)
        msgbox.addButton('Да', QtWidgets.QMessageBox.YesRole)
        bt_no=msgbox.addButton('Нет', QtWidgets.QMessageBox.NoRole)
        msgbox.setDefaultButton(bt_no)
        result = msgbox.exec_()
        if result == 0:
            self.settings.remove(self.colors_section)
            self.mainw.clock.set_dict_colors()
            self.mainw.clock.set_color_clock()
            self.mainw.clock.set_type_clock()
            self.mainw.clock.update()
            self.close()

    def chng_color(self):
        slider = self.sender()
        xx_c = slider.objectName()[6:]
        val = "self.Lblv_" + xx_c + ".setText(str(slider.value()))"
        eval(val)
        self.mainw.clock.dic_colors[xx_c]=slider.value()
        self.mainw.clock.chng_color_clock()
        self.mainw.clock.update()


    def run_save(self):
        for slider in self.findChildren(Qt.QSlider):
            xx_c = slider.objectName()[6:]
            colors = slider.value()
            self.settings.setValue(self.colors_section + "/" + xx_c, slider.value())
        self.settings.setValue(self.colors_section + "/size", (0 if self.radioB_bsize.isChecked() else 1))

    def run_exit(self):
        self.close()

    def closeEvent(self, event):
        self.settings.setValue(self.window_section + "/geometry", self.saveGeometry())  # Сохранение размера окна
        self.settings.setValue(self.window_section + "/windowState", self.saveState())  # Сохранение состояния окна
        self.mainw.clock.setting = False
        self.mainw.rgb_win = None


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Window = RGB_Window()
    Window.show()
    sys.exit(app.exec_())
