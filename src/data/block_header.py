from hashlib import sha256
import time
import json
import datetime as date

class Block:
    def __init__(self, version, id, transactions, previous_hash, merkle_hash, block_generator_address, 
              block_generation_proof, nonce, status, t_counter):
        self.version = version                            # A version number to track software protocol upgrades
        self.id = id                                      # Block index or block height
        self.transactions = transactions                  # Transaction ??
        self.previous_hash = previous_hash                # A reference to the previous (parent) block in the chain
        self.merkle_hash = merkle_hash                    # A hash of the root of the Merkel tree of this block's transactions
        self.timestamp = date.datetime.now()              # Creation time of this block
        self.block_generator_address = block_generator_address  # Public key of the Validator node proposed and broadcast the block
        self.block_generation_proof = block_generation_proof    # Aggregated signature of Block Generator & Validator
        self.nonce = nonce                                # A counter used for Concensus algorithm 
        self.status = status                              # Block status - Proposed/Confirmed/Rejected
        self.t_counter = t_counter                        # Total number of transaction included in this block ???
        self.hash = self.block_hash()                     # The hash of the block header


    # Return the block hash
    def block_hash(self):
        # self.__dict__ is used to store the Block object's attributes into dictionary
        # json.dumps convert the data in the dictionary to JSON form
        block_string = json.dumps(self.__dict__, sort_keys=True) 
        return sha256(block_string.encode()).hexdigest() # Encode the block's data using sha256 hash function

    

        


