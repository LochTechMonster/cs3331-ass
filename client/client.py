#coding: utf-8
from os import path
from socket import *
from sys import argv

user = ''

#FIXME: Remove response print
#TODO: Change all str variables
#TODO: Make errors red
def recvError(msg):
    print(msg)

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
    print(filesize)
    sendSize(str(fileid) + ' ' + filesize)
    #soc.send(filesize.encode('utf-8'))
    file = open(filename, "rb")
    # one byte for the File indicator and one for the fileid
    data = file.read(1022)
    while data:
        print("Sending...")
        soc.send(data)
        data = file.read(1022)
    file.close()
    print("File sent")

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
    #DEBUG: 
    #print('response: ' + response)
    commands = response.split('\u23F9')
    #DEBUG_i = 0
    for cmd in commands:
        if cmd == '':
            # Last command
            break
        #print(DEBUG_i)
        command = cmd[0]
        if command == 'E':
            recvError(cmd[1:])
        elif command == 'M':
            recvMessage(cmd[1:])
        elif command == 'I':
            recvInputUser(cmd[1:])
        elif command == 'N':
            recvInputRegisterName(cmd[1:])
        elif command == 'C':
            recvInputComm(cmd[1:])
        elif command == 'L':
            recvInputLogin(cmd[1:])
        elif command == 'R':
            recvInputRegister(cmd[1:])
        elif command == 'F':
            recvUpload(cmd[1:])
        elif command == 'D':
            recvDownload(cmd[1:])
        elif command == 'U':
            global user
            user = cmd[1:]
        elif command == 'L':
            # Logout
            logout()
        #DEBUG_i += 1

def logout():
    soc.close()
    exit()

# TODO: Fix specifying messages here
def sendToServer(msg):
    #DEBUG:
    #print(f'Sent: {msg}')
    soc.send(msg.encode('utf-8'))

#TODO: bring sendToServer back
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

def sendSize(resp):
    sendToServer('F' + resp)

def sendFile(data):
    soc.send(b'F'+data)


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

# try:
#     if __name__ == "__main__":
#         serverName = 'localhost'
#         serverPort = 12000

#         if len(argv) == 3:
#             serverName = argv[1]
#             serverPort = int(argv[2])
#         else:
#             print('Correct usage: python3 client.py server_IP server_port')

#         soc = socket(AF_INET, SOCK_STREAM)
#         #This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM). 
#         soc.connect((serverName, serverPort))
#         #Before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the connect( ) method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

#         while True:
#             recvFromServer()
# except KeyboardInterrupt:
#     pass
# finally:
#     logout()
