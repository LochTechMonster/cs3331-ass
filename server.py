#coding: utf-8
# Change socket import
from socket import *
from sys import argv
from os import path, remove
import re
import select
from queue import Queue


#TODO: Check user logged in

curr_users = []
threads = []
server_port = 12000
admin_passwd = None 
files = []

#FIXME: Remove line numbers from responses
#TODO: Make ' and ' consistent
#FIXME: SHT removes the credentials file
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

def sendError(msg, soc):
    #print('ERROR: ' + msg)
    sendToSocket('E' + msg, soc)
    #FIXME: send different messages for all errors to user and to server

def sendMessage(msg, soc):
    sendToSocket('M' + msg, soc)

def sendInputUser(msg, soc):
    sendToSocket('I' + msg, soc)

def sendInputRegisterName(msg, soc):
    sendToSocket('N' + msg, soc)

def sendInputComm(soc):
    sendToSocket('CEnter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT, SHT:', soc)

def sendInputLogin(msg, soc):
    sendToSocket('L' + msg, soc)

def sendInputRegister(msg, soc):
    sendToSocket('R' + msg, soc)

def sendUpload(msg, soc):
    sendToSocket('F' + msg, soc)

def sendDownload(msg, soc):
    sendToSocket('D' + msg, soc)

def sendName(msg, soc):
    sendToSocket('U' + msg, soc)

def sendLogout(soc):
    sendMessage('Goodbye', soc)
    sendToSocket('Q', soc)

def sendToSocket(msg, soc):
    message_queues[soc].put((msg.rstrip() + '\u23F9').encode('utf-8'))

def thread_exists(threadtitle):
    return next((x for x in threads if x['title'] == threadtitle), False)

def create_thread(threadtitle, user, soc):
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
        sendError(f'Thread {threadtitle} exists', soc)
        print(f'Thread {threadtitle} exists')
    else:
        # thread doesn't exist yet
        file = open(threadtitle, 'w')
        file.write(user)
        file.close()
        global threads
        threads.append({'title': threadtitle,'files':[]})
        threads = sorted(threads, key= lambda k: k['title'])
        sendMessage('Thread ' + threadtitle + ' created', soc)
        print('Thread ' + threadtitle + ' created')

def send_message(threadtitle, message, user, soc):
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
        sendError('Thread does not exist', soc)
        return
    msg = ' '.join(message)
    
    lastNum = get_lastnumber(threadtitle)

    file = open(threadtitle, 'a')
    file.write('\n' + str(lastNum + 1) + ' ' + user + ': ' + msg)
    sendMessage('Message sent to ' + threadtitle + ' thread', soc)
    print(user + ' posted to ' + threadtitle + ' thread')

    file.close()

def is_message(line):
    result = re.search('^[0-9]+ .+: .+', line)
    return (result is not None)

def get_msgnumber(line):
    # Prob try to catch error here
    return int(line.split()[0])

def get_lastnumber(threadtitle):
    file = open(threadtitle, 'r')
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

def delete_message(threadtitle, msgNumber, user, soc):
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
        sendError('Thread does not exist', soc)
        return
    
    msgNum = int(msgNumber)
    if msgNum < 1 or msgNum > get_lastnumber(threadtitle):
        sendError('Message number does not exist', soc)
        return
    
    found = False
    with open(threadtitle, 'r+') as f:
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
                        sendError('Message cannot be deleted', soc)
                        f.write('\n' + line.rstrip())
                else:
                    # Before the message
                    f.write('\n' + line.strip())
            else:
                f.write('\n' + line.strip())

    if found:
        sendMessage('Line deleted', soc)

def edit_message(threadtitle, msgNumber, message, user, soc):
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
        sendError(f'Thread {threadtitle} does not exist', soc)
        print('Incorrect thread specified')
        return
    
    msgNum = int(msgNumber)
    if msgNum < 1 or msgNum > get_lastnumber(threadtitle):
        sendError(f'Message {str(msgNum)} does not exist in {threadtitle}', soc)
        print('Incorrect message number specified')
        return
    
    found = False
    with open(threadtitle, 'r+') as f:
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
                        # User wrote message
                        found = True
                        msg = ' '.join(message)
                        prefix = ' '.join(line.split()[0:2])
                        f.write('\n' + prefix + ' ' + msg)
                    else:
                        sendError('The message belongs to another user and cannot be edited', soc)
                        print('Message cannot be edited')
                        f.write('\n' + line.rstrip())
                else:
                    f.write('\n' + line.strip())
            else:
                f.write('\n' + line.strip())

    if found:
        sendMessage('The message has been edited', soc)
        print('Message edited')

def list_threads(user, soc):
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
        sendMessage('No threads to list', soc)
    else:
        for thread in threads:
            sendMessage(thread['title'], soc)

def read_thread(threadtitle, user, soc):
    '''
    RDT: Read thread
    USAGE: 'RDT threadtitle'
    Sends the file minus the first line to the client
    Client displays all contents and info of uploaded files
    If thread doesn't exist give error
    '''
    print(user + ' issued RDT command')
    if not thread_exists(threadtitle):
        sendError(f'Thread {threadtitle} does not exist', soc)
        print('Incorrect thread specified')
        return
    
    with open(threadtitle, 'r') as f:
        f.readline()
        for line in f:
            sendMessage(line, soc)
    
    print(f'Thread {threadtitle} read')



