#Привет дорогой узер!
#Этот мессенджер на python производится с использованием pyqt5 python и имеет графический интерфейс. Данный проект реализован полностью на python с использованием сокетов, и следующих модулей: pyqt5, socket, rsa, и многие другие
#Данный мессенджер на питон защищен от тайминг и MITM атак.
#Данный проект полностью реализован на языке Python с использованием асимметричного RSA шифрования и построен на модуле Socket с генерацией файлов аутентификации. Каждый узел подключается ТОЛЬКО по файлу ключу другого узла, который заранее генерируется и передается между участниками чата. Весь процесс переписки не сохраняется на компьютере и будет очищен после завершения программы, так как хранится только в оперативной памяти.
#Сервер же используется только для передачи данных между участниками, при этом расшифровать ваши сообщения на стороне сервера невозможно. И да, модель сервера и клиента полностью построена на TCP.

import time
import socket
import base64
import threading


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.all_client = []

        # Запускаем прослушивание соединений
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)
        threading.Thread(target=self.connect_handler).start()
        print('Сервер запущен!')


    # Обрабатываем входящие соединения
    def connect_handler(self):
        while True:
            client, address = self.server.accept()
            if client not in self.all_client:
                self.all_client.append(client)
                threading.Thread(target=self.message_handler, args=(client,)).start()
                client.send('Успешное подключение к чату!'.encode('utf-8'))
            time.sleep(1)


    # Обрабатываем отправленный текст
    def message_handler(self, client_socket):
        while True:
            message = client_socket.recv(1024)
            print(message)

            # Удаляем текущий сокет
            if message == b'exit':
                self.all_client.remove(client_socket)
                break

            for client in self.all_client:
                if client != client_socket:
                    client.send(message)
            time.sleep(1)



myserver = Server('127.0.0.1', 5555)
