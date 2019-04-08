from random import randint
from abc import ABC, abstractmethod

import os
import ssl
import socket
import errno


class Node(ABC):
    '''
        Base class for a generic node
    '''

    def __init__(self, hostname=None, addr="0.0.0.0", port=4848, bind=True, capath="~/.BlockchainPKI/validators/"):
        '''
            Initialize the Node object

            :param str hostname: The fully qualified domain name
            :param str addr: The ip address to bind to
            :param int port: The port to bind to
            :param bool bind: Whether or not to bind a socket
            :param str capath: The path to the Validators CAs
        '''
        self.capath = capath.replace('~', os.environ['HOME'])

        if not bind:
            assert hostname != None, "Hostname must be specified when not binding"
            self.hostname = hostname
            self.address = (socket.gethostbyname(self.hostname), 8080)
        else:
            self.hostname = hostname or socket.getfqdn(socket.gethostname())
            self.address = (addr, port)
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
        finally:
            # Create a context for encrypting/decrypting network connections
            self.context = ssl.create_default_context()
            self.context.check_hostname = False
            self.load_other_ca()

    @abstractmethod
    def message(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    def load_other_ca(self, capath=None):
        '''
            Loads a list of certificates from capath into the SSLContext
        '''
        capath = capath or self.capath
        capath = capath.replace('~', os.environ['HOME'])

        if not os.path.exists(capath):
            # The capath directory does not exist
            print("Directory %s does not exist" % capath)
            return
        elif len(os.listdir(capath)) == 0:
            # The capath directory contains no files
            raise FileNotFoundError("Directory %s is empty.")
        else:
            # Load all the CAs
            cafiles = [path for path in os.listdir(
                capath) if path.endswith('.pem')]
            for path in cafiles:
                abspath = os.path.join(capath, path)
                self.context.load_verify_locations(abspath)

    def close(self):
        if self.net != None:
            self.net.close()
