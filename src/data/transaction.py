"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs, lock_time, time_stamp, username, public_key, and proof 
 
"""

'''
need to create two different transaction classes one for admin and one for regular  
email jamal to ask him about what admin_tx and regular_tx and about the fields they take in . Will the admin_tx or regular_tx be hash. Would these transactions have private key. What does outputs request result for 
outputs do we specify the condition to verify the transaction 
we need to have a speecial transaction or the beginning transaction that occurs in the block, and it doesn't have any inputs 
do we need previous transaction hash???

Questions: What kind of data type does registration, query, update, revoke can take in 
what does update, revoke is for , and query?
'''


class Transaction:

    registration = "12312321"
    query = "asdl12"
    update = "3453497a"

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, lock_time, time_stamp):
        self.version = version  # specifies which rules this transaction follows
        self.transaction_id = transaction_id  # transaction sequence #
        self.transaction_type = transaction_type  # Admin/Regular
        # public key of transaction generator-Client or Block validators
        self.tx_generator_address = tx_generator_address
        # self.inputs = inputs  # type of services requested
        # self.outputs = outputs  # request result
        # a unix timestamp or block number-locktime defines the earlier time that a transaction can be added
        self.lock_time = lock_time
        self.time_stamp = time_stamp  # transaction generation time
        # self.username = username  # username for the client
        # self.public_key = public_key  # public key of the client
        # self.proof = proof  # proof

    def admin_tx(self, round_change, leader_selection):
        if leader_selection == True:
            round_change = False
        else:
            round_change = True

    def regular_tx(self, registration, query, update, revoke):
        pass

    def output(self):
        pass
