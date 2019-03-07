"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, and proof 
 
"""

'''
need to create two different transaction classes one for admin and one for regular  
email jamal to ask him about what admin_tx and regular_tx and about the fields they take in . Will the admin_tx or regular_tx be hash. Would these transactions have private key. What does outputs request result for 
outputs do we specify the condition to verify the transaction 
we need to have a speecial transaction or the beginning transaction that occurs in the block, and it doesn't have any inputs 
do we need previous transaction hash???

'''


class Transaction:

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, proof):
        self.version = version  # specifies which rules this transaction follows
        self.transaction_id = transaction_id  # transaction sequence #
        self.transaction_type = transaction_type  # Admin/Regular
        # public key of transaction generator-Client or Block validators
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs  # type of services requested
        self.outputs = outputs  # request result
        # a unix timestamp or block number-locktime defines the earlier time that a transaction can be added
        self.lock_time = lock_time
        self.time_stamp = time_stamp  # transaction generation time
        self.username = username  # username for the client
        self.public_key = public_key  # public key of the client
        self.proof = proof  # proof


'''
this class defines the admin transaction. this class inherits from Transaction 
'''


class admin_tx(Transaction):
    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, proof, round_change, leader_selection):
        Transaction.__init__(self, version, transaction_id, transaction_type, tx_generator_address,
                             inputs, outputs, lock_time, time_stamp, username, public_key, proof)
        self.round_change = round_change #
        self.leader_selection = leader_selection


'''
this class defines the regular transaction, this class inherits from Transaction 
'''


class regular_tx(Transaction):
    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, proof, registration, query, update, revoke):
        Transaction.__init__(self, version, transaction_id, transaction_type, tx_generator_address,
                             inputs, outputs, lock_time, time_stamp, username, public_key, proof)
        self.registration = registration
        self.query = query
        self.update = update
        self.revoke = revoke
