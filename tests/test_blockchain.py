from hashlib import sha256

import sys
import pickle

sys.path.append('../src/')
from block import Block
from validator import Validator
from transaction import Transaction
from blockchain import Blockchain
from client import Client
import test_block

# # create a dummy transaction to be added to blockchain
# my_transaction = transaction.Transaction(1, 'asfasdfss112', 'Admin', 'sd3lkaslkf2',
#                              1231201.012, 2181208)


# # this function will test whether the transaction has been added to the mempool
# # to execute this test, run pytest in terminal
# def test_add_transaction():
#     my_blockchain = blockchain.Blockchain()  # first, initiate a blockchain object
#     # add it to the mempool
#     my_blockchain.add_new_transaction(my_transaction)
#     # loop through all the transactions and check to see if that transaction is in the pool
#     for transaction in my_blockchain.unconfirmed_transactions:
#         # check whether our transaction is in the list of uncofirmed transaction
#         assert transaction == my_transaction

def create_blockchain():
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++VALIDATOR UPDATE_BLOCKCHAIN() TEST++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        vl = Validator()

        for i in range(0,4):
                test_block.new_block(i, vl) # Create new block by calling new_block() method in test_block.py and pass validator as parameter
                rt = vl.add_block()
                #print("validation: ", rt)
        
        #print(blockchain)
        blockC = vl.update_blockchain()
        print("\nLOAD FILE!\nBlockchain's length = ", len(blockC.chain))
        print("The last_block of the Blockchain: ")
        print(blockC.last_block)

        # Test update_blockchain() in client
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++CLIENT UPDATE_BLOCKCHAIN() TEST++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        cl = Client()
        bl_test = test_block.new_block(10, vl) # Create a new block
        cl.update_blockchain(bl_test) # Update a new block to client's blockchain
        print("Blockchain's length = ", len(cl.blockchain.chain))

        # Load the file again and check if the new block has been added to the file
        try:
                with open("blockchain.txt", "rb") as file1:
                        bl = pickle.load(file1)

                print("\nLOAD FILE!... HASH OF NEW BLOCK is: ", bl.last_block.hash)
                
        except:
            print("Update Failed!")

create_blockchain()

