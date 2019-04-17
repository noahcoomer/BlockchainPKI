from threading import Thread

import sys
sys.path.append('../src/')
from transaction import Transaction
from block import Block
from client import Client
from validator import Validator

PORTS = [6644, 6666, 6688]

def val_thread(port, leader):
    val = Validator(port=port)
    val.create_connections()
    while True:
        val.receive()

def main():
    # start three validator threads
    for i in PORTS:
        leader = False
        if i == 6644:
            leader = True
        thr = Thread(target=val_thread, args=(i,leader,))
        thr.start()

    # start the client
    #cli = Client()
    #cli.create_connections()
    #cli.update_blockchain()
    #cli.command_loop()

if __name__ == '__main__':
    main()