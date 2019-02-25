"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs
and I also added some getters to retrieve information from the transaction 
"""


class Transaction:

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, proof):
        self.version = version
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs
        self.outputs = outputs
        self.lock_time = lock_time
        self.time_stamp = time_stamp
        self.username = username
        self.public_key = public_key
        self.proof = proof
