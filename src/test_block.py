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
    tx_data = transactions.__str__()

    return tx_data

def new_block():

    bl = Block(
        version=0.1,
        id=0,
        previous_hash="",
        block_generator_address="123.09.02.24",
        block_generation_proof="None",
        nonce=0, 
        status="Proposed"
    )

    for i in range(1,10):
        tx = new_transaction(i)
        bl.add_transactions(tx)
    
    print("Hashes of each transaction is :")
    for t in bl.sha256_txs:
        print(t)
    print("Merkel root of the block is ", bl.merkle_root)
    print("Hash of the block is ", bl.hash)
        


def main():
    new_block()


if __name__ == '__main__':
    main()
