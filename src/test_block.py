import sys
sys.path.append('../')
import pickle
from hashlib import sha256
from block import Block
from validator import Validator
from transaction import Transaction

def new_transaction(input):
    ''' Every time this function is run the transaction + block hashes will changed because of the
    # time_stamp variable, which always change

    # For testing purposes => need to comment out the time_stamp var 
    # in Transaction class + Block class

    '''
    transactions = Transaction(
        version=0, 
        transaction_type="Regular", 
        tx_generator_address="123.09.02.23", 
        inputs = input,
        outputs= "",
        lock_time = 12334
    )
    tx_data = pickle.dumps(transactions)

    return tx_data

def new_block():

    
    vl = Validator()

    for i in range(1,10):
        tx = new_transaction(i)
        vl.add_transaction(tx)
    
    bl = vl.create_block(0,9)
    print("Hashes of each transaction is :")
    for t in bl.sha256_txs:
        print(t)
    print("\nMerkel root of the block is ", bl.merkle_root)
    print("Hash of the block is ", bl.hash)

    test_verification(vl, bl)
        

def test_verification(validator, block):
    print("\nSend block to validator for verification\nReturn: ", end="")
    print(validator.verify_txs(block))


def main():
    new_block()


if __name__ == '__main__':
    main()
