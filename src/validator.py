from random import randint
from transaction import Transaction
from block import Block
from blockchain import Blockchain

import os
import ssl
import time
import errno
import socket
import string
import random
import hashlib
import binascii
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

        # Blockchain object
        self.blockchain = Blockchain()

        if bind:
            self.cafile = cafile.replace('~', os.environ['HOME'])
            self.keyfile = keyfile.replace('~', os.environ['HOME'])
            self.validators_capath = validators_capath.replace(
                '~', os.environ['HOME'])

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
            self.net.listen(INCONN_THRESH)  # Listen for connections
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
            print("Listening on %s:%d" % self.address)

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

    def save_new_certificate(self, data):
        '''
            Saves a new certificate that was received 
            from a Validator

            :param bytearray data: the certificate
        '''
        # Create a random filename of length 15
        filename = ''.join(random.choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(15))
        # Save the certificate and remake the context with the new certificate included
        path = os.path.join(
            self.validators_capath, "%s.pem" % filename)
        for p in os.listdir(self.validators_capath):
            if p.endswith('.pem'):
                p = os.path.join(self.validators_capath, p)
                content = open(p, 'rb').read()
                if content == data:
                    print("This certificate already exists at %s" % p)
                    return
        with open(path, 'wb') as f:
            f.write(data)
        print("New CA added at %s" % path)
        self._load_other_ca(self.validators_capath)
        print("Reloaded Validator CAs")

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
                    self.save_new_certificate(data=DATA)
                # Deserialize the entire object when data reception has ended
                try:
                    data = pickle.loads(DATA)
                except pickle.UnpicklingError:
                    # The data received most likely wasn't a Transaction
                    data = DATA.decode()

                if type(data) == Transaction:
                    # Add transaction to the pool
                    self.add_transaction(data)
                    # broadcast to network
                    self.broadcast(data)
                    end_time = int(time.time())

                    # Probably need to add a leader flag here
                    if (end_time - start_time) >= 10:
                        start_time = int(time.time())
                        print("Call Round Robin to chose the leader")
                        self.create_block(self.mempool)
                    elif len(self.mempool) >= 10:
                        start_time = int(time.time())
                        self.create_block(self.mempool[:10])
                elif type(data) == Block:
                    print("Call verification/consensus function to vote on Block")
                else:
                    print("Data received was not of type Transaction or Block, but of type %s: \n%s\n" % (
                        type(data), data))
                # return decoded_transaction
        except socket.timeout:
            pass


    def add_transaction(self, tx):
        '''
            Receive incoming transactions and add to mempool
        '''
        transaction = pickle.loads(tx)
        if transaction.output == 'YES':
            pass
        elif transaction.output == 'NO':
            pass
        else:
            transaction = str(pickle.dumps(transaction))
            if transaction not in self.mempool:
                self.mempool.append(transaction)
                


    def create_block(self, first, last ):
        block_tx_pool = []

        for tx in range(first, last):
            block_tx_pool.append(self.mempool[tx])

        bl = Block(
            version=0.1,
            id=len("Blockchain.block_index"),
            transaction=block_tx_pool,
            previous_hash="Blockchain.last_block(Blockchain)",
            block_generator_address=self.address,
            block_generation_proof=self.cafile,
            nonce=0, 
            status="Proposed"
        )

        return bl

        

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

    def send_certificate(self, addr, port):
        '''
            Sends the certificate to addr:port through 
            standard, unencrypted TCP

            :param str addr: the ipv4 address to send to
            :param int port: the port number to send to
        '''
        cafile = open(self.cafile, 'rb').read()
        print("Read cafile. Attempting to send to %s:%d" % (addr, port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((addr, port))
                # Alert receiver that you want to send a certificate
                s.send(b'/cert')
                s.sendall(cafile)  # Send the certificate
            except OSError as e:
                print(e)
            except socket.timeout as e:
                print(e)

    def broadcast(self, message):
        '''
            Broadcast a message to every other validator that is connected to this node
        '''
        for val in self.connections:
            self.message(val, message)

    def create_connections(self):
        '''
            Create the connection objects from the validators info file and store them as a triple
            arr[0] = hostname, arr[1] = ip, int(arr[2]) = port 
        '''
        f = open('../validators.txt', 'r')
        for line in f:
            arr = line.split(' ')
            if self.name == arr[0] and self.address == (arr[1], int(arr[2])):
                continue
            else:
                val = Validator(name=arr[0], addr=arr[1],
                                port=int(arr[2]), bind=False)
                self.connections.append(val)
        f.close()

    def create_block(self, transactions):
        # for tx in transactions:

        block = Block(id=len(self.blockchain), transactions=transactions,
                      previous_hash=self.blockchain.last_block.hash)
        self.broadcast(block)

    def verify_txs_from_merkel_root(self, merkel_root, first, last, validators):
        '''
            Verifies transactions from merkel root 

            param: merkel_root: the merkel root created by the block generator from the new block
            param: first: the position of the transaction in the mempool, but in the new block, it is considered the first transaction
            param: last: the position of the transaction in the mempool, but in the new block, it is considered the last transaction
            param: validators: list of validators
        '''
        transactions = []
        for i in range(first, last+1):
            transactions.append(self.mempool[i])

        sha256_txs = self.hash_tx(transactions)
        calculated_merkle_root = self.compute_merkle_root(sha256_txs)

    def hash_tx(self, transaction):
        '''
            Returns a list of hashed transactions
        '''
        sha256_txs = []
        # A hash of the root of the Merkel tree of this block's transactions.
        for tx in transaction:
            tx_hash = tx.compute_hash()
            sha256_txs.append(tx_hash)
        return sha256_txs

    def compute_merkle_root(self, transactions):
        # If the length of the list is 1 then return the final hash
        if len(transactions) == 1:
            return transactions[0]

        new_tx_hashes = []
        for tx_id in range(0, len(transactions)-1, 2):
            tx_hash = self.hash_2_txs(
                transactions[tx_id], transactions[tx_id+1])
            new_tx_hashes.append(tx_hash)

        # if the number of transactions is odd then hash the last item twice
        if len(transactions % 2 == 1):
            tx_hash = self.hash_2_txs(transactions[-1], transactions[-1])
            new_tx_hashes.append(tx_hash)

        return self.compute_merkle_root(new_tx_hashes)

    def hash_2_txs(self, hash1, hash2):
        '''
            Returns the hash of two hashes
        '''
        # Reverse inputs before and after hashing because of the big-edian and little-endian problem
        h1 = hash1.hexdigest()[::-1]
        h2 = hash2.hexdigest()[::-1]
        hash_return = hashlib.sha256((h1+h2).encode())
        return hash_return.hexdigest()[::-1]

    def verify_txs(self, block, validators):
        '''
        params - block - the new generated block sent from block generator
        '''
        for tx in block.transactions:
            if tx not in self.mempool:
                return False
        return True
        
     def close(self):
        '''
            Closes a Validator and its net. Ignores Validators whose nets are not bound.
        '''
        if self.bound:
            self.net.close()
        

if __name__ == "__main__":
    port = int(input("Enter a port number: "))
    val = Validator(port=port)
    val2 = Validator(port=port+1)
    # val.create_connections()
    # val.update_blockchain()

    try:
        while True:
            val.receive('insecure')
            val2.send_certificate(addr=val.address[0], port=val.address[1])
    except KeyboardInterrupt:
        val.close()
