import time
import socket
import select
import Orion5
from General import ComQuery

def tryConversion(data):
    try:
        if '.' in data[3]:
            value = float(data[3])
        else:
            value = int(data[3])
    except ValueError:
        print(data)
        print("Orion5_Server: ValueError in conversion 1")
        return None
    return value

comport = None
print('\nSearching for Orion5...')
try:
    while True:
        comport = ComQuery()
        if comport is not None:
            print('Found Orion5, serial port name:', comport.device)
            break
        time.sleep(2)
except KeyboardInterrupt:
    print('\nExiting...\n')
    quit()

HOST = 'localhost'
PORT = 42000

running = True
max_timeouts = 5
timeouts = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

orion = Orion5.Orion5(comport.device)

print('\nIf MATLAB code crashes, call the orion.stop() function in MATLAB console.')

while running:
    print('\nWaiting for MATLAB')

    s.settimeout(None)
    conn, addr = s.accept()
    s.settimeout(0)

    connected = True
    print('Connected to MATLAB')

    try:
        while connected:
            data = ''

            ready = select.select([conn], [], [], 1)

            if ready[0]:
                data = conn.recv(1024).decode()
            
            if not data or len(data) == 0 or not ready[0]:
                timeouts += 1
                if timeouts > max_timeouts:
                    connected = False
                    print('Timeout')
            else:
                timeouts = 0

                if data == 'p':
                    conn.sendall('p'.encode())
                elif data == 'q':
                    break
                else:
                    try:
                        data = data.split('+')
                        data_dict = {
                            'jointID': int(data[0]),
                            'id1': data[1],
                            'id2': data[2]
                        }
                    except ValueError:
                        print(data)
                        print("Orion5_Server: ValueError in conversion 2")
                        continue
                    
                    if data_dict['id1'] == 'posFeedback':
                        conn.sendall(str(orion.getJointAngles()).encode())
                    elif data_dict['id1'] == 'velFeedback':
                        conn.sendall(str(orion.getJointSpeeds()).encode())
                    elif data_dict['id1'] == 'torFeedback':
                        conn.sendall(str(orion.getJointLoads()).encode())
                    elif data_dict['id1'] == 'posControl':
                        conn.sendall('r'.encode())
                        orion.setJointAnglesArray(eval(data[3]))
                    elif data_dict['id1'] == 'velControl':
                        conn.sendall('r'.encode())
                        orion.setJointSpeedsArray(eval(data[3]))
                    elif data_dict['id1'] == 'enControl':
                        conn.sendall('r'.encode())
                        orion.setJointTorqueEnablesArray(eval(data[3]))
                    elif data_dict['id1'] == 'config':
                        conn.sendall('r'.encode())
                        value = tryConversion(data)
                        if value == None:
                            continue
                        orion.setVariable(data_dict['id2'], value)
                    elif len(data) == 4:
                        conn.sendall('r'.encode())
                        value = tryConversion(data)
                        if value == None:
                            continue
                        orion.joints[data_dict['jointID']].setVariable(data_dict['id1'], data_dict['id2'], value)
                    elif len(data) == 3:
                        var = orion.joints[data_dict['jointID']].getVariable(data_dict['id1'], data_dict['id2'])
                        conn.sendall(str(var).encode())
    except KeyboardInterrupt:
        running = False
        print('\nExiting...\n')
    finally:
        conn.close()
        if running:
            print('Disconnected from MATLAB')

s.close()
orion.exit()
