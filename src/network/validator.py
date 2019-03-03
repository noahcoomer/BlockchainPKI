"""
    Listen for transactions on the network and validate them
"""
from random import randint
from threading import Thread

import time
import errno
import socket

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
        self._init_net()

    def _init_net(self):
        '''
            Initalizes a TCP sockets for incoming traffic and binds it. 

            If the connection is refused, -1 will be returned.
            If the address is already in use, a new random port will be recursively tried.
        '''
        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            while True:
                conn, addr = self.net.accept()
                print("Connection created from %s:%d" % addr)
                with conn:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        else:
                            data = data.decode()
                            print("Data received: %s" % data)

        if self.net:
            # Create a new thread to handle incoming connections
            receive_thread = Thread(target=_receive)
            receive_thread.start()  # Start the thread

    def addr(self, which_net=True):
        '''
            Returns the address of a specific net or -1 upon error. By default, it 
            returns the address of the inbound connection.

            :param bool which_net: indicates which socket (0 is outbound, 1 is inbound)
        '''
        return self.address[which_net] if self.address[which_net] else -1

    def message(self, v, msg):
        '''
            Send a message to a validator v

            :param Validator v: the validator to receive the message
            :param msg: the message to send to the validator

            v's net should be initialized and listening for incoming connections.
            msg must be an instance of str or bytes. 
        '''
        if self.net and v.net:
            # Connect to v's inbound net using self's outbound net
            address = v.address
            if not isinstance(msg, str):
                raise TypeError(
                    "msg should be of type str, not %s" % type(msg))
            else:
                if isinstance(msg, str):
                    msg = msg.encode()  # encode the msg to binary
                print("Attempting to send to %s:%s" % v.address)
                # Create a new socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(address)  # Connect to v
                    s.sendall(msg)  # Send the entirety of the message
        else:
            raise Exception(
                "The validator's net must be initialized and listening for connections")

    def cleanup(self):
        '''
            Closes sockets and stops the receive thread.
        '''
        self.net.close()  # Close the incoming socket


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
