from random import randint
from threading import Thread
# from Crypto.Signature import PKCS1_v1_5
from transaction import Transaction

import os
import ssl
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

    def __init__(self, name=None, addr="0.0.0.0", port=4321, bind=True, cafile="~/.BlockchainPKI/rootCA.pem",
                 keyfile="~/.BlockchainPKI/rootCA.key", validators_capath="~/.BlockchainPKI/validators/"):
        '''
            Initialize a Validator object

            :param str name: The hostname
            :param str bind_addr: The ip address to bind to for serving inbound connections
            :param int bind_port: The port to bind to for serving inbound connections
            :param bool bind: Whether or not to bind to (addr, port)
            :param str cafile: The path to the CA
            :param str keyfile: The path to the private key
            :param str validators_capath: The directory to where other Validators CAs are saved
        '''
        self.name = name or socket.getfqdn(socket.gethostname())
        self.address = addr, port
        self.bound = bind

        # Buffer to store incoming transactions
        self.mempool = []

        # Buffer to store connection objects
        self.connections = []

        if bind:
            self.cafile = cafile
            self.keyfile = keyfile
            self.validators_capath = validators_capath

            # Initialize the network, both the send and receive context,
            # and load the necessary CAs
            self._init_net()
            self._load_root_ca(cafile=self.cafile,
                               keyfile=self.keyfile)
            self._load_other_ca(capath=self.validators_capath)

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
            # Context for decrypting incoming connections
            self.send_context = ssl.create_default_context()
            self.receive_context = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH)

    def _load_root_ca(self, cafile, keyfile):
        '''
            Load a CA and private key

            :param str cafile: A path to the CA file
            :param str keyfile: A path to the private key
        '''
        assert self.receive_context != None, "Initialize the receive context before loading CAs."

        cafile = cafile.replace("~", os.environ["HOME"])
        keyfile = keyfile.replace("~", os.environ["HOME"])

        if os.path.exists(cafile) and os.path.exists(keyfile):
            self.receive_context.load_cert_chain(
                certfile=cafile, keyfile=keyfile)
            print("Root CA and key loaded from %s and %s." % (cafile, keyfile))
        else:
            raise FileNotFoundError(
                "Either %s or %s does not exist. Please generate a CA and private key." % (cafile, keyfile))

    def _load_other_ca(self, capath=None):
        '''
            Loads a set of CAs from a directory
            into the sending context
        '''
        assert self.send_context != None, "Initialize the send context before loading CAs."

        if capath == None:
            # This is the default path to the cafiles if nothing is entered
            capath = self.validators_capath

        capath = capath.replace("~", os.environ["HOME"])

        if not os.path.exists(capath):
            print("Directory %s does not exist" % capath)
            cont = input("Would you like to create %s? (y/n)" % capath)
            if cont.strip() == 'y':
                os.makedirs(capath)
                print("Created %s" % capath)
        elif len(os.listdir(capath)) == 0:
            raise FileNotFoundError(
                "No other Validator CAs were found at %s. You will be unable to send any data without them." % capath)
        else:
            cafiles = [path for path in os.listdir(
                capath) if path.endswith('.pem')]
            print("Loaded %d certificates from %s" %
                  (len(cafiles), capath))

            for path in cafiles:
                abspath = os.path.join(capath, path)
                self.send_context.load_verify_locations(abspath)

    def receive(self):
        '''
            Receive thread; handles incoming transactions
        '''
        try:
            conn, addr = self.net.accept()
            print("Connection from %s:%d" % (addr[0], addr[1]))
            DATA = bytearray()  # used to store the incoming data
            with self.receive_context.wrap_socket(conn, server_side=True) as secure_conn:
                # Receive the initial BUFF_SIZE chunk of data
                data = secure_conn.recv(BUFF_SIZE)
                while data:
                    # Continue receiving chunks of the data until the buffer is empty
                    # (until the client sends empty data)
                    DATA += data
                    data = secure_conn.recv(BUFF_SIZE)
                # Deserialize the entire object when data reception has ended
                decoded_transaction = pickle.loads(DATA)
                print("Received data from %s:%d: %s" %
                      (addr[0], addr[1], decoded_transaction))
                #########

                print(type(decoded_transaction) == Transaction)
                # check if this transaction is in mempool
                if decoded_transaction not in self.mempool:
                    self.mempool.append(decoded_transaction)
                
                # broadcast to network

                #return decoded_transaction
        except socket.timeout:
            pass

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
                msg = msg.encode()  # encode the msg to binary
            print("Attempting to send to %s:%s" % v.address)
            secure_conn = self.send_context.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=v.name)
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

    def broadcast(self, message):
        '''
            Broadcast a message to every other validator that is connected to this node
        '''
        i = 0
        for addr in self.connections:
            ip, port = addr
            name = "val-" + str(i)
            receiver = Validator(name=name, addr=ip, port=port)
            self.message(receiver, message)

    def close(self):
        '''
            Closes a Validator and its net. Ignores Validators whose nets are not bound.
        '''
        if self.bound:
            self.net.close()


if __name__ == "__main__":
    Alice = Validator(port=1234)
    Bob = Validator(name="ubuntu-xenial", addr="127.0.0.1",
                    port=6666, bind=False)

    tx = pickle.dumps({'msg': 'Hello! Is this thing on?',
                                'x': 'Any serialized object can be sent.',
                                'could_be': 'This could be a transaction!'})
    try:
        while True:
            # Send the serialized object to Guest
            Alice.message(Bob, tx)
            time.sleep(1)
    except KeyboardInterrupt:
        Alice.close()
