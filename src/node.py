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

    def __init__(self, hostname=None, addr="0.0.0.0", port=4848, bind=True, capath="~/.BlockchainPKI/validators/",
                 certfile="~/.BlockchainPKI/rootCA.pem", keyfile="~/.BlockchainPKI/rootCA.key"):
        '''
            Initialize the Node object

            :param str hostname: The fully qualified domain name
            :param str addr: The ip address to bind to
            :param int port: The port to bind to
            :param bool bind: Whether or not to bind a socket
            :param str capath: The path to the Validators CAs
        '''
        self.address = (addr, port)
        self.capath = capath.replace('~', os.environ['HOME'])

        if not bind:
            assert hostname != None, "Hostname must be specified when not binding"
            self.hostname = hostname
            self.address = (socket.gethostbyname(self.hostname), port)
        else:
            self.hostname = hostname or socket.getfqdn(socket.gethostname())
            self._init_net()

            self.certfile = certfile.replace('~', os.environ['HOME'])
            self.keyfile = keyfile.replace('~', os.environ['HOME'])
            self.receive_context = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH)
            self.receive_context.load_cert_chain(self.certfile, self.keyfile)

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

            :param str capath: The path to load from. Can absolute or relative to $HOME.
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

    def send_certificate(self, addr, port):
        '''
            Sends the certificate to addr:port through 
            standard, unencrypted TCP

            :param str addr: the ipv4 address to send to
            :param int port: the port number to send to
        '''
        certfile = open(self.certfile, 'rb').read()
        print("Read certfile. Attempting to send to %s:%d" % (addr, port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((addr, port))
                # Alert receiver that you want to send a certificate
                s.send(b'/cert')
                s.sendall(certfile)  # Send the certificate
            except OSError as e:
                print(e)
            except socket.timeout as e:
                print(e)

    def close(self):
        if self.net != None:
            self.net.close()