def upload_file(threadtitle, filename, user, soc):
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
    # Overengineered, the module
    print(user + ' issued UPD command')
    thread = thread_exists(threadtitle)
    if not thread:
        sendError('Thread does not exist', soc)
        return
    fileid = 0
    if files != []:
        # There are files
        fileid = files[-1]['id'] + 1
        if fileid > 255:
            fileid = 0
            # I feel like we can safely assume 
            # there will be less than 256 files 
            # being uploaded at the same time
    files.append({
        'id': fileid,
        'name': filename,
        'user': user,
        'thread': threadtitle,
    })
    sendUpload(filename + ' ' + str(fileid), soc)

    thread['files'].append(filename)

def download_file(threadtitle, filename, user, soc):
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
        sendError(f'Thread {threadtitle} does not exist', soc)
        print('Incorrect thread specified')
        return
    if filename not in thread['files']:
        sendError(f'File does not exist in Thread {threadtitle}', soc)
        print(f'{filename} does not exist in Thread {threadtitle}')
        return
    
    combinedName = threadtitle + '-' + filename
    filesize = str(path.getsize(combinedName))
    sendDownload(filename + ' ' + filesize, soc)

    file = open(combinedName, 'rb')
    data = file.read(1024)
    while data:
        print('Sending...')
        message_queues[soc].put(data)
        #sendToSocket(data, soc)
        #soc.send(data)
        data = file.read(1024)
    file.close()
    print('File sent')
    sendMessage(f'{filename} successfully downloaded', soc)
    
def remove_thread(threadtitle, user, soc):
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
        sendError('Thread does not exist', soc)
        return
    
    #FIXME:
    isOwner = False
    with open(threadtitle, 'r') as f:
        owner = f.readline().rstrip()
        #print(owner)
        #print(user)
        if owner == user:
            isOwner = True

    if isOwner:
        removeFile(threadtitle)
        for filename in thread['files']:
            removeFile(threadtitle + '-' + filename)
    else:
        sendError('The thread was created by another user and cannot be removed', soc)
        print(f'Thread {threadtitle} cannot be removed')
        return
    
    sendMessage(f'Thread {threadtitle} removed', soc)
    print(f'Thread {threadtitle} removed')

def userExit(name, soc):
    sendMessage('Logging out', soc)
    sendLogout(soc)
    print(name + ' logged out')
    curr_users.remove(name)
    #soc gets closed by the loop at the bottom

def shutdown(password, user, soc):
    #FIXME: Work with multiple clients
    print(f'{user} issued SHT command')
    if password != admin_passwd:
        sendError('Incorrect password', soc)
        sendInputComm(soc)
        print('Incorrect password')
        return

    # server is inputs[0]
    for i in inputs[1:]:
        sendMessage('Server shutting down', i)
        sendLogout(i)
    print('Server shutting down')
    for thread in threads:
        removeFile(thread['title'])
        for f in thread['files']:
            removeFile(thread['title'] + '-' + f)
    # TODO: close all current connections
    global server_shutdown
    server_shutdown = True
    #server.close()
    
def removeFile(filename):
    '''Safely removes files'''
    if path.exists(filename):
        remove(filename)

#FIXME: 
def recv_handler(message, soc):
    comm = message[0]
    if comm == 'C':
        typeCommand(message[1:], soc)
    elif comm == 'U':
        typeUsername(message[1:], soc)
    elif comm == 'N':
        typeRegisterName(message[1:], soc)
    elif comm == 'L':
        typeLogin(message[1:], soc)
    elif comm == 'R':
        typeRegister(message[1:], soc)
    elif comm == 'F':
        typeFile(message[1:], soc)
    elif message == 'Hello':
        # Initial connection
        pass
    else:
        print('Invalid Command')
    # elif comm == b'F':
    #     typeFile(message[1:], soc)

'''
    Input types:

    Command: Response to the send command
        Cuser comm arg1 arg2....
    Username: Check username exists, if it does move to login
            If username doesn't exist prompt username again,
        Uuser
    Register Name: Check username exists, if it does move to login
                If username doesn't exist, prompt to register
        Nname
    Login: Login attempt with user and password
        Luser password
    Register: Register a new user, do if username doesn't exist
        Ruser password
'''

