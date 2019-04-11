from random import randint
from threading import Thread
# from Crypto.Signature import PKCS1_v1_5
# from data import transaction

from net import Net

import time
import errno
import socket
import binascii
import threading

import pickle

INCONN_THRESH = 128
OUTCONN_THRESH = 8


class Validator(object):

    def __init__(self, name, addr="0.0.0.0", port=4321, bind=True):
        '''
            Initialize a Validator object

            :param str name: A canonical name for the validator
            :param str bind_addr: The ip address to bind to for serving inbound connections
            :param int bind_port: The port to bind to for serving inbound connections
            :param bool bind: Whether or not to bind to (addr, port)
        '''
        self.name = name
        # Create socket connection
        self.net = Net(name=name, addr=addr, port=port, bind=bind)
        # Instantiate Thread with a receive function
        recv_thread = Thread(target=self.receive)
        # Instantiate Thread with a send function
        send_thread = Thread(target=self.send)
        # Start receive thread
        recv_thread.start()
        # Start send thread
        send_thread.start()

    def close(self):
        '''
            Closes a Validator and its net
        '''
        if self.net:
            # Close socket
            self.net.close()


    def receive(self):
        '''
            Receive thread; handles incoming transactions
        '''
        try:
            conn, addr = self.net.accept()
            with conn:
                while True:
                    data = conn.recv(BUFF_SIZE)
                    if not data:
                        break
                        # Decode binary transaction
                        decoded_transaction = data.decode()
                        # Deserialize transaction
                        decoded_transaction = pickle.loads(decoded_transaction)
                    print("Received data: " + decoded_transaction)
        except socket.timeout:
            pass
        return decoded_transaction




    def message(self, v, msg):
        '''
            Send a message to another Validator
            :param Validator v: receiver of the message
            :param msg: the message to send
            v's net should be initialized and listening for incoming connections,
            probably bound to listen for all connections (addr="0.0.0.0").
            msg must be an instance of str or bytes.
        '''
        if self.net and self != v:
            # Connect to v's inbound net using self's outbound net
            address = v.address
            if isinstance(msg, str):
                msg = input('Client:')
                msg = msg.encode()  # encode the msg to binary
            elif isinstance(msg, Transaction) or isinstance(msg, Block):
                msg = pickle.dumps(msg)
            print("Attempting to send to %s:%s" % v.address)
            secure_conn = self.context.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=v.hostname)
            try:
                secure_conn.connect(address)  # Connect to v
                # Send the entirety of the message
                secure_conn.sendall(msg)
            except OSError as e:
                # Except cases for if the send fails
                if e.errno == errno.ECONNREFUSED:
                    print(e)
            except socket.error as e:
                print(e)
            finally:
                secure_conn.close()
        else:
            raise Exception(
                "The net must be initialized and listening for connections")


if __name__ == "__main__":
    Alice = Validator(name="Alice", port=1234)
    Bob = Validator(name="Bob", addr="10.228.112.126", port=4321, bind=False)

try:
    while True:
        # Receives incoming transactions
        Alice.receive()
        time.sleep(1)

        # Alice sends a message to Bob. So, in this case, Bob is acting as the server.
        #Bob.receive()
        #Alice.message(Bob, "Hello, Bob. This is Alice.")
        #time.sleep(1)


except KeyboardInterrupt:
    Alice.close()
    Bob.close()
