"""
    Listen for transactions on the network and validate them
"""
from random import randint
from threading import Thread
from Crypto.Signature import PKCS1_v1_5
#from data import transaction

import time
import errno
import socket
import binascii
import threading

INCONN_THRESH = 128
OUTCONN_THRESH = 8


class Validator(object):

    def __init__(self, name, bind_addr="0.0.0.0", bind_port=None):
        '''
            Initialize a Validator object

            :param str name: A canonical name for the validator
            :param str bind_addr: The ip address to bind to for serving inbound connections
            :param int bind_port: The port to bind to for serving inbound connections
        '''
        self.name = name
        self.address = bind_addr, bind_port
        self.is_receiving = False
        self._init_net()

    def _init_net(self):
        '''
            Initializes a TCP socket for incoming traffic and binds it.

            If the connection is refused, -1 will be returned.
            If the address is already in use, a new random port will be recursively tried.
        '''
        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.setblocking(False)
            self.net.bind(self.address)  # Bind to address
            self.net.listen()  # Listen for connections
            self.receive()  # Start receiving data
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                # Connection refused error
                return -1, e
            elif e.errno == errno.EADDRINUSE:
                # Address already in use, try another port
                addr, port = self.address
                new_port = randint(1500, 50000)
                print("Address %s:%d is already in use, trying port %d instead" %
                      (addr, port, new_port))
                self.address = addr, new_port
                self._init_net()  # Try to initialize the net again

    def receive(self):
        '''
            Receive incoming connections on a seperate thread

            The thread is terminated when receive_thread's "do_run"
            attribute is set to False. See cleanup().
        '''
        def _receive():
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                try:
                    conn, addr = self.net.accept()
                    conn.setblocking(True)
                    with conn:
                        # print("Connection created from %s:%d" % addr)
                        while True:
                            data = conn.recv(4096)
                            if not data:
                                break
                            else:
                                data = data.decode()
                                print("Data received: %s" % data)
                except BlockingIOError:
                    continue  # non-blocking sockets raise BlockingIOError, but these can be ignored
        if self.net:
            self.is_receiving = True

            # Create a new thread to handle incoming connections
            self.receive_thread = Thread(target=_receive)
            self.receive_thread.start()  # Start the thread

    def addr(self):
        '''
            Returns the address
        '''
        return self.address

    def sign_message(self, private_key, message):
        signer = PKCS1_v1_5.new(private_key)
        sig = signer.sign(message)
        return sig

    def verify_message(self, public_key, message):
        verifier = PKCS1_v1_5.new(public_key)
        verified = verifier.verify(message, sign_message())
        assert verified, "Signature Verification Failed"

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

    def message(self, v, msg):
        '''
            Send a message to a validator v

            :param Validator v: the validator to receive the message
            :param msg: the message to send to the validator

            v's net should be initialized and listening for incoming connections.
            msg must be an instance of str or bytes.
        '''
        if self.net and v.net and self.is_receiving:
            # Connect to v's inbound net using self's outbound net
            address = v.address
            if not isinstance(msg, str):
                raise TypeError(
                    "msg should be of type str, not %s" % type(msg))
            else:
                if isinstance(msg, str):
                    msg = msg.encode()  # encode the msg to binary
                # print("Attempting to send to %s:%s" % v.address)
                # Create a new socket (the outbound net)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setblocking(True)
                    try:
                        s.connect(address)  # Connect to v
                        s.sendall(msg)  # Send the entirety of the message
                    except OSError as e:
                        # Except cases for if the send fails
                        if e.errno == errno.ECONNREFUSED:
                            return -1, e
        else:
            raise Exception(
                "The validator's net must be initialized and listening for connections")

    def close(self):
        '''
            Closes sockets and stops the receive thread.
        '''
        self.receive_thread.do_run = False  # tell receive_thread to stop running
        self.receive_thread.join()  # wait for the thread to exit
        self.is_receiving = False
        self.net.close()  # close the inbound socket

        print("Closed %s" % self.name)


if __name__ == "__main__":
    # Test cases
    Alice = Validator(bind_port=1234, name="Alice")
    Bob = Validator(bind_port=4321, name="Bob")

    # Connect Alice to Bob, and send Bob a message.
    # So, in this case, Bob is acting as the server and Alice the client.
    Alice.message(Bob, "Hello! My name is Alice.")

    # Alice can also act as a server and send messages to Bob.
    Bob.message(Alice, "Hello, Alice. My name is Bob.")
    Alice.message(Bob, "How are you, Bob?")

    # The order of messages should be preserved.
    for i in range(15):
        Alice.message(Bob, "Message %d to Bob" % i)
        Bob.message(Alice, "Message %d to Alice" % i)

    # Close both Alice and Bob
    Alice.close()
    Bob.close()