def typeCommand(message, soc):
    words = message.split()
    username = words[0]
    if username not in curr_users:
        sendError('User not currently logged in', soc)
    cmd = words[1]
    args = len(words)

    if cmd == 'CRT':
        if args == 3:
            create_thread(words[2], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'MSG':
        if args >= 4:
            send_message(words[2], words[3:], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'DLT':
        if args == 4:
            delete_message(words[2], words[3], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'EDT':
        if args >= 5:
            edit_message(words[2], words[3], words[4:], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'LST':
        if args == 2:
            list_threads(username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'RDT':
        if args == 3:
            read_thread(words[2], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'UPD':
        if args == 4:
            upload_file(words[2], words[3], username, soc)
            return
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'DWN':
        if args == 4:
            download_file(words[2], words[3], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'RMV':
        if args == 3:
            remove_thread(words[2], username, soc)
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'XIT':
        if args == 2:
            userExit(username, soc)
            return
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    elif cmd == 'SHT':
        if args == 3:
            shutdown(words[2], username, soc)
            return
        else:
            sendError(f'Invalid syntax for {cmd}', soc)
    else:
        sendError('Invalid Command', soc)
    
    sendInputComm(soc)

def typeUsername(message, soc):
    '''
    Check username exists
    If it does, send login
    If it doesn't, move to register if user already connected
    If user hasn't connected before, add to connected, then try username again
    '''
    result = findUsername(message)
    if result:
        if result in curr_users:
            sendError('User already logged in', soc)
            sendInputUser('Enter your username:', soc)
        else:
            sendName(result.split()[0], soc)
            sendInputLogin('Enter password:', soc)
    else:
        sendError('Username not found', soc)
        sendInputRegisterName('Enter username:', soc)

def findUsername(user):
    with open('credentials.txt', 'r') as f:
        for line in f.readlines():
            words = line.split()
            if words[0] == user:
                return line
    
    return None

def typeRegisterName(message, soc):
    result = findUsername(message)
    sendName(message.split()[0], soc)
    if result:
        sendInputLogin('Enter password:', soc)
    else:
        sendMessage('Username not found, registering new user', soc)
        sendInputRegister(f'Input new password for {message.split()[0]}:', soc)

def typeLogin(message, soc):
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
        curr_users.append(inUser)
        sendMessage('Welcome to the forum', soc)
        print(inUser + ' successful login')
        sendInputComm(soc)
    else:
        sendError('Incorrect password', soc)
        print(inUser + ' incorrect password')
        sendInputLogin('Enter username:', soc)

def typeRegister(message, soc):
    '''
    Adds username and password to credentials
    Then adds to logged in
    '''
    with open('credentials.txt', 'a') as f:
        f.write(message + '\n')
        print('New user ' + message.split()[0] + ' registered')
        curr_users.append(message.split()[0])
        sendMessage('Welcome to the forum', soc)

    sendInputComm(soc)
        
def getFile(fileid):
    return next((x for x in files if x['id'] == fileid), None)

def typeFile(message, soc):
    fileid = int(message.split()[0])
    filesize = int(message.split()[1])

    file = getFile(fileid)
    if file:
        file['size'] = filesize
    else:
        #This shouldn't ever happen
        print(fileid)
        print('Incorrect file id')
        sendError('Wrong file ID', soc)
        sendInputComm(soc)
        return

    soc.setblocking(1)
    filename = getFilename(file)
    with open(filename, 'ab') as f:
        while filesize > 0:
            data = soc.recv(1024)
            f.write(data)
            filesize -= len(data)
    soc.setblocking(0)    
    sendMessage('File received', soc)

    with open(file['thread'], 'a') as f:
        f.write('\n' + file['user'] + ' uploaded ' + file['name'])
        f.close()

    user = file['user']
    name = file['name']
    thread = file['thread']
    print(f'{user} uploaded file {name} to {thread}')

    
    sendInputComm(soc)
   
def getFilename(file):
    return file['thread'] + '-' + file['name']

#try:
#using the socket module

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
# change this port number if required
if len(argv) == 3:
    server_port = int(argv[1])
    admin_passwd = argv[2]
else:
    print('Correct usage: python3 server.py server_port admin_passwd')
    exit()
server = socket(AF_INET, SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', server_port))
server.listen(5)
print('The server is ready to receive')

server_shutdown = False

# https://pymotw.com/2/select/
inputs = [server]
outputs = []
message_queues = {}

while inputs:
    if inputs == [server]:
        if server_shutdown:
            server.close()
            exit()
        else:
            #TODO: Check this works
            print('Waiting for clients')

    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # Handle inputs
    for s in readable:
        if s is server:
            # New connection
            connection, client_address = s.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = Queue()

            sendInputUser('Enter your username:', connection)
            
        else:
            # Established client
            data = s.recv(1024).decode('utf-8')
            #DEBUG: 
            #print(f'Received: {data}')
            if data:
                #message_queues[s].put(data)
                # if data[0] != 'F':
                #     data = data.decode('utf-8')
                # else:
                #     typeFile(data[1:], s)
                recv_handler(data, s)
                if s not in outputs:
                    outputs.append(s)
            else:
                # Client ended connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

                del message_queues[s]

    # Handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
            if next_msg == 'Q\u23F9'.encode('utf-8'):
                # Shutting down client
                inputs.remove(s)
                outputs.remove(s)
                del message_queues[s]
        except:
            # No more messages
            outputs.remove(s)
        else:
            #DEBUG: 
            #print(f'Sent: {next_msg} to {s.getpeername()}')
            s.send(next_msg)
    
    # Handle exceptions:
    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        del message_queues[s]
