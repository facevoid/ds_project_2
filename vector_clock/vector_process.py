import socket 
import json
import time
from threading import Thread
import argparse
import random

# lamport_clock = 0
multicast_ports = [ 6001, 6002]
my_port = 6001
host = 'localhost'
event_queue = []
ack_required = 0
PID = 1
p_event_id = 1
vectors_clock = [0 for i in range(len(multicast_ports))]

def update_req_msg(pid, p_event_id, lamport_clock):
    return json.dumps(
        {
            'type': 'update',
            'PID': pid, 
            'p_event_id': p_event_id,
            'lamport_clock': lamport_clock
        }
    ).encode()

def ack_msg(pid, p_event_id, lamport_clock):
    return json.dumps(
        {
            'type': 'ack',
            'PID': pid,
            'p_event_id': p_event_id,
            'lamport_clock': lamport_clock
        }
    ).encode()

def process_update_req(data):
    global lamport_clock
    if type(data) != dict:
        data = json.loads(data)
    event_queue.append(data)
    # lamport_clock = max(int(data['lamport_clock']), lamport_clock) + 1 
    vectors_clock[data['PID'] - 1] += 1


def process_ack(data):
    global ack_required
    global lamport_clock
    # print(ack_required)
    if type(data) != dict:
        data = json.loads(data)
    lamport_clock = max(data['lamport_clock'], vectors_clock[data['PID'] - 1])
    if ack_required != 0:
        ack_required -= 1
    if ack_required % 2 == 0:
        # print(f"prcess {data['p_event_id']} from {PID} is executed after receiving all acks")
        if len(event_queue) == 0:
            return
        top_evt = event_queue.pop(0)
        if type(top_evt) != dict:
            top_evt = json.loads(top_evt)
        print(f"PID {PID}: {PID}.{top_evt['p_event_id']} has been executed after receiving all acks, vectors_clock {vectors_clock}")
        
        
        



class ReceiverThread(Thread):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind((host, my_port))
    
    def run(self):
        while True:
            data, adderss = self.sock.recvfrom(1024)
            data = json.loads(data)
            # print(data)
            if data['type'] == 'ack':
                process_ack(data) 
            if data['type'] == 'update':
                process_update_req(data) 

class UpdateQueueBufferThread(Thread):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    def run(self):
        global event_queue
        while True:
            for evt in reversed(event_queue[:]):
                # print(evt)
                if type(evt) != dict:
                    evt = json.loads(evt)
                if evt['PID'] == PID:
                    continue
                for port in multicast_ports:
                    if port != my_port:
                        msg = ack_msg(PID, evt['p_event_id'], vectors_clock[PID-1])
                        self.sock.sendto(msg, (host, port))
                event_queue.remove(evt)
                
                        


def create_event():
    global lamport_clock
    global p_event_id
    global PID
    global ack_required
    # global multicast_ports
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    for port in multicast_ports:
        if port != my_port:
            msg = update_req_msg(PID, p_event_id, lamport_clock=vectors_clock[PID -1])
            sock.sendto(msg, (host, port))
            # print(f'Message has been sent to {port}')
    # print(f'Event Created in {PID}, Event id {p_event_id} now in buffer, lamport clock {lamport_clock}')
    
    
    msg_for_this_evt = update_req_msg(PID, p_event_id, lamport_clock= vectors_clock[PID -1])
    event_queue.append(msg_for_this_evt)
    # lamport_clock += 1
    vectors_clock[PID - 1] += 1
    p_event_id += 1

    #Updating  required acknowledgements based on distributed system's member
    ack_required += len(multicast_ports) - 1 



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pid', '--PID')
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    PID = int(args.PID)
    my_port = int(args.port) 

    receive_thread = ReceiverThread()
    # receive_thread.daemon = True
    receive_thread.start()

    update_buffer_thread = UpdateQueueBufferThread()
    # update_buffer_thread.daemon = True
    update_buffer_thread.start()

    time.sleep(10)
    for i in range(50):
        rand_number = random.randint(0,1000000)
        if rand_number % 2 == 0:
            create_event()
            time.sleep(3)
    