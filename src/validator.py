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

        self.certfile = certfile.replace('~', os.environ['HOME'])
        self.keyfile = keyfile.replace('~', os.environ['HOME'])

        self.receive_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH)
        self.receive_context.load_cert_chain(self.certfile, self.keyfile)

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
        self._load_other_ca(self.capath)
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
                    self.save_new_certfile(data=DATA)
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

    def create_block(self, first, last):
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
        certfile = open(self.certfile, 'rb').read()
        print("Read cafile. Attempting to send to %s:%d" % (addr, port))
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

    def verify_txs_from_merkel_root(self, merkel_root, first, last, validators):
        '''
            Verifies transactions from merkel root

            param: merkel_root: the merkel root created by the block generator from the new block
            param: first: the position of the transaction in the mempool, but in the new block, it is considered the first transaction
            param: last: the position of the transaction in the mempool, but in the new block, it is considered the last transaction
            param: validators: list of validators
        '''
        transactions = []
        for i in range(first, last + 1):
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
        for tx_id in range(0, len(transactions) - 1, 2):
            tx_hash = self.hash_2_txs(
                transactions[tx_id], transactions[tx_id + 1])
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
        hash_return = hashlib.sha256((h1 + h2).encode())
        return hash_return.hexdigest()[::-1]

    def verify_txs(self, block, validators):
        '''
        params - block - the new generated block sent from block generator
        '''
        for tx in block.transactions:
            if tx not in self.mempool:
                return False
        return True


if __name__ == "__main__":
    port = int(input("Enter a port number: "))
    val = Validator(port=port)
    val2 = Validator(port=port + 1)
    # val.create_connections()
    # val.update_blockchain()

    try:
        while True:
            val.receive('insecure')
            val2.send_certificate(addr=val.address[0], port=val.address[1])
    except KeyboardInterrupt:
        val.close()
