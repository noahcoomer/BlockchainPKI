#This transaction class set up what the user can put into a transaction

class Transaction(object):
    
    #constructor that set up the fields of the transaction 
    
    def __init__(self, version, transactionID, transactionType, TxGeneratorAddress, inputs, outputs):
        self.version = version
        self.transactionID = transactionID
        self.transactionType = transactionType
        self.TxGeneratorAddress = TxGeneratorAddress
        self.inputs = inputs
        self.outputs = outputs

    
    #function: this function returns all the values for the parameters
    
    def returnAll(self):
        return "Version", self.version, " transactionID: ", self.transactionID, "Transaction Type: ", self.transactionType, " Tx Generator Address: " , self.TxGeneratorAddress, "inputs: ", self.inputs, "outputs: ", self.outputs

    #function: this function returns the version of the transaction 
    
    def returnVersion(self):
        return self.version
    
    #function: this function returns the transactionID for transaction 
    
    def returnTransactionID(self):
        return self.transactionID

    #function: this function returns the transaction type for the transaction     
    
    def returnTransactionType(self):
        return self.transactionType
    
    #function: this function returns the transaction generator address for the transaction 
    
    def returnTxGeneratorAddress(self):
        return self.TxGeneratorAddress
    
    #function: this function returns the inputs for the transaction 
    
    def returnInputs(self):
        return self.inputs

    #function: this function returns the outputs for the transaction     
    
    def returnOutputs(self):
        return self.outputs


my_transaction = Transaction("version2", "123121", "Admin", "asl12312", "input1", "output1")
print(my_transaction.returnAll())
    
