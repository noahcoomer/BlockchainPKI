from hashlib import sha256

import sys
import pickle

sys.path.append('../src/')
from block import Block
from validator import Validator
from transaction import Transaction
from client import Client
import test_block

def test_validate_transaction_in_block():
    cl = Client()
    bl = Block()
    vl = Validator()

    bl = test_block.new_block(10,vl)
    cl.tx = bl.transactions[1]
    print("Check client's transaction - hash : ", cl.tx.compute_hash(), ": ")
    print("If client's transaction is in the inbound block, then return True, else return False")
    print("============================")
    print("Return Result: ", cl.validate_transaction_in_block(bl))

def main():
    test_validate_transaction_in_block()


if __name__ == '__main__':
    main()


