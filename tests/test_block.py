import sys
sys.path.append('../')
import pickle
from hashlib import sha256
from src import block, validator, transaction

def new_transaction(input):
    #block_string = json.dumps("123456")
    #proof_string = json.dumps("000234567")

    transactions = transaction.Transaction(
        version=0, 
        transaction_type="Regular", 
        tx_generator_address="123.09.02.23", 
        inputs = input,
        outputs= "",
        lock_time = 12334
    )
    tx_data = pickle.dumps({"transaction" : transactions.__dict__}, sort_keys=True)

    return tx_data

def new_block():
    txs = []
    for i in range(1,10):
        tx = pickle.loads(new_transaction(i))
        tx_hash = sha256((tx.encode())).hexdigest()
        txs.append(tx_hash)

    bl = block.Block(
        version=0.1,
        id=0,
        transactions=txs,
        previous_hash="",
        block_generator_address="123.09.02.24",
        block_generation_proof="None",
        nonce=0, 
        status="Proposed"
    )


def main():
    print("Hello World!")


if __name__ == '__main__':
    main()
