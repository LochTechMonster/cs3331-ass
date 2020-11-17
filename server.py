#coding: utf-8
from socket import *
from sys import argv
from os import path, remove
import re

currUsers = []
threads = []
files = []

#FIXME: Remove line numbers from responses
#TODO: Make ' and " consistent
'''
Initial Connection: 
When connecting, client prompts for a username
 - Receive username
 - Check credentials.txt for a match
If name exists send confirmation to client
 - Client prompts for password
 - Receive password
If password match then confirm to client
If doesn't then send error to client

If things don't match then:
 - Client prompts for username
 - If doesn't exist, prompt for new password
Creates new line in credentials.txt
 - Send confirmation to client
 - Client sends message to user
Make sure credentials.txt has write permissions

Multi-threading version:
Keep track of logged in accounts
Make sure connecting users aren't using the same account


Forum Ops:
Commands are sent as uppercase
Arguments are separated by one space and will be one word long
  Except Messages which can contain whitespace
If anything doesn't follow usage specs then send error to user
  User prompted to pick a command again
Client sends username on every command

11 Different commands

CRT: Create thread
USAGE: 'CRT threadtitle'
Thread titles are one word long
Client sends command, title of thread and username
each thread is a text file with the name 'threadtitle' (no .txt)
First line is the username of who created the thread
The rest of the lines are messages, added in chronological order (just append to the end)
Server checks if a thread exists with the same title (sends error)
If doesn't exist, create file
Send confirmation to client

MSG: Post Message
USAGE: 'MSG threadtitle message'
The message can contain spaces
If a thread with the title doesn't exist, send error
Append message and username to thread file
'messagenumber username: message'
Messages start at 1
Send confirmation to client

DLT: Delete message
USAGE: 'DLT threadtitle messagenumber'
Message can only be deleted by the user who posted the message
Check:
  Thread exists
  Message number exists
  If user sent message
Delete line in thread
  Remove line in the file
  move all other messages up by one line
  update message numbers appropriately

EDT: Edit message
USAGE: 'EDT threadtitle messagenumber message'
Message can only be edited by the user who posted that message
Message is the updated message
Check:
  Thread exists
  Message number exists
  If user sent message
Replace original message with the replacement
  Message number and username remain unchanged

LST: List threads
USAGE: 'LST'
No arguments
Lists all thread titles
Client prints the list in the terminal
  one thread per line
If no threads, then give that message to user

RDT: Read thread
USAGE: 'RDT threadtitle'
Sends the file minus the first line to the client
Client displays all contents and info of uploaded files
If thread doesn't exist give error

UPD: Upload file
USAGE: 'UPD threadtitle filename'
Assume file is binary
Client sends command and thread
After check that thread exists
Then sends filename and username
Then sends file
Stores file as 'threadtitle-filename'
  keep current extension in name
Assume filename is unique
Append to thread file 'username uploaded filename'
Those messages are sent with RDT

DWN: Download file
USAGE: 'DWN threadtitle filename'
Client sends command, title, filename
Check if thread exists
Check if file is in thread
If match, then send file
Client saves as 'filename' no threadtitle
Can assume client doesn't have file
Once transfer is complete, send confirmation
File is not deleted on server end

RMV: Remove thread
USAGE: 'RMV threadtitle'
Check thread exists
Check user created thread
Thread is deleted, all files connected are deleted
Send confirmation

XIT: Exit
USAGE: 'XIT'
Closes TCP connection
Gives goodbye message to user
Update logged in users

SHT: Shutdown
USAGE: 'SHT admin_password'
Checks admin password
Sends a shutdown message to all clients
Closes all TCP messages
Deletes all file created by the server
  All threads
  All uploaded files
  credentials file
All sockets closed
Exits program

'''

def sendError(msg, addr):
    print('ERROR: ' + msg)
    sendToSocket('E' + msg, addr)
    #FIXME: send different messages for all errors to user and to server

