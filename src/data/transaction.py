"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs
and I also added some getters to retrieve information from the transaction 
"""

'''
don't need getters delete them later
'''


class Transaction:

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs):
        self.version = version
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs
        self.outputs = outputs
