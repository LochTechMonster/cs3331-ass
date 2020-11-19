#coding: utf-8
from os import path
import select
from socket import *
from sys import argv
import threading

user = ''

COLOUR_RED = '\u001b[31m'
COLOUR_RESET = '\u001b[0m'

def recvError(msg):
    print(COLOUR_RED + msg + COLOUR_RESET)

def recvMessage(msg):
    print(msg)

def recvInputUser(msg):
    resp = None
    while not resp:
        resp = input(msg + ' ')
    sendUsername(resp)

def recvInputRegisterName(msg):
    resp = None
    while not resp:
        resp = input(msg + ' ')
    sendRegisterName(resp)

def recvInputComm(msg):
    resp = None
    while not resp:
        resp = input(msg + ' ')
    sendCommand(resp)

def recvInputLogin(msg):
    resp = None
    while not resp:
        resp = input(msg + ' ')
    sendLogin(resp)

def recvInputRegister(msg):
    resp = None
    while not resp:
        resp = input(msg + ' ')
    sendRegister(resp)

def recvUpload(msg):
    filename = msg.split()[0]
    fileid = int(msg.split()[1])
    filesize = str(path.getsize(filename))
    sendFile(str(fileid) + ' ' + filesize)
    file = open(filename, "rb")
    data = file.read(1024)
    while data:
        soc.send(data)
        data = file.read(1024)
    file.close()

def recvDownload(string):
    filename = string.split()[0]
    filesize = int(string.split()[1])
    file = open(filename, 'wb')

    while filesize > 0:
        print(str(filesize) + " Receiving...")
        data = soc.recv(1024)
        file.write(data)
        filesize -= len(data)
    file.close()

def recvFromServer():
    response = soc.recv(1024).decode('utf-8')
    commands = response.split('\u23F9')
    for cmd in commands:
        run_command(cmd)

def run_command(cmd):
    if cmd == '':
        # Last command
        return
    command = cmd[0]
    if command == 'E':
        recvError(cmd[1:])
    elif command == 'M':
        recvMessage(cmd[1:])
    elif command == 'I':
        # A failed attempt at getting threading to work
        newthread = threading.Thread(target=recvInputUser(cmd[1:]))
        newthread.start()
    elif command == 'N':
        newthread = threading.Thread(target=recvInputRegisterName(cmd[1:]))
        newthread.start()
    elif command == 'C':
        newthread = threading.Thread(target=recvInputComm(cmd[1:]))
        newthread.start()
    elif command == 'L':
        newthread = threading.Thread(target=recvInputLogin(cmd[1:]))
        newthread.start()
    elif command == 'R':
        newthread = threading.Thread(target=recvInputRegister(cmd[1:]))
        newthread.start()
    elif command == 'F':
        recvUpload(cmd[1:])
    elif command == 'D':
        recvDownload(cmd[1:])
    elif command == 'U':
        global user
        user = cmd[1:]
    elif command == 'Q':
        # Logout
        logout()


def logout():
    soc.close()
    exit()

def sendToServer(msg):
    soc.send(msg.encode('utf-8'))

def sendCommand(resp):
    sendToServer('C' + user + ' ' + resp)

def sendUsername(resp):
    sendToServer('U' + resp)

def sendRegisterName(resp):
    sendToServer('N' + resp)

def sendLogin(resp):
    sendToServer('L' + user + ' ' + resp)

def sendRegister(resp):
    sendToServer('R' + user + ' ' + resp)

def sendFile(resp):
    sendToServer('F' + resp)

if __name__ == "__main__":
        serverName = 'localhost'
        serverPort = 12000

        if len(argv) == 3:
            serverName = argv[1]
            serverPort = int(argv[2])
        else:
            print('Correct usage: python3 client.py server_IP server_port')
            exit()

        soc = socket(AF_INET, SOCK_STREAM)
        soc.connect((serverName, serverPort))
        sendToServer('Hello')

        while True:
            recvFromServer()
