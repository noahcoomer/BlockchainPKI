from block import Block
from transaction import Transaction
import json
import time

NOAH_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
                     MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQYD1K9cQt+FLYL4WsiiuDhsE6
                     ut40BWhbkpk0yIfuZX13bg4sQ1aL5AKFswzvEGMM9ACNg6AYh2DOdWDKEkQVGLdD
                     PRqtSCORDX+l74BWxwhYIUPf4nqiKHF0/D5QF5cNvw7aSrbZxtc5AlPHhVziQgVW
                     0NBEFXgdCpJC1BTjWQIDAQAB
                     -----END PUBLIC KEY-----
                  """

DUNGLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
                    AAAAB3NzaC1yc2EAAAADAQABAAABAQCSjebchoY0rncJSbtkbwpTvggKaY/TVObKY
                    NXu55pIuMTMJKdd8xEGOAtJo12kzyrn/7I5F0kAdYwFe/PZJJQZ6v0IgJ+sDwTrvM
                    vP/YU5JQOSkJKu5VEoDd44gv93x4d9636zgXV6X2CGlwcFtr6DvE9wzE7ml1hxGwR
                    9GD7EkUsZMcOF5au5QrygKiN0BJkp7rLeJIzAwoJJf5/7nchxZAgEyJ6VE0WXZp6H
                    Zou8WfA5UZxzG0/0AveCt29cCRiYTJiIQuavp2zxzUblh4Ds/yUcJdWSGansKdWnT
                    v7C6RWl9NXTr4R+JaC8GcmNZLdeetXr8AD2Pym9F1WKMUOf
                       -----END PUBLIC KEY-----
                    """


class Blockchain:
    difficulty = 3
    chain = []
    block_index = 0

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        #self.create_genesis_block()

    def create_genesis_block(self):
        inputs_1 = {"REGISTER": {"name": "Noah Coomer",
                                 "public_key": NOAH_PUBLIC_KEY}}
        inputs_1 = json.dumps(inputs_1)
        outputs_1 = {"REGISTER": {"success": True}}
        outputs_1 = json.dumps(outputs_1)

        inputs_2 = {"REGISTER": {"name": "Dung Le",
                                 "public_key": DUNGLE_PUBLIC_KEY}}
        inputs_2 = json.dumps(inputs_2)
        outputs_2 = {"REGISTER": {"success": True}}
        outputs_2 = json.dumps(outputs_2)

        tx_1 = Transaction(tx_generator_address=NOAH_PUBLIC_KEY,
                           inputs=inputs_1, outputs=outputs_1, lock_time=int(time.time()))

        tx_2 = Transaction(tx_generator_address=DUNGLE_PUBLIC_KEY,
                           inputs=inputs_1, outputs=outputs_1, lock_time=int(time.time()))

        genesis_block = Block(
            version=0.1,
            id=0,
            transactions=[tx_1, tx_2],
            previous_hash="",
            block_generator_address="",
            block_generation_proof="",
            nonce=0,
            status="Confirmed"
        )
        self.chain.append(genesis_block)

    # last_block() returns the last block of the chain
    @property
    def last_block(self):
        return self.chain[-1]

    # Generate a concensus_hash number based on the concensus algorithms
    # This consensus algorithm does not use proof of work
    '''Concensus code go in here...
        def concensus_algorithms(self,...,...)
        ...
        ...
        ...
        return concensus_hash
    '''

    ''' The function to add the new block to the chain after verification that
        the previous_hash of the new block is poiting to or matched with the hash
        of the previous block (parent block)

        + block: a new block mined by the node
        + concensus_hash: the hash of the new block generated by the concensus algorithm.
                          The add_block() also needs to verify that the concensus_hash is match
                          with the block hash by using the is_valid_concensus_hash(...) method'''

    def add_block(self, block, consensus_hash):
        previous_hash_temp = self.last_block.hash

        # Compare the hash of last block andthe previous_hash of the new block
        if previous_hash_temp != block.previous_hash:
            return False

        # if self.is_valid_concensus_hash(block, concensus_hash) != True:
         #   return False

        if block.hash == consensus_hash:
            self.chain.append(block)
            self.block_index = self.block_index + 1
            return True
        else:
            return False

    # Validate the concensus_hash of the block and verify if it satisfies
    #  some require criterias (etc. difficulty)

    def is_valid_concensus_hash(self, block, concensus_hash):
        # The 'difficulty' is put here temporary before finding a new way for constraint
        return (concensus_hash.startswith('0' * Blockchain.difficulty)
                and block.compute_hash() == concensus_hash)

    # Add new transaction into the unconfirmed transactions pool
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    # Mining: add unconfirmed transactions into a block and using the new concensus algorithm to
    # find a new consensus_hash.

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block
        new_block = Block(
            version=last_block.version,
            id=last_block.id + 1,
            transactions=self.unconfirmed_transactions,
            previous_hash=last_block.hash,
            block_generator_address="",
            block_generation_proof="",
            nonce=0,
            status="proposed",
        )

        '''
            ...
            concensus_hash = self.consensus_algorithms(new_block)
            ...
        '''
        concensus_hash = 0
        self.add_block(new_block, concensus_hash)

        self.unconfirmed_transactions = []
        return new_block.id

    # def load_data(self):
    #     with open('blockchain.txt', 'r') as file_load:

    # def save_data(self):
    #     with open('blockchain.txt', 'w') as file_write:
