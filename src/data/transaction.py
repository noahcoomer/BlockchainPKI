"""
This is the setup for our transaction which contains version, transaction_id, transaction_type, tx_generator_address, inputs, outputs
and I also added some getters to retrieve information from the transaction 
"""


class Transaction:

    # constructor that set up the fields of the transaction

    def __init__(self, version, transaction_id, transaction_type, tx_generator_address, inputs, outputs):
        self.version = version
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs
        self.outputs = outputs

    # this function returns all the values for the parameters

    def return_all(self):
        return "Version", self.version, " transactionID: ", self.transaction_id, "Transaction Type: ", self.transaction_type, " Tx Generator Address: ", self.tx_generator_address, "inputs: ", self.inputs, "outputs: ", self.outputs

    # this function returns the version of the transaction

    def return_version(self):
        return self.version

    # this function returns the transaction_id for transaction

    def return_transaction_id(self):
        return self.transaction_id

    # this function returns the transaction_type for the transaction

    def return_transaction_type(self):
        return self.transaction_type

    # this function returns the tx_generator_address for the transaction

    def return_tx_Generator_Address(self):
        return self.tx_generator_address

    # this function returns the inputs for the transaction

    def return_inputs(self):
        return self.inputs

    # this function returns the outputs for the transaction

    def return_Outputs(self):
        return self.outputs
