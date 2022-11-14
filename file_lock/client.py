import threading
import time 
import socket

def get_server_connection(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host, port))
    print('Connect to server')
    return conn 

def listen_to_server(conn):
    while True:
        message = conn.recv(1024)
        if message.decode() == 'Accepted':
            with open('file.txt', 'r+') as fp:
                number = int(fp.read())
                fp.seek(0)
                fp.write(str(number+1))
                print(f'Number updated to {str(number+1)}')
                time.sleep(10)

            conn.send('Release'.encode())
        else:
            print(message.decode())
            # print(message.decode().split('<')[-1])




if __name__ == '__main__':
    conn = get_server_connection('localhost', 6007)
    threading.Thread(target = listen_to_server, args = (conn, )).start()
    for i in range(10):
        conn.send('Acquire'.encode())
        print('Sent request to server')
        time.sleep(5)
        
