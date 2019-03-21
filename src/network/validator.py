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
        self.net = Net(name=name, addr=addr, port=port, bind=bind)
        
        recv_thread = Thread(target=self.receive)
        send_thread = Thread(target=self.send)
        recv_thread.start()
        send_thread.start()

    def close(self):
        '''
            Closes a Validator and its net
        '''
        if self.net:
            self.net.close()


    def receive(self):
        '''
            Receive thread; handles incoming transactions
        '''
        pass

    
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
    Bob = Validator(name="Bob", addr="10.100.109.36", port=4321, bind=False)

    Alice.close()
    Bob.close()
