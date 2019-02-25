from hashlib import sha256
import time
import json
import datetime as date


class Block:
    def __init__(self, version, id, transactions, previous_hash, merkle_hash, timestamp, block_generator_address,
                 block_generation_proof, nonce, status, t_counter):
        # A version number to track software protocol upgrades
        self.version = version
        self.id = id                                      # Block index or block height
        self.transactions = transactions                  # Transaction ??
        # A reference to the previous (parent) block in the chain
        self.previous_hash = previous_hash
        # A hash of the root of the Merkel tree of this block's transactions.
        self.merkle_hash = merkle_hash
        self.timestamp = timestamp             # Creation time of this block
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
        # The hash of the block header
        self.hash = self.compute_hash()

    # Return the block hash

    def compute_hash(self):
        # self.__dict__ is used to store the Block object's attributes into dictionary
        # json.dumps convert the data in the dictionary to JSON form
        block_string = json.dumps(self.__dict__, sort_keys=True)
        # Encode the block's data using sha256 hash function
        return sha256(block_string.encode()).hexdigest()
