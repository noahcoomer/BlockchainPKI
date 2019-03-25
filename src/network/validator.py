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
BUFF_SIZE = 2048


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
        # Buffer to store incoming transactions
        self.mempool = []
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
            # add this connection to a dictionary of incoming connections
            with conn:
                data = ''
                while True:
                    data += conn.recv(BUFF_SIZE)
                    if not data:
                        # Deserialize the entire object when data reception has ended
                        decoded_transaction = pickle.loads(data)
                        print("Received data: " + decoded_transaction)
                        # check if this transaction is in mempool
                        # broadcast to network
                        data = ''
        except socket.timeout:
            pass
        return decoded_transaction


    def send(self):
        '''
            Send thread; handles outgoing transactions
        '''
        pass

    # def sign_message(self, private_key, message):
    #     signer = PKCS1_v1_5.new(private_key)
    #     sig = signer.sign(message)
    #     return sig

    # def verify_message(self, public_key, message):
    #     verifier = PKCS1_v1_5.new(public_key)
    #     verified = verifier.verify(message, sign_message())
    #     assert verified, "Signature Verification Failed"

    # def verify_transaction_signature(self, sender_address, signature, transaction):
    #     """
    #     Check that the provided signature corresponds to transaction
    #     signed by the public key (sender_address)
    #     """
    #     public_key = RSA.importKey(binascii.unhexlify(sender_address))
    #     verifier = PKCS1_v1_5.new(public_key)
    #     h = SHA.new(str(transaction).encode('utf8'))
    #     return verifier.verify(h, binascii.unhexlify(signature))


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
