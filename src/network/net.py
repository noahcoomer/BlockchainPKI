from random import randint
from threading import Thread

import time
import errno
import socket

BUFF_SIZE = 4096


class Net(object):

    def __init__(self, name, addr="0.0.0.0", port=None, bind=True):
        '''
            Initialize a Net object

            :param str name: A canonical name
            :param str addr: The ip address for serving inbound connections
            :param int port: The port for serving inbound connections
            :param bool bind: Whether or not to bind to (addr, port)
        '''
        self.name = name
        self.bound = bind
        self.address = addr, port

        if bind:
            self._init_net()

    def _init_net(self):
        '''
            Initializes a TCP socket for incoming traffic and binds it.

            If the connection is refused, -1 will be returned.
            If the address is already in use, a new random port will be recursively tried.
        '''
        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.settimeout(0.001)  # Blocking socket
            self.net.bind(self.address)  # Bind to address
            self.net.listen()  # Listen for connections
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                # Connection refused error
                return -1, e
            elif e.errno == errno.EADDRINUSE:
                # Address already in use, try another port
                addr, port = self.address
                new_port = randint(1500, 5000)
                print("Address %s:%d is already in use, trying port %d instead" %
                      (addr, port, new_port))
                self.address = addr, new_port
                self._init_net()  # Try to initialize the net again

    def receive(self):
        '''
            Receive incoming connections. Call repeatedly in a loop.
        '''
        try:
            conn, addr = self.net.accept()
            with conn:
                while True:
                    data = conn.recv(BUFF_SIZE)
                    if not data:
                        break
                    print("Data received from %s:%d: %s" %
                          (addr[0], addr[1], data.decode()))
        except socket.timeout:
            pass

    def addr(self):
        '''
            Returns the address
        '''
        return self.address

    def message(self, v, msg):
        '''
            Send a message to another Net

            :param Net v: receiver of the message
            :param msg: the message to send

            v's net should be initialized and listening for incoming connections.
            msg must be an instance of str or bytes.
        '''
        if self.net and self != v:
            # Connect to v's inbound net using self's outbound net
            address = v.address
            if not isinstance(msg, str):
                raise TypeError(
                    "msg should be of type str, not %s" % type(msg))
            else:
                if isinstance(msg, str):
                    msg = msg.encode()  # encode the msg to binary
                print("Attempting to send to %s:%s" % v.address)
                # Create a new socket (the outbound net)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setblocking(True)
                    try:
                        s.connect(address)  # Connect to v
                        s.sendall(msg)  # Send the entirety of the message
                    except OSError as e:
                        # Except cases for if the send fails
                        if e.errno == errno.ECONNREFUSED:
                            print(e)
                            # return -1, e
                    except socket.error as e:
                        print(e)
        else:
            raise Exception(
                "The net must be initialized and listening for connections")

    def close(self):
        '''
            Closes the inbound socket if it was initialized
        '''
        if self.bound and self.net != None:
            self.net.close()

    def __str__(self):
        return "Net: <Name: %s, Address: %s:%d, Bound: %s>" % (self.name, self.address[0], self.address[1], self.bound)


if __name__ == "__main__":
    # Test cases
    # Create two local nets, both listening on all addresses.
    Alice = Net(port=1234, name="Alice")
    Bob = Net(port=4321, name="Bob")

    # For non-local connections, set bind to False and specify the address and port
    # that the socket is running on.

    try:
        while True:
            # Bob sends a message to Alice. So, in this case, Alice is acting
            # as the server and Bob is acting as the client.
            Alice.receive()
            Bob.message(Alice, "Hello, Alice. This is Bob.")
            time.sleep(1)

            # Alice sends a message to Bob. So, in this case, Bob is acting as the server.
            Bob.receive()
            Alice.message(Bob, "Hello, Bob. This is Alice.")
            time.sleep(1)
    except KeyboardInterrupt:
        Alice.close()
        Bob.close()
