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
        vl = Validator()

        for i in range(0,2):
                bl = test_block.new_block(i) # Create new block by calling new_block() method in test_block.py
                rt = vl.blockchain.add_block(bl, bl.hash)
                print("validation: ", rt)
        
        #print(blockchain)
        blockC = vl.update_blockchain()
        print("Blockchain's length = ", len(blockC.chain))
        print(blockC.last_block)

        # Test update_blockchain() in client
        cl = Client()
        cl.blockchain = blockC
        bl_test = test_block.new_block(10)
        cl.update_blockchain(bl_test)
        print("Blockchain's length = ", len(blockC.chain))
        print(blockC.last_block)

create_blockchain()