def sendMessage(msg, addr):
    sendToSocket('M' + msg, addr)

def sendInputUser(msg, addr):
    sendToSocket('I' + msg, addr)

def sendInputRegisterName(msg, addr):
    sendToSocket('N' + msg, addr)

def sendInputComm(addr):
    sendToSocket('C' + 'Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT, SHT:', addr)

def sendInputLogin(msg, addr):
    sendToSocket('L' + msg, addr)

def sendInputRegister(msg, addr):
    sendToSocket('R' + msg, addr)

def sendUpload(msg, addr):
    sendToSocket('F' + msg, addr)

def sendDownload(msg, addr):
    sendToSocket('D' + msg, addr)

def sendName(msg, addr):
    sendToSocket('U' + msg, addr)

def sendLogout(addr):
    sendMessage('Goodbye', addr)
    sendToSocket('L', addr)

def sendToSocket(msg, addr):
    # TODO: Change separator
    connectionSocket.sendto((msg.rstrip() + '-*-').encode('utf-8'), addr)

def receiveResponse():
    return connectionSocket.recv(1024).decode('utf-8').strip()

def thread_exists(threadtitle):
    return next((x for x in threads if x['title'] == threadtitle), False)

def user_login(addr):
    '''
    Initial Connection: 
    When connecting, client prompts for a username
    - Receive username
    - Check credentials.txt for a match
    If name exists send confirmation to client
    - Client prompts for password
    - Receive password
    If password match then confirm to client
    If doesn't then send error to client

    If things don't match then:
    - Client prompts for username
    - If doesn't exist, prompt for new password
    Creates new line in credentials.txt
    - Send confirmation to client
    - Client sends message to user
    Make sure credentials.txt has write permissions
    '''
    print('Client Connected')
    sendInput('Enter your username: ', addr)
    username = receiveResponse()
    file = open('credentials.txt', 'r')

    u_found = False
    login = False
    for line in file.readlines():
        words = line.split()
        # FIXME:
        #print(words[0])
        if words[0] == username:
            sendInput('200Enter your password: ', addr)
            passwd = receiveResponse()
            if words[1] == passwd:
                login = True
                currUsers.append(username)
                print(username + ' successful login', addr)
                sendMessage('206Successful login', addr)
                sendName(username, addr)
            else:
                sendError('Incorrect password', addr)
                
            break
    
    file.close()

    if not login:
        if not u_found:
            sendError('216Username not found', addr)
        # 
        user_register(addr)
        
    
    # u_exists == true
    # check password

def user_register(addr):
    # TODO: Check the recursion

    # Get username
    sendInput('227Enter your username: ', addr)
    username = receiveResponse()
    file = open('credentials.txt', 'r')

    u_exists = False
    for line in file.readlines():
        words = line.split()
        if words[0] == username:
            u_exists = True
            sendInput('236Enter your password: ', addr)
            passwd = receiveResponse()
            if words[1] == passwd:
                currUsers.append(username)
                sendMessage('240Successful login', addr)
                print(username + ' successful login')
                
            break
    file.close()
    # If user doesn't exist
    # Prompt new password
    if not u_exists:
        file = open('credentials.txt', 'a')
        sendMessage('249Username not found', addr)
        sendInput('250Enter new password: ', addr)
        passwd = receiveResponse()
        file.write('\n' + username + ' ' + passwd)
        currUsers.append(username)
        print('256New user ' + username + ' registered')
        sendMessage('255User Registered', addr)
        file.close()
    else:
        user_register(addr)
    

    sendName(username, addr)
    # Confirmation new user

