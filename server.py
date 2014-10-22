#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pidpawel, projekt na ćwiczenia z przedmiotu Sieci komputerowe 2014
import socket
import threading
import random

bind_host = "127.0.0.1"
bind_port = 1632

GAME_SIZE = 3

class Game(threading.Thread):
    def __init__(self, player1, player2):
        super(Game, self).__init__()

        self.player1 = player1
        self.player2 = player2

        self.board = {}
        for x in range(0, GAME_SIZE):
            self.board[x] = {}
            for y in range(0, GAME_SIZE):
                self.board[x][y] = '-'

    def sendBoard(self, target):
        b = []
        for y in range(0, GAME_SIZE):
            for x in range(0, GAME_SIZE):
                b.append(self.board[x][y])
        self.send(target, "YOUR MOVE:%s\n" % ''.join(b))

    def disconnect(self):
        self.player1.close()
        self.player2.close()

    def send(self, sock, s):
        print("Sending : %s" % s.strip())
        sock.sendall(s.encode('UTF-8'))

    def readline(self, sock):
        r = []
        l = ''
        while l != '\n':
            l = sock.recv(1).decode('UTF-8')
            if len(l)>0:
                r.append(l)
            else:
                if sock == self.player1:
                    self.send(self.player2, "ERROR:Other side has disconnected!\n")
                elif sock == self.player2:
                    self.send(self.player1, "ERROR:Other side has disconnected!\n")
                self.disconnect()
                return None

        s = ''.join(r[:-1])
        print("Received: %s" % s)
        return s

    def judge(self):
        l = self.board[0][0]

        if l is not '-':
            count = 0
            for a in range(1, GAME_SIZE):
                c = self.board[a][a]
                if c != l:
                    break
                l = c
                count += 1
            if count == (GAME_SIZE-1):
                return self.board[0][0]

        l = self.board[GAME_SIZE-1][0]

        if l is not '-':
            count = 0
            for a in range(1, GAME_SIZE):
                c = self.board[GAME_SIZE-1-a][a]
                if c != l:
                    break
                l = c
                count += 1
            if count == (GAME_SIZE-1):
                return self.board[GAME_SIZE-1][0]

        for col in range(0, GAME_SIZE):
            l = self.board[col][0]

            count = 1
            for y in range(1, GAME_SIZE):
                c = self.board[col][y]
                if c!=l:
                    break
                l = c
                count += 1
            if count == GAME_SIZE:
                return self.board[col][0]

        for row in range(0, GAME_SIZE):
            l = self.board[0][row]

            count = 1
            for x in range(1, GAME_SIZE):
                c = self.board[x][row]
                if c!=l:
                    break
                l = c
                count += 1
            if count == GAME_SIZE:
                return self.board[0][row]

        count = 0
        for x in range(0, GAME_SIZE):
            for y in range(0, GAME_SIZE):
                if self.board[x][y] in ('O', 'X'):
                    count += 1
        if count == GAME_SIZE*GAME_SIZE:
            return 'R'

        return None

    def run(self):
        self.send(self.player1, "START:O\n")
        self.send(self.player2, "START:X\n")

        current_player = self.player1

        while True:
            self.sendBoard(current_player)

            client = self.readline(current_player)
            if client is not None:
                parts = client.split(':', 1)
                if parts[0] == "SELECT":
                    coords_x, coords_y = parts[1].split('x', 1)
                    coords_x = int(coords_x)
                    coords_y = int(coords_y)

                    self.board[coords_x][coords_y] = 'O' if current_player == self.player1 else 'X'
                else:
                    self.send(self.player1, "ERROR:Wykryto błędny pakiet!\n")
                    self.send(self.player2, "ERROR:Wykryto błędny pakiet!\n")
                    self.disconnect()
                    break

                result = self.judge()

                if result == 'O':  # O wins
                    self.send(self.player1, "WINNER:Congratulations, you won!\n")
                    self.send(self.player2, "WINNER:You lost!\n")
                elif result == 'X':  # X wins
                    self.send(self.player2, "WINNER:Congratulations, you won!\n")
                    self.send(self.player1, "WINNER:You lost!\n")
                elif result == 'R':  # Remis
                    self.send(self.player2, "WINNER:Nobody wins!\n")
                    self.send(self.player1, "WINNER:Nobody wins!\n")
                else:  # Not finished yet
                    pass

                if current_player == self.player1:
                    current_player = self.player2
                else:
                    current_player = self.player1
            else:
                self.disconnect()
                break

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind_host, int(bind_port)))
    s.listen(2)

    games = []

    while True:
        conn1, addr1 = s.accept()
        conn2, addr2 = s.accept()

        game = Game(conn1, conn2)
        game.start()
