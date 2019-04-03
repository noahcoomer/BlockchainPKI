from threading import Thread
import time

import sys
sys.path.append('../src/')
from validator import Validator
from client import Client
from transaction import Transaction

PORTS = [6666, 6644]
TEST_KEY_PATH = open("/Users/noahcoomer/.BlockchainPKI/keys/public.pem", 'r')

def val_thread(port):
    val = Validator(port=port)
    val.create_connections()
    while True:
        val.receive()

def client_thread():
    cli = Client(name="Client 1")
    cli.create_connections()
    cli._load_other_ca(capath=cli.validators_capath)
    for i in range(5):
        tx = Transaction(transaction_type='Standard', inputs=str(i))
        cli.broadcast_transaction(tx)
        time.sleep(2)

def main():
    for i in PORTS:
        thr = Thread(target=val_thread, args=(i,))
        thr.start()
    time.sleep(1)

    thr = Thread(target=client_thread)
    thr.start()

if __name__ == '__main__':
    main()