def create_thread(threadtitle, user, addr):
    '''
    CRT: Create thread
    USAGE: 'CRT threadtitle'
    Thread titles are one word long
    Client sends command, title of thread and username
    each thread is a text file with the name 'threadtitle' (no .txt)
    First line is the username of who created the thread
    The rest of the lines are messages, added in chronological order (just append to the end)
    Server checks if a thread exists with the same title (sends error)
    If doesn't exist, create file
    Send confirmation to client
    '''
    print(user + ' issued CRT command')

    if thread_exists(threadtitle):
        sendError('277Thread already exists', addr)
    else:
        # thread doesn't exist yet
        file = open(threadtitle, 'w')
        file.write(user)
        file.close()
        global threads
        threads.append({'title': threadtitle,'files':[]})
        threads = sorted(threads, key= lambda k: k['title'])
        sendMessage('283Thread ' + threadtitle + ' created', addr)
        print('Thread ' + threadtitle + ' created')

def send_message(threadtitle, message, user, addr):
    '''
    MSG: Post Message
    USAGE: 'MSG threadtitle message'
    The message can contain spaces
    If a thread with the title doesn't exist, send error
    Append message and username to thread file
    'messagenumber username: message'
    Messages start at 1
    Send confirmation to client
    '''
    print(user + ' issued MSG command')
    if not thread_exists(threadtitle):
        sendError("298Thread doesn't exist", addr)
        return
    msg = ' '.join(message)
    
    lastNum = get_lastnumber(threadtitle)

    file = open(threadtitle, "a")
    file.write('\n' + str(lastNum + 1) + ' ' + user + ': ' + msg)
    sendMessage('313Message sent to ' + threadtitle + ' thread', addr)
    print(user + ' posted to ' + threadtitle + ' thread')

    file.close()

def is_message(line):
    result = re.search("^[0-9]+ .+: .+", line)
    return (result is not None)

def get_msgnumber(line):
    # Prob try to catch error here
    return int(line.split()[0])

def get_lastnumber(threadtitle):
    file = open(threadtitle, "r")
    lines = file.read().splitlines()
    #print(lines)
    #print(len(lines))
    lastMessage = None
    for line in reversed(lines[1:]):
        if is_message(line):
            lastMessage = line
            break
    file.close()

    lastNum = 0
    if lastMessage is not None:
        lastNum = get_msgnumber(lastMessage)
    
    return lastNum

def delete_message(threadtitle, msgNumber, user, addr):
    '''
    DLT: Delete message
    USAGE: 'DLT threadtitle messagenumber'
    Message can only be deleted by the user who posted the message
    Check:
        Thread exists
        Message number exists
        If user sent message
    Delete line in thread
        Remove line in the file
        move all other messages up by one line
        update message numbers appropriately
    '''
    print(user + ' issued DLT command')
    if not thread_exists(threadtitle):
        sendError("358Thread doesn't exist", addr)
        return
    
    msgNum = int(msgNumber)
    if msgNum < 1 or msgNum > get_lastnumber(threadtitle):
        sendError("Message number doesn't exist", addr)
        return
    
    found = False
    with open(threadtitle, "r+") as f:
        thread = f.readlines()
        # Clears file then rewrites it
        f.seek(0)
        f.truncate()
        f.write(thread[0].strip())
        for line in thread[1:]:
            #print(line)
            if is_message(line):
                if found:
                    # After the message
                    msg = ' '.join(line.split()[1:])
                    f.write('\n' + str(get_msgnumber(line) - 1) + ' ' + msg)
                    continue
                if get_msgnumber(line) == msgNum:
                    if (user + ':') == line.split()[1]:
                        found = True
                    else:
                        sendError("Message cannot be deleted", addr)
                        f.write('\n' + line.rstrip())
                else:
                    # Before the message
                    f.write('\n' + line.strip())
            else:
                f.write('\n' + line.strip())

    if found:
        sendMessage('Line deleted', addr)

