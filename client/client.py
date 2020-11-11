#coding: utf-8
from os import path
from socket import *
from sys import argv

user = ''

#FIXME: Remove response print
#TODO: Change all str variables
def typeError(str):
    print(str)

def typeMessage(str):
    print(str)

def typeInput(str):
    response = input(str + ' ')
    sendToServer(response)

def typeRequest(str):
    pass

def typeUpload(filename):
    filesize = str(path.getsize(filename))
    print(filesize)
    soc.send(filesize.encode('utf-8'))
    file = open(filename, "rb")
    data = file.read(1024)
    while data:
        print("Sending...")
        soc.send(data)
        data = file.read(1024)
    file.close()
    print("Done")
    

def typeDownload(string):
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
        elif command == 'U':
            typeUpload(cmd[1:])
        elif command == 'D':
            typeDownload(cmd[1:])
        elif command == 'N':
            global user
            user = cmd[1:]
        elif command == 'L':
            # Logout
            logout()
        DEBUG_i += 1

def logout():
    soc.close()
    exit()

def sendToServer(str):
    soc.send((user + ' ' + str).encode('utf-8'))


if __name__ == "__main__":
        serverName = 'localhost'
        serverPort = 12000

        if len(argv) == 3:
            serverName = argv[1]
            serverPort = int(argv[2])
        else:
            print('Correct usage: python3 client.py server_IP server_port')

        soc = socket(AF_INET, SOCK_STREAM)
        #This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM). 
        soc.connect((serverName, serverPort))
        #Before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the connect( ) method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

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
