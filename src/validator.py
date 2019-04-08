from random import choice
from string import ascii_uppercase, ascii_lowercase, digits

from node import Node
from block import Block
from blockchain import Blockchain
from transaction import Transaction

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
        self.blockchain = Blockchain()
        # Buffer to store connection objects
        self.connections = list()

        self.certfile = certfile.replace('~', os.environ['HOME'])
        self.keyfile = keyfile.replace('~', os.environ['HOME'])

        self.receive_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH)
        self.receive_context.load_cert_chain(self.certfile, self.keyfile)

    def create_connections(self):
        pass

    def save_new_certfile(self, data):
        '''
            Saves a new certificate that was received from a Validator

            :param bytearray data: The certificate file
        '''
        newfilename = lambda namelength: ''.join(
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
            raise Exception("The net must be initialized and listening for connections")

    def broadcast(self, tx):
        '''
            Broadcast a message to every other validator that is connected to this node
        '''
        i = 0
        for addr in self.connections:
            ip, port = addr
            name = "val-" + str(i)
            receiver = Validator(hostname=name, addr=ip, port=port)
            self.message(receiver, tx)

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
                print("Received data from %s:%d: %s" %
                      (addr[0], addr[1], decoded_message))
                if type(decoded_message) == Transaction:
                    # Add transaction to the pool
                    self.add_transaction(decoded_message)
                    # broadcast to network
                    self.broadcast(decoded_message)
                    end_time = int(time.time())

                    # Probably need to add a leader flag here
                    if (end_time - start_time) >= 10:
                        start_time = int(time.time())
                        last = None
                        print("Call Round Robin to chose the leader")
                        self.create_block(self.mempool, last)
                    elif len(self.mempool) >= 10:
                        start_time = int(time.time())
                        last = None
                        self.create_block(self.mempool[:10], last)
                elif type(data) == Block:
                    print("Call verification/consensus function to vote on Block")
                else:
                    print("Data received was not of type Transaction or Block, but of type %s: \n%s\n" % (
                        type(data), data))
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
                tx.status = "Open"
                self.mempool.append(tx)

    def create_block(self, first, last):
        block_tx_pool = []
        for tx in range(first, last):
            block_tx_pool.append(self.mempool[tx])
        return Block(
            version=0.1,
            id=len("Blockchain.block_index"),
            transactions=block_tx_pool,
            previous_hash=self.blockchain.last_block.hash,
            block_generator_address=self.address,
            block_generation_proof=self.certfile,
            nonce=0,
            status="Proposed"
        )
    
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

    def verify_txs(self, block, validators):
        '''
            Verify transactions 

            param: Block block: the new generated block sent from block generator
        '''
        for tx in block.transactions:
            if tx not in self.mempool:
                return False
        return True
        
if __name__ == "__main__":
    port = int(input("Enter a port number: "))
    val = Validator(hostname="localhost", port=port)
    val2 = Validator(hostname="localhost", port=port+1)

    try:
        while True:
            val.receive('insecure')
            val2.send_certificate(addr=val.address[0], port=val.address[1])
    except KeyboardInterrupt:
        val.close()