def edit_message(threadtitle, msgNumber, message, user, addr):
    '''
    EDT: Edit message
    USAGE: 'EDT threadtitle messagenumber message'
    Message can only be edited by the user who posted that message
    Message is the updated message
    Check:
        Thread exists
        Message number exists
        If user sent message
    Replace original message with the replacement
        Message number and username remain unchanged
    '''
    print(user + ' issued EDT command')
    if not thread_exists(threadtitle):
        sendError("358Thread doesn't exist", addr)
        return
    
    msgNum = int(msgNumber)
    if msgNum < 1 or msgNum > get_lastnumber(threadtitle):
        sendError("Message number doesn't exist", addr)
        return
    
    found = False
    with open(threadtitle, "r+") as f:
        thread = f.readlines()
        # Clears file then rewrites it
        f.seek(0)
        f.truncate()
        f.write(thread[0].strip())
        for line in thread[1:]:
            #print(line)
            if is_message(line):
                if not found and get_msgnumber(line) == msgNum:
                    if (user + ':') == line.split()[1]:
                        found = True
                        msg = ' '.join(message)
                        prefix = ' '.join(line.split()[0:2])
                        f.write('\n' + prefix + ' ' + msg)
                    else:
                        sendError("Message cannot be edited", addr)
                        f.write('\n' + line.rstrip())
                else:
                    f.write('\n' + line.strip())
            else:
                f.write('\n' + line.strip())

    if found:
        sendMessage('Message edited', addr)
        print('Message edited')

def list_threads(user, addr):
    '''
    LST: List threads
    USAGE: 'LST'
    No arguments
    Lists all thread titles
    Client prints the list in the terminal
        one thread per line
    If no threads, then give that message to user
    '''
    print(user + ' issued LST command')
    if threads == []:
        sendMessage('No threads to list', addr)
    else:
        for thread in threads:
            sendMessage(thread['title'], addr)

def read_thread(threadtitle, user, addr):
    '''
    RDT: Read thread
    USAGE: 'RDT threadtitle'
    Sends the file minus the first line to the client
    Client displays all contents and info of uploaded files
    If thread doesn't exist give error
    '''
    print(user + ' issued RDT command')
    if not thread_exists(threadtitle):
        sendError("Thread doesn't exist", addr)
        return
    
    with open(threadtitle, 'r') as f:
        f.readline()
        for line in f:
            sendMessage(line, addr)

def upload_file(threadtitle, filename, user, addr):
    '''
    UPD: Upload file
    USAGE: 'UPD threadtitle filename'
    Assume file is binary
    Client sends command and thread
    After check that thread exists
    Then sends filename and username
    Then sends file
    Stores file as 'threadtitle-filename'
        keep current extension in name
    Assume filename is unique
    Append to thread file 'username uploaded filename'
    Those messages are sent with RDT
    '''
    print(user + ' issued UPD command')
    thread = thread_exists(threadtitle)
    if not thread:
        sendError("Thread doesn't exist", addr)
        return
    sendUpload(filename, addr)
    filesize = int(receiveResponse())
    print(filesize)
    file = open(threadtitle + '-' + filename, 'wb')
    while filesize > 0:
        print(str(filesize) + " Receiving...")
        data = connectionSocket.recv(1024)
        file.write(data)
        filesize -= len(data)
    print(filesize)
    print('File ' + filename + ' received')
    file.close()

    file = open(threadtitle, 'a')
    file.write('\n' + user + ' uploaded ' + filename)
    file.close()

    thread['files'].append(filename)
    sendMessage('File sent', addr)

def download_file(threadtitle, filename, user, addr):
    '''
    DWN: Download file
    USAGE: 'DWN threadtitle filename'
    Client sends command, title, filename
    Check if thread exists
    Check if file is in thread
    If match, then send file
    Client saves as 'filename' no threadtitle
    Can assume client doesn't have file
    Once transfer is complete, send confirmation
    File is not deleted on server end
    '''
    print(user + ' issued DWN command')

    thread = thread_exists(threadtitle)
    if not thread:
        sendError("Thread doesn't exist", addr)
        return
    if filename not in thread['files']:
        sendError("File doesn't exist in thread", addr)
        return
    
    combinedName = threadtitle + '-' + filename
    filesize = str(path.getsize(combinedName))
    sendDownload(filename + ' ' + filesize, addr)

    file = open(combinedName, "rb")
    data = file.read(1024)
    while data:
        print("Sending...")
        connectionSocket.send(data)
        data = file.read(1024)
    file.close()
    print("File sent")
    sendMessage("File downloaded", addr)
    
