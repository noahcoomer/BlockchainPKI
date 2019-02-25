"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, and proof 
 
"""


class Transaction:

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, proof):
        self.version = version  # specifies which rules this transaction follows
        self.transaction_id = transaction_id  # transaction sequence #
        self.transaction_type = transaction_type  # Admin/Regular
        # public key of ttransaction generator-Client or Block validators
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs  # type of services requested
        self.outputs = outputs  # request result
        # a unix timestamp or block number-locktime defines the earlier time that a transaction can be added
        self.lock_time = lock_time
        self.time_stamp = time_stamp  # transaction generation time
        self.username = username  # username for the client
        self.public_key = public_key  # public key of the client
        self.proof = proof  # proof
