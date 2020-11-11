#coding: utf-8
from socket import *
from sys import argv
from typing import final

user = ''

#FIXME: Remove response print

def typeError(str):
    print(str)

def typeMessage(str):
    print(str)

def typeInput(str):
    response = input(str)
    sendToServer(response)

def typeUpload(str):
    file = open(str, "rb")
    data = file.read(1024)
    while data:
        print("Sending...")
        clientSocket.send(data)
        data = file.read(1024)
    clientSocket.send(b"DONE")

def typeDownload(str):
    pass

def recvFromServer():
    response = clientSocket.recv(1024).decode('utf-8')
    #print('response: ' + response)
    commands = response.split('-*-')
    DEBUG_i = 0
    for cmd in commands:
        if cmd == '':
            # Last command
            break
        #print(DEBUG_i)
        command = cmd[0]
        if command == 'E':
            typeError(cmd[1:])
        elif command == 'M':
            typeMessage(cmd[1:])
        elif command == 'I':
            typeInput(cmd[1:])
        elif command == 'R':
            typeUpload(cmd[1:])
        elif command == 'D':
            typeDownload(cmd[1:])
        elif command == 'U':
            global user
            user = cmd[1:]
        elif command == 'L':
            # Logout
            logout()
        DEBUG_i += 1

def logout():
    clientSocket.close()
    exit()

def sendToServer(str):
    clientSocket.send((user + ' ' + str).encode('utf-8'))

try:
    if __name__ == "__main__":
        serverName = 'localhost'
        serverPort = 12000

        if len(argv) == 3:
            serverName = argv[1]
            serverPort = int(argv[2])
        else:
            print('Correct usage: python3 client.py server_IP server_port')

        clientSocket = socket(AF_INET, SOCK_STREAM)
        #This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM). 
        clientSocket.connect((serverName, serverPort))
        #Before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the connect( ) method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

        while True:
            recvFromServer()
except KeyboardInterrupt:
    pass
finally:
    logout()
