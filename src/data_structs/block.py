from hashlib import sha256
import time
import json
import datetime as date
import time

class Block:
    def __init__(self, version=0.1, id=None, transactions=[], previous_hash=None, merkle_hash=None,  block_generator_address=None,
                 block_generation_proof=None, nonce=None, status=None, t_counter=None, timestamp=int(time.time())):
        # A version number to track software protocol upgrades
        self.version = version
        self.id = id                                      # Block index or block height
        self.transactions = transactions                  # Transaction ??
        # A reference to the previous (parent) block in the chain
        self.previous_hash = previous_hash
        # A hash of the root of the Merkel tree of this block's transactions.
        self.merkle_hash = merkle_hash
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
        self.t_counter = t_counter
        self.timestamp = int(time.time())            # Creation time of this block
        # The hash of the block header
        self.hash = hash(self)

    # Return the block hash

    def compute_hash(self):
        # self.__dict__ is used to store the Block object's attributes into dictionary
        # json.dumps convert the data in the dictionary to JSON form
        block_string = json.dumps(self.__dict__, sort_keys=True)
        # Encode the block's data using sha256 hash function
        return sha256(block_string.encode()).hexdigest()


    def __hash__(self):
        tx_hashes = []
        for tx in self.transactions:
            tx_hash = hash(tx)
            tx_hashes.append(tx_hash)

        tx_hashes = tuple(tx_hashes)
        return hash((self.version, self.id, self.previous_hash, self.merkle_hash,
                     self.block_generator_address, self.block_generation_proof,
                     self.nonce, hash(tx_hashes), self.status, self.t_counter,
                     self.timestamp))
