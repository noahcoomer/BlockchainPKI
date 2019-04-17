from random import choice
from string import ascii_uppercase, ascii_lowercase, digits

from node import Node
from block import Block
from blockchain import Blockchain
from transaction import Transaction
import client

import os
import ssl
import time
import errno
import pickle
import socket
import hashlib

INCONN_THRESH = 128
OUTCONN_THRESH = 8
BUFF_SIZE = 2048


class Validator(Node):
    def __init__(self, hostname=None, addr="0.0.0.0", port=4848, bind=True, capath="~/.BlockchainPKI/validators/",
                 certfile="~/.BlockchainPKI/rootCA.pem", keyfile="~/.BlockchainPKI/rootCA.key"):
        '''
            Initialize a Validator

            :param str certfile: The path to the CA
            :param str keyfile: The path to the private key
        '''
        super().__init__(hostname=hostname, addr=addr, port=port, bind=bind, capath=capath)

        # Buffer to store incoming transactions
        self.mempool = list()
        self.blockchain = Blockchain() #list()
        self.block = Block()
        # Buffer to store connection objects
        self.connections = list()
        # Buffer to store client connection objects
        self.client_connections = list()

        self.certfile = certfile.replace('~', os.environ['HOME'])
        self.keyfile = keyfile.replace('~', os.environ['HOME'])

        self.receive_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH)
        self.receive_context.load_cert_chain(self.certfile, self.keyfile)
        self.first = 0 # First index of the new sent tx mempool
        self.last = 0   # Last index of the new sent tx mempool
        

    def create_connections(self):
        '''
            Create the connection objects from the validators info file and store them as a triple
            arr[0] = hostname, arr[1] = ip, int(arr[2]) = port
        '''
        f = open('../validators.txt', 'r')
        for line in f:
            arr = line.split(' ')
            if self.hostname == arr[0] and self.address == (arr[1], int(arr[2])):
                continue
            else:
                v = Validator(
                    hostname=arr[0], addr=arr[1], port=int(arr[2]), bind=False)
                self.connections.append(v)
        f.close()

    def save_new_certfile(self, data):
        '''
            Saves a new certificate that was received from a Validator

            :param bytearray data: The certificate file
        '''
        def newfilename(namelength): return ''.join(
            choice(ascii_uppercase + ascii_lowercase + digits) for _ in range(namelength))

        # Create a random filename of length 15
        filename = newfilename(15)
        path = os.path.join(
            self.capath, "%s.pem" % filename)

        # Make sure a file doesn't already exist with that name. If it does, make a new name.
        while os.path.exists(path):
            path = os.path.join(self.capath, "%s.pem" % newfilename(15))

        # Save the certificate and remake the context with the new certificate included
        for p in os.listdir(self.capath):
            if p.endswith('.pem'):
                p = os.path.join(self.capath, p)
                content = open(p, 'rb').read()
                if content == data:
                    print("This certificate already exists at %s" % p)
                    return
        with open(path, 'wb') as f:
            f.write(data)
        print("New CA added at %s" % path)
        self.load_other_ca(self.capath)
        print("Reloaded Validator CAs")

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

    def broadcast(self, tx):
        '''
            Broadcast a message to every other validator that is connected to this node
        '''
        for conn in self.connections:
            self.message(conn, tx)

    def receive(self, mode='secure'):
        '''
            Receive thread; handles incoming transactions
            Add the incoming transaction into the pool. If after 10 seconds
            the number of transactions is 10 then call the Round Robin to chose
            Block Generator (Leader)

            :param: str mode: whether or not the connection is encrypted ('secure' or None).
            mode=None specifies the connection should not be encrypted.
        '''
        try:
            conn, addr = self.net.accept()
            print("Connection from %s:%d" % (addr[0], addr[1]))
            if mode is 'secure':
                s = self.receive_context.wrap_socket(conn, server_side=True)
            else:
                warn = input(
                    "Warning: Are you sure you want to allow insecure connections? (y/n)")
                warn = warn.strip().lower()
                if warn == 'y':
                    mode = 'insecure'
                    s = conn
                elif warn == 'n':
                    print("Setting mode=secure")
                    mode = 'secure'
                    s = self.receive_context.wrap_socket(
                        conn, server_side=True)
                else:
                    raise ValueError("Answer must be either (y/n)")

            DATA = bytearray()  # used to store the incoming data
            with s:
                start_time = int(time.time())
                # Receive the initial BUFF_SIZE chunk of data
                data = s.recv(BUFF_SIZE)
                while data:
                    # Continue receiving chunks of the data until the buffer is empty
                    # (until the client sends empty data)
                    DATA += data
                    data = s.recv(BUFF_SIZE)

                if b'/cert' in DATA:
                    # Validator sent their certificate
                    DATA = DATA[5:]  # Remove flag
                    self.save_new_certfile(data=DATA)
                    return

                # Deserialize the entire object when data reception has ended
                decoded_message = pickle.loads(DATA)
                # print("Received data from %s:%d: %s" %
                #       (addr[0], addr[1], decoded_message))
                if type(decoded_message) == Transaction:
                    # Add transaction to the pool
                    self.add_transaction(decoded_message)
                    print(self.mempool)
                    # broadcast to network
                    self.broadcast(decoded_message)
                    end_time = int(time.time())

                    # Probably need to add a leader flag here
                    if (end_time - start_time) >= 10:
                        start_time = int(time.time())
                        last = None
                        print("Call Round Robin to chose the leader")
                        self.create_block(self.first, self.last)
                    elif len(self.mempool) >= 3:
                        start_time = int(time.time())
                        last = None
                        blk = self.create_block(0, 3)
                        self.blockchain.chain.append(blk)
                        self.broadcast(blk)
                        self.mempool = list()
                elif type(decoded_message) == Block:
                    #print("Call verification/consensus function to vote on Block")
                    # If we are receiving an old block, we know we have received a client connection
                    if decoded_message.id <= self.blockchain.last_block.id:
                        h_name = socket.gethostbyaddr(addr[0])[0]
                        c = client.Client(hostname=h_name, addr=addr[0], port=4848, bind=False)
                        #self.client_connections.append((addr[0], 4848))
                        self.connections.append(c)
                        # Send the chain from the id onwards
                        for blk in self.blockchain.chain[decoded_message.id:]:
                            self.message(c, blk)
                    if decoded_message.id > self.blockchain.last_block.id:
                        self.blockchain.chain.append(decoded_message)
                else:
                    print("Data received was not of type Transaction or Block, but of type %s: \n%s\n" % (
                        type(decoded_message), decoded_message))
        except socket.timeout:
            pass

    def add_transaction(self, tx):
        '''
            Receive incoming transactions and add to mempool
        '''
        if tx.status == 'YES':
            pass
        elif tx.status == 'NO':
            pass
        else:
            if tx not in self.mempool:
                self.last = self.last + 1
                tx.status = "Open"
                self.mempool.append(tx)


    def create_block(self, first, last):
        block_tx_pool = []
        for tx in range(first, last):
            block_tx_pool.append(self.mempool[tx])

        self.block = Block(
            version=0.1,
            id=len(self.blockchain.chain),
            transactions=block_tx_pool,
            previous_hash=self.blockchain.last_block.hash,
            block_generator_address=self.address,
            block_generation_proof=self.certfile,
            nonce=0,
            status="Proposed"
        )
        return self.block


    # Add block to the blockchain
    def add_block(self):
        self.first = self.last + 1
        self.blockchain.add_block(self.block, self.block.compute_hash())
    

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


    def verify_txs(self, block):
        '''
            Verify transactions 

            param: Block block: the new generated block sent from block generator
        '''
        for tx in block.transactions:
            #tx = str(tx)
            if tx not in self.mempool:
                return False
        return True


if __name__ == "__main__":
    port = int(input("Enter a port number: "))
    val = Validator(hostname="localhost", port=port)
    
    # THIS COMMAND SHOULD ONLY BE EXECUTED ON THE VERY FIRST VALIDATOR TO GO ACTIVE
    #val.blockchain.create_genesis_block()
    # marshal = Validator(hostname="home.marshalh.com", port=8080, bind=False)

    try:
        while True:
            # tx = Transaction(inputs=0)
            # val.message(marshal, tx)
            # time.sleep(1)
            val.receive()
    except KeyboardInterrupt:
        val.close()
