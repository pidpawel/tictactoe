#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pidpawel, projekt na ćwiczenia z przedmiotu Sieci komputerowe 2014
from PySide import QtGui, QtCore, QtNetwork
from PySide.QtGui import QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel, QSplitter, QStatusBar, QMessageBox, QFont
import random
import sys

GAME_SIZE = 3

class TTClient(QtGui.QMainWindow):
    def __init__(self):
        super(TTClient, self).__init__()

        self.initUI()
        self.initNetworking()

        self.figure = None

    def initNetworking(self):
        self.tcpSocket = QtNetwork.QTcpSocket(self)
        self.destroyed.connect(self.disconnect)

    def reconnect(self):
        self.tcpSocket.abort()
        self.statusBar().showMessage("Connecting to %s:%d..." % (self.server_input.text(), int(self.port_input.text())))
        self.tcpSocket.connectToHost(self.server_input.text(), int(self.port_input.text()))
        self.tcpSocket.connected.connect(self.sayHello)
        self.tcpSocket.readyRead.connect(self.onMessage)
        self.tcpSocket.disconnected.connect(self.onDisconnect)

    def onMessage(self):
        while self.tcpSocket.bytesAvailable() > 0:
            line = str(self.tcpSocket.readLine()).strip()
            print("Received: %s" % line.strip())

            if ':' in line:
                parts = line.split(':', 1)
                #print(parts)

                if parts[0] == "START":
                    self.statusBar().showMessage("Peer connected, you're: %s" % parts[1])
                    self.disableKeypad(True)
                    self.cleanKeypad()
                    self.figure = parts[1]

                elif parts[0] == "ERROR":
                    alert = QMessageBox(QMessageBox.Critical, "Error!", "Error! %s" % parts[1])
                    self.tcpSocket.abort()
                    alert.exec_()
                elif parts[0] == "WINNER":
                    alert = QMessageBox(QMessageBox.Information, parts[1], parts[1])
                    self.tcpSocket.abort()
                    alert.exec_()
                elif parts[0] == "YOUR MOVE":
                    board = parts[1]

                    for x in range(0, GAME_SIZE):
                        for y in range(0, GAME_SIZE):
                            if board[y*GAME_SIZE+x] == 'O':
                                self.game_fields[x][y].setText("O")
                                self.game_fields[x][y].setDisabled(True)
                            elif board[y*GAME_SIZE+x] == 'X':
                                self.game_fields[x][y].setText("X")
                                self.game_fields[x][y].setDisabled(True)
                            else:
                                self.game_fields[x][y].setText(" ")
                                self.game_fields[x][y].setDisabled(False)

    def onDisconnect(self):
        self.disableKeypad(False)
        self.statusBar().showMessage("Disconnected!")

    def sayHello(self):
        self.disableKeypad(True)
        self.statusBar().showMessage("Connected, waiting for second player...")

    def onGameButtonClicked(self):
        button_x = button_y = 0

        for x in range(0, GAME_SIZE):
            for y in range(0, GAME_SIZE):
                if self.sender() == self.game_fields[x][y]:
                    button_x = x
                    button_y = y
                    break

        if self.tcpSocket.isOpen():
            s = "SELECT:%dx%d\n" % (button_x, button_y)
            print("Sending : %s" % s.strip())
            self.tcpSocket.write(s)
            self.tcpSocket.flush()

            self.game_fields[button_x][button_y].setText(self.figure)
            self.disableKeypad(True)

    def cleanKeypad(self, b=True):
        for x in range(0, GAME_SIZE):
            for y in range(0, GAME_SIZE):
                self.game_fields[x][y].setText(" ")


    def disableKeypad(self, b=True):
        for x in range(0, GAME_SIZE):
            for y in range(0, GAME_SIZE):
                self.game_fields[x][y].setDisabled(b)

    def initUI(self):
        self.setWindowTitle('TickTackToe 2000')

        self.resize(350, 350)
        self.center()

        self.main_layout = QVBoxLayout()

        self.form_layout = QGridLayout()
        self.main_layout.addLayout(self.form_layout)

        splitter = QSplitter(QtCore.Qt.Horizontal)
        self.main_layout.addWidget(splitter)

        self.game_layout = QGridLayout()
        self.main_layout.addLayout(self.game_layout)

        self.server_label = QLabel("Server: ")
        self.server_input = QLineEdit("127.0.0.1")
        self.form_layout.addWidget(self.server_label, 0, 0)
        self.form_layout.addWidget(self.server_input, 0, 1)

        self.port_label = QLabel("Port: ")
        self.port_input = QLineEdit("1632")
        self.form_layout.addWidget(self.port_label, 1, 0)
        self.form_layout.addWidget(self.port_input, 1, 1)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setMinimumHeight(60)
        self.connect_button.pressed.connect(self.reconnect)
        self.form_layout.addWidget(self.connect_button, 0, 2, 2, 1)

        self.game_fields = {}

        tile_font = QFont()
        tile_font.setPointSize(30)

        for x in range(0, GAME_SIZE):
            for y in range(0, GAME_SIZE):
                f = QPushButton(" ")
                f.setMinimumHeight(90)
                f.setDisabled(True)
                f.setFont(tile_font)
                f.clicked.connect(self.onGameButtonClicked)

                if x in self.game_fields:
                    self.game_fields[x][y] = f
                else:
                    self.game_fields[x] = { 0: f }

                self.game_layout.addWidget(f, y, x)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("")

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ui = TTClient()
    sys.exit(app.exec_())
