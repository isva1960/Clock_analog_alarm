from PyQt5.QtGui import QKeyEvent

from Clock_Timer_Sound_dlg import \
    Ui_Clock_Timer_Sound  # Импортируем класс Ui_MainWindow из модуля Mainwindow созданного в дизайнере.
import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSettings, Qt
import pygame
import locale

ORGANIZATION_NAME = "isva_company"
APPLICATION_NAME = "Clock_Alarm_Application"
TAIMER_START_TXT = "Сработал таймер!!!"
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


# pygame.init()

class Dlg_Sound(QDialog, Ui_Clock_Timer_Sound):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs, flags=Qt.WindowCloseButtonHint)
        self.main = root
        self.setupUi(self)
        self.soundname = ""
        self.label_sound.setText(os.path.basename(self.soundname))
        self.pushB_start_pause.clicked.connect(self.sound_start_pause)
        self.pushB_stop.clicked.connect(self.sound_stop)
        self.start_alarm = 0
        self.pushB_stop.setEnabled(False)
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.window_section = "Sound_Window"  # Секция параметров окна
        self.values_section = "Values"  # Секция параметров переменных
        if self.settings.contains(self.window_section + "/geometry"):
            self.restoreGeometry(self.settings.value(self.window_section + "/geometry"))  # Восстановление размера окна

    def set_objnane(self):
        self.soundname = self.main.soundnameA
        if not os.path.exists(self.soundname):
            self.label_sound.setText("Не задан или не найден файл мелодии!!!")
            self.pushB_stop.setEnabled(False)
            self.pushB_start_pause.setEnabled(False)
        else:
            self.label_sound.setText(os.path.basename(self.soundname))

    def sound_start_pause(self):
        if self.start_alarm == 0:
            self.start_alarm = 1
            self.pushB_start_pause.setText("Пауза")
            self.pushB_stop.setEnabled(True)
            pygame.mixer.music.load(self.soundname)
            pygame.mixer.music.play()
        elif self.start_alarm == 1:
            self.start_alarm = 2
            self.pushB_start_pause.setText("Продолжить")
            self.pushB_stop.setEnabled(True)
            pygame.mixer.music.pause()
        elif self.start_alarm == 2:
            self.start_alarm = 1
            self.pushB_start_pause.setText("Пауза")
            self.pushB_stop.setEnabled(True)
            pygame.mixer.music.unpause()

    def sound_stop(self):
        self.start_alarm = 0
        self.pushB_start_pause.setText("Старт")
        self.pushB_stop.setEnabled(False)
        pygame.mixer.music.stop()

    def closeEvent(self, event):
        # Ваше действие при закрытии окна
        self.settings.setValue(self.window_section + "/geometry", self.saveGeometry())  # Сохранение размера окна
        try:
            pygame.mixer.music.stop()
            # pygame.quit()
        except Exception:
            pass
        event.accept()  # Закрываем окно

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            return
        else:
            return super().keyPressEvent(a0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Window = Dlg_Sound()
    Window.show()
    sys.exit(app.exec_())
