import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = ''
port = 56789

with open('config.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'server' in line:
            ip = line[line.index(':')+1:].replace('\n', '').strip()
        if 'port' in line:
            port = int(line[line.index(':')+1:].replace('\n','').strip())


try:
    s.bind(('', port))
except socket.error as e:
    print(e)

s.listen(2)
print('Waiting for incoming connections')

clientId = 0
# formatted as clientID(also color, 0 for blue),x,y,lookingdirection,fired,health, otherhealth
data = ['0,100,400,0,0,20,20', '1,700,400,3.14,0,20,20']


def threaded_server(conn: socket.socket):
    global clientId, data
    conn.send(str.encode(data[clientId]))
    clientId = 1
    reply = ''
    while True:
        try:
            d = conn.recv(2048)
            reply = d.decode('utf-8')
            if not d:
                conn.send(str.encode('ENDING CONNECTION'))
                break
            else:
                # print(f'Received {reply}')
                r_data = reply.split(',')
                id = r_data[0]
                data[int(id)] = reply
                if id == '1':
                    id = 0
                else:
                    id = 1
                reply = data[id][:]
                # print(f'Sending {reply}')
            conn.sendall(str.encode(reply))
        except:
            break
    print('Connection closed')
    conn.close()

while True:
    conn, addr = s.accept()
    print(f'Connected to: {addr}')
    start_new_thread(threaded_server, (conn,))
