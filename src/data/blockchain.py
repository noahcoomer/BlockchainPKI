from block_header import Block

class Blockchain:

    def __init__(self):
        self.unconfirm_transactions = [] 
        self.chain = []
        self.create_genesis_block()

    
    def create_genesis_block(self):
        genesis_block = Block(
            version = 0, 
            id = 0, 
            transactions = [], 
            previous_hash = "0",
            merkle_hash="",
            block_generator_address="", 
            block_generation_proof="",
            nonce=0,
            status="confirmed",
            t_counter=0
        )

        self.chain.append(genesis_block)


    @property
    def last_block(self):
        return self.chain[-1]

    def add_block():

    # Validate the hash of the block and some criterias
    def is_valid_proof():