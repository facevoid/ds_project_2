
import socket 
import time 
import threading 


lock_queue = []

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)
    return server_socket


def process_acq_req(conn):
    global lock_queue
    global lock_status

    if len(lock_queue) != 0:
        lock_queue.append(conn)
        conn.send(f'Queued: {len(lock_queue)} position in the queue '.encode())
        time.sleep(3)
    else:
        conn.send('Accepted'.encode())
        lock_queue.append(conn)

def process_release_req(conn):
    global lock_queue
    global lock_status

    queue_head = lock_queue.pop(0)
    
    if lock_queue:
        lock_queue[0].send('Accepted'.encode())
        






def handle_client(conn, address):
    while True:
        message = conn.recv(1024)
        print(message.decode())
        if message.decode() == 'Acquire':
            process_acq_req(conn)
        if message.decode() == 'Release':
            process_release_req(conn)

if __name__ == '__main__':
    server_socket = start_server('localhost', 6007)
    
    #Accept connections from clients
    while True:
        conn, address = server_socket.accept()
        threading.Thread(target = handle_client, args = (conn,address)).start()