def remove_thread(threadtitle, user, addr):
    '''
    RMV: Remove thread
    USAGE: 'RMV threadtitle'
    Check thread exists
    Check user created thread
    Thread is deleted, all files connected are deleted
    Send confirmation
    '''
    thread = thread_exists(threadtitle)
    if not thread:
        sendError("Thread doesn't exist", addr)
        return
    
    isOwner = False
    with open(threadtitle, "r") as f:
        if f.readline().rstrip == user:
            isOwner = True

    if isOwner:
        if path.exists(threadtitle):
            remove(threadtitle)
        for filename in thread['files']:
            if path.exists(threadtitle + '-' + filename):
                remove(threadtitle + '-' + filename)
    else:
        sendError("User is not the owner", addr)


def selectCommand(resp, addr):
    sendInputComm(addr)
    resp = receiveResponse()
    words = resp.split()
    username = words[0]
    if username not in currUsers:
        sendError('User not currently logged in', addr)
        return True
    cmd = words[1]
    # Check words, make sure they aren't NULL
    if cmd == 'CRT':
        create_thread(words[2], username, addr)
    elif cmd == 'MSG':
        send_message(words[2], words[3:], username, addr)
    elif cmd == 'DLT':
        delete_message(words[2], words[3], username, addr)
    elif cmd == 'EDT':
        edit_message(words[2], words[3], words[4:], username, addr)
    elif cmd == 'LST':
        list_threads(username, addr)
    elif cmd == 'RDT':
        read_thread(words[2], username, addr)
    elif cmd == 'UPD':
        upload_file(words[2], words[3], username, addr)
    elif cmd == 'DWN':
        download_file(words[2], words[3], username, addr)
    elif cmd == 'RMV':
        remove_thread(words[2], username, addr)
    elif cmd == 'XIT':
        sendMessage('Logging out', addr)
        sendLogout(addr)
        print(username + ' logged out')
        currUsers.remove(username)
        return False
    elif cmd == 'SHT':
        shutdown()
    return True

def userExit(name, addr):
    sendMessage('Logging out', addr)
    sendLogout(addr)
    print(name + ' logged out')
    currUsers.remove(name)
    connectedClients.remove(addr)

def shutdown(password, addr):
    #FIXME: Work with multiple clients
    if password != admin_passwd:
        sendError('Incorrect admin password', addr)
        return

    for i in connectedClients:
        sendMessage('Server shutting down', i)
        sendLogout(i)
    print('Shutting down')
    # TODO: close all current connections
    connectionSocket.close()
    serverSocket.close()
    for thread in threads:
        if path.exists(thread['title']):
            remove(thread['title'])
        for f in thread['files']:
            if path.exists(thread['title'] + '-' + f):
                remove(thread['title'] + '-' + f)
    exit()

import threading
t_lock = threading.Condition()
connectedClients = []

#FIXME: 
def recv_handler():
    while 1:
        message, addr = serverSocket.recvfrom(1024)
        with t_lock:
            if addr not in connectedClients:
                # New user
                sendInputUser('Enter your username:')
            comm = message[0]
            if comm == 'C':
                typeCommand(message[1:], addr)
            elif comm == 'U':
                typeUsername(message[1:], addr)
            elif comm == 'N':
                typeRegisterName(message[1:], addr)
            elif comm == 'L':
                typeLogin(message[1:], addr)
            elif comm == 'R':
                typeRegister(message[1:], addr)

# Input types:
#
# Command: Response to the send command
#   Cuser comm arg1 arg2....
# Username: Username to check if it exists
#   Uuser
# Register Name: If username doesn't exist, prompt to register
#   Nname
# Login: Login attempt with user and password
#   Luser password
# Register: Register a new user, do if username doesn't exist
#   Ruser password

