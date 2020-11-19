#coding: utf-8
from os import path
import select
from socket import *
from sys import argv
import threading

user = ''

COLOUR_RED = '\u001b[31m'
COLOUR_RESET = '\u001b[0m'

#TODO: Make errors red

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
    #DEBUG
    #print(filesize)
    sendFile(str(fileid) + ' ' + filesize)
    #soc.send(filesize.encode('utf-8'))
    file = open(filename, "rb")
    # one byte for the File indicator and one for the fileid
    data = file.read(1024)
    while data:
        #DEBUG
        #print("Sending...")
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
    #DEBUG: 
    #print('response: ' + response)
    commands = response.split('\u23F9')
    #DEBUG_i = 0
    for cmd in commands:
        run_command(cmd)

def run_command(cmd):
    if cmd == '':
        # Last command
        return
    #print(DEBUG_i)
    command = cmd[0]
    if command == 'E':
        recvError(cmd[1:])
    elif command == 'M':
        recvMessage(cmd[1:])
    elif command == 'I':
        newthread = threading.Thread(target=recvInputUser(cmd[1:]))
        newthread.start()
        #recvInputUser(cmd[1:])
    elif command == 'N':
        newthread = threading.Thread(target=recvInputRegisterName(cmd[1:]))
        newthread.start()
        #recvInputRegisterName(cmd[1:])
    elif command == 'C':
        newthread = threading.Thread(target=recvInputComm(cmd[1:]))
        newthread.start()
        #recvInputComm(cmd[1:])
    elif command == 'L':
        newthread = threading.Thread(target=recvInputLogin(cmd[1:]))
        newthread.start()
        #recvInputLogin(cmd[1:])
    elif command == 'R':
        newthread = threading.Thread(target=recvInputRegister(cmd[1:]))
        newthread.start()
        #recvInputRegister(cmd[1:])
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

def sendFile(resp):
    sendToServer('F' + resp)


# def ping_server():
#     sendToServer('P')
#     ready = select.select([soc], [], [], 2)
#     if ready[0]:
#         response = soc.recv(1024).decode('utf-8')
#         commands = response.split('\u23F9')
        
#         # Check for logout
#         for cmd in commands:
#             if cmd == 'Q':
#                 logout()
        
#         # Running any commands
#         for cmd in commands:
#             run_command(cmd)
#     else:
#         #server shutdown
#         print('Server shutdown')
#         soc.close()
#         exit()



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
        #ping_thread = threading.Thread(target=ping_server)
        #ping_thread.start()

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
