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
        self.transactions = transactions                  # Transaction ??
        # A reference to the previous (parent) block in the chain
        self.previous_hash = previous_hash
        # A hash of the root of the Merkel tree of this block's transactions.
        self.merkle_hash = self.compute_merkle_root()
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

    # Return the merkle root
    def compute_merkle_root(self):
        tx_hashes = []
        for tx in self.transactions:
            tx_hash = hash(tx)
            tx_hashes.append(tx_hash)

        tx_hashes = tuple(tx_hashes)
        return hash(tx_hashes)


    def __hash__(self):
        return hash((self.version, self.id, self.previous_hash, self.merkle_hash,
                     self.block_generator_address, self.block_generation_proof,
                     self.nonce, self.status, self.t_counter,
                     self.timestamp))