def typeCommand(message, addr):
    words = message.split()
    username = words[0]
    if username not in currUsers:
        sendError('User not currently logged in', addr)
        return True
    cmd = words[1]
    args = len(words)

    if cmd == 'CRT':
        if args == 3:
            create_thread(words[2], username, addr)
    elif cmd == 'MSG':
        if args > 4:
            send_message(words[2], words[3:], username, addr)
    elif cmd == 'DLT':
        if args == 4:
            delete_message(words[2], words[3], username, addr)
    elif cmd == 'EDT':
        if args > 5:
            edit_message(words[2], words[3], words[4:], username, addr)
    elif cmd == 'LST':
        if args == 2:
            list_threads(username, addr)
    elif cmd == 'RDT':
        if args == 3:
            read_thread(words[2], username, addr)
    elif cmd == 'UPD':
        if args == 4:
            upload_file(words[2], words[3], username, addr)
    elif cmd == 'DWN':
        if args == 4:
            download_file(words[2], words[3], username, addr)
    elif cmd == 'RMV':
        if args == 3:
            remove_thread(words[2], username, addr)
    elif cmd == 'XIT':
        if args == 2:
            userExit(username, addr)
            return
    elif cmd == 'SHT':
        if args == 3:
            shutdown(words[2], addr)
    
    sendInputComm(addr)

def typeUsername(message, addr):
    '''
    Check username exists
    If it does, send login
    If it doesn't, move to register if user already connected
    If user hasn't connected before, add to connected, then try username again
    '''
    result = findUsername(message)
    if result:
        sendName(result.split()[0])
        sendInputLogin('Enter password:', addr)
    else:
        sendError('Username not found', addr)
        sendInputRegisterName('Enter username:', addr)

def findUsername(user):
    with open('credentials.txt', 'r') as f:
        for line in f.readlines():
            words = line.split()
            if words[0] == user:
                return line
    
    return None

def typeRegisterName(message, addr):
    result = findUsername(message)
    if result:
        sendName(result.split()[0])
        sendInputLogin('Enter password:', addr)
    else:
        sendMessage('Username not found, registering new user', addr)
        sendInputRegister('Input new password:')


def typeLogin(message, addr):
    '''
    Checks username and password
    If correct, add to connected users
    If incorrect, go to username again
    '''
    inUser = message.split()[0]
    inPass = message.split()[1]

    result = findUsername(inUser)
    storedPass = result.split()[1]
    if storedPass == inPass:
        currUsers.append(inUser)
        sendMessage('Logged in', addr)
        print(inUser + ' successfully logged in')
        sendInputComm(addr)
    else:
        sendError('Incorrect password', addr)
        print(inUser + ' incorrect password')
        sendInputLogin('Enter username:', addr)


def typeRegister(message, addr):
    '''
    Adds username and password to credentials
    Then adds to logged in
    '''
    

    with open('credentials.txt', 'a') as f:
        f.write(message + '\n')
        print('New user ' + message.split()[0] + ' registered')
        currUsers.append(message.split()[0])
        sendMessage('Successful login', addr)

    sendInputComm(addr)
        


#try:
if __name__ == "__main__":
    #using the socket module

    #Define connection (socket) parameters
    #Address + Port no
    #Server would be running on the same host as Client
    # change this port number if required
    server_port = 12000
    admin_passwd = None 

    if len(argv) == 3:
        server_port = int(argv[1])
        admin_passwd = argv[2]
    else:
        print("Correct usage: python3 server.py server_port admin_passwd")
        exit()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', server_port))
    serverSocket.listen(1)
    print("The server is ready to receive")

    while True:
        connectionSocket, addr = serverSocket.accept()
        user_login()
        while selectCommand():
            pass

        connectionSocket.close()
# except KeyboardInterrupt:
#     pass
# finally:
#     shutdown()