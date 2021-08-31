import os
import sys
import time
import json
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from des import *

from methods.SettingsPanel import *
from methods.ConnectThreadMonitor import *

# Интерфейс программы и обработчик событий внутри него
class Client(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Данные из конфига (симметричный ключ получаем в ответе от сервера)
        self.nick = None
        self.ip = None
        self.port = None
        self.smile_type = None
        self.connect_status = False

        # Экземпляр класса для обработки соединений и сигналов
        self.connect_monitor = message_monitor()
        self.connect_monitor.mysignal.connect(self.signal_handler)

        # Отключаем стандартные границы окна программы
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()

        # Обработчики основных кнопок + кнопок с панели
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_2.clicked.connect(self.connect_to_server)
        self.ui.pushButton_3.clicked.connect(lambda: self.close())
        self.ui.pushButton_4.clicked.connect(lambda: self.ui.listWidget.clear())
        self.ui.pushButton_5.clicked.connect(lambda: self.showMinimized())
        self.ui.pushButton_7.clicked.connect(self.setting_panel)

        # Обработчик смайликов
        self.ui.pushButton_10.clicked.connect(lambda: self.smile_send('1'))
        self.ui.pushButton_11.clicked.connect(lambda: self.smile_send('2'))
        self.ui.pushButton_12.clicked.connect(lambda: self.smile_send('3'))
        self.ui.pushButton_6.clicked.connect(lambda: self.smile_send('4'))
        self.ui.pushButton_8.clicked.connect(lambda: self.smile_send('5'))
        self.ui.pushButton_9.clicked.connect(lambda: self.smile_send('6'))
        self.ui.pushButton_13.clicked.connect(lambda: self.smile_send('7'))
        self.ui.pushButton_17.clicked.connect(lambda: self.smile_send('8'))
        self.ui.pushButton_16.clicked.connect(lambda: self.smile_send('9'))
        self.ui.pushButton_14.clicked.connect(lambda: self.smile_send('10'))
        self.ui.pushButton_15.clicked.connect(lambda: self.smile_send('11'))
        self.ui.pushButton_18.clicked.connect(lambda: self.smile_send('12'))
        self.ui.pushButton_21.clicked.connect(lambda: self.smile_send('13'))
        self.ui.pushButton_22.clicked.connect(lambda: self.smile_send('14'))
        self.ui.pushButton_24.clicked.connect(lambda: self.smile_send('15'))


    # Перетаскивание безрамочного окна
    # ==================================================================
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except AttributeError:
            pass
    # ==================================================================


    # Отправить смайлик
    def smile_send(self, smile_number: str):
        btn_base = {'1': self.ui.pushButton_10,
                    '2': self.ui.pushButton_11,
                    '3': self.ui.pushButton_12,
                    '4': self.ui.pushButton_6,
                    '5': self.ui.pushButton_8,
                    '6': self.ui.pushButton_9,
                    '7': self.ui.pushButton_13,
                    '8': self.ui.pushButton_17,
                    '9': self.ui.pushButton_16,
                    '10': self.ui.pushButton_14,
                    '11': self.ui.pushButton_15,
                    '12': self.ui.pushButton_18,
                    '13': self.ui.pushButton_21,
                    '14': self.ui.pushButton_22,
                    '15': self.ui.pushButton_24}

        change_style = """
        border-radius: 35px;
        border: 2px solid white;
        """

        default_style = """
        border: none;
        """

        if self.smile_type == None:
            btn_base[smile_number].setStyleSheet(change_style)
            self.smile_type = smile_number

        elif self.smile_type != None and self.smile_type != smile_number:
            btn_base[self.smile_type].setStyleSheet(default_style)
            btn_base[smile_number].setStyleSheet(change_style)
            self.smile_type = smile_number

        elif self.smile_type != None and self.smile_type == smile_number:
            btn_base[smile_number].setStyleSheet(default_style)
            self.smile_type = None

        print(f'SELF.SMILE_TYPE: {self.smile_type}')


    # Открыть окно для настройки клиента
    def setting_panel(self):
        setting_win = SettingPanel(self, self.connect_monitor.mysignal)
        setting_win.show()


    # Обновление конфигов клиента
    def update_config(self):
        """
        Используется для обновления значений на лету, без необходимости
        перезапускать клиент (В случае если пользователь отредактировал настройки
        либо же запустил софт и необходимо проинициализировать значения)
        """
        # Если конфиг уже был создан
        if os.path.exists(os.path.join("data", "config.json")):
            with open(os.path.join("data", "config.json")) as file:
                data = json.load(file)
                self.nick = data['nick']
                self.ip = data['server_ip']
                self.port = int(data['server_port'])


    # Обработчик сигналов из потока
    def signal_handler(self, value: list):
        # Обновление параметров конфига
        if value[0] == "update_config":
            self.update_config()

        # Обновление симметричного ключа
        elif value[0] == "SERVER_OK":
            self.connect_status = True
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignHCenter)
            item.setText(f"SERVER: {value[1]}\n")
            self.ui.listWidget.addItem(item)
            print(value)


        # Обработка сообщений других пользователей
        # ['ENCRYPT_MESSAGE', self.nick, smile_num, message_text.encode()]
        elif value[0] == "ENCRYPT_MESSAGE":
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignRight)

            if value[2] != None:
                size = QtCore.QSize(45, 45)
                icon = QtGui.QIcon(os.path.join("icons", f"smile{value[2]}.png"))
                self.ui.listWidget.setIconSize(size)
                item.setIcon(icon)

            item.setText(f"{value[1]}:\n{value[-1]}")
            self.ui.listWidget.addItem(item)
            print(value)


    # Отправить сообщение на сервер
    def send_message(self):
        if self.connect_status:
            message_text = self.ui.lineEdit.text()
            smile_num = self.smile_type

            # Если поле с текстом не пустое шифруем сообщение и передаем на сервер
            if len(message_text) > 0:
                payload = ['ENCRYPT_MESSAGE', self.nick, smile_num, message_text.encode()]
                print(payload)
                self.connect_monitor.send_encrypt(payload)

                # Добавляем свое сообщение в ListWidget
                item = QtWidgets.QListWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                size = QtCore.QSize(45, 45)

                if smile_num != None:
                    icon = QtGui.QIcon(os.path.join("icons", f"smile{smile_num}.png"))
                    self.ui.listWidget.setIconSize(size)
                    item.setIcon(icon)
                item.setText(f"{self.nick} (ВЫ):\n{message_text}")
                self.ui.listWidget.addItem(item)

        else:
            message = "Проверьте соединение с сервером"
            QtWidgets.QMessageBox.about(self, "Оповещение", message)


    # Покдлючаемся к общему серверу
    def connect_to_server(self):
        self.update_config()    # Обновляем данные пользователя

        if self.nick != None:
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((self.ip, self.port))

                # Запускаем мониторинг входящих сообщений
                self.connect_monitor.server_socket = self.client
                self.connect_monitor.start()

                # Блокируем кнопки
                self.btn_locker(self.ui.pushButton_2, True)
                self.btn_locker(self.ui.pushButton_7, True)

            except Exception as err:
                message = "Ошибка соединения с сервером.\nПроверьте правильность ввода данных"
                QtWidgets.QMessageBox.about(self, "Оповещение", message)
        else:   # Если пользователь не заполнил данные
            message = "Для начала заполните данные во вкладке 'Настройки'"
            QtWidgets.QMessageBox.about(self, "Оповещение", message)


    # Блокировщик кнопок
    def btn_locker(self, btn: object, lock_status: bool) -> None:
        default_style = """
        QPushButton{
            color: white;
            border-radius: 7px;
            background-color: #595F76;
        }
        QPushButton:hover{
            background-color: #50566E;
        }      
        QPushButton:pressed{
            background-color: #434965;
        }
        """

        lock_style = """
        color: #9EA2AB;
        border-radius: 7px;
        background-color: #2C313C;
        """

        if lock_style:
            btn.setDisabled(True)
            btn.setStyleSheet(lock_style)
        else:
            btn.setDisabled(False)
            btn.setStyleSheet(default_style)


    # Обработчик события на выход из клиента
    def closeEvent(self, value: QtGui.QCloseEvent) -> None:
        try:
            payload = ['EXIT', f'{self.nick}', 'вышел из чата!'.encode()]
            self.connect_monitor.send_encrypt(payload); self.hide()
            time.sleep(3); self.client.close()
            self.close()
        except Exception as err:
            print(err)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = Client()
    myapp.show()
    sys.exit(app.exec_())