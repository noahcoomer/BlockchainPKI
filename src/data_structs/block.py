import hashlib
from hashlib import sha256
import time
import json
import datetime as date
import time



class Block:
    def __init__(self, version=0.1, id=None, transactions=[], previous_hash=None, block_generator_address=None,
                 block_generation_proof=None, nonce=None, status=None):
        # A version number to track software protocol upgrades
        self.version = version
        self.id = id                                      # Block index or block height
        self.transactions = transactions                # Transaction pool passed from the validator
        # A reference to the previous (parent) block in the chain
        self.previous_hash = previous_hash
        # A hash of the root of the Merkel tree of this block's transactions.
        self.merkle_root = self.compute_merkle_root(self.transactions)
        # Public key of the Validator node proposed and broadcast the block
        self.block_generator_address = block_generator_address
        # Aggregated signature of Block Generator & Validator
        self.block_generation_proof = block_generation_proof
        # A counter used for Concensus algorithm. The value of nonce will keep changing until
        # the node generates a block that satisfied with the Concensus
        self.nonce = nonce
        # Block status - Proposed/Confirmed/Rejected/"Accepted??"
        self.status = status
        # Total number of transaction included in this block ???
        self.t_counter = len(transactions)
        self.timestamp = int(time.time())            # Creation time of this block
        # The hash of the block header
        self.hash = hash(self)

    
    # Return the root of the hash tree of all the transactions in the block's transaction pool (Recursive Function)
    # Assuming each transaction in the transaction pool was HASHed in the Validator class (Ex: encode with binascii.hexlify(b'Blaah'))
    # The number of the transactions hashes in the pool has to be even. 
    # If the number is odd, then hash the last item of the list twice
    def compute_merkle_root(self, transactions):
        # If the length of the list is 1 then return the final hash
        if len(transactions) == 1:
            return transactions[0]

        new_tx_hashes = []

        for tx_id in range(0, len(transactions)-1, 2):  # for(t_id = 0, t_id < len(transactions) - 1, t_id = t_id + 2)
            
            tx_hash = self.hash_2_txs(transactions[tx_id], transactions[tx_id+1])
            new_tx_hashes.append(tx_hash)

        # if the number of transactions is odd then hash the last item twice
        if len(transactions % 2 == 1):
            tx_hash = self.hash_2_txs(transactions[-1], transactions[-1])
            new_tx_hashes.append(tx_hash)

        return self.compute_merkle_root(new_tx_hashes)


        #tx_hashes = tuple(tx_hashes)
        #return hash(new_tx_hashes)

    # Hash two hashes together -> return 1 final hash
    def hash_2_txs(self, hash1, hash2):
        # Reverse inputs before and after hashing because of the big-edian and little-endian problem
        h1 = hash1.hexdigest()[::-1]
        h2 = hash2.hexdigest()[::-1]
        hash_return = hashlib.sha256((h1+h2).encode())

        return hash_return.hexdigest()[::-1]


    def __hash__(self): # SHA256() ???
        return hash((self.version, self.id, self.previous_hash, self.merkle_root,
                     self.block_generator_address, self.block_generation_proof,
                     self.nonce, self.status, self.t_counter, self.timestamp))

    
    def __eq__(self, other):
        return hash(self) == hash(other)
