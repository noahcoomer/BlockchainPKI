import sys
sys.path.append('../')
#import pytest
from hashlib import sha256
import json
import requests
import time
import random
from flask import Flask, request
from data import transaction
from data import blockchain
from data import block
from random import shuffle


'''
testing: test for transaction, block, and blockchain 
'''

app = Flask(__name__)

# the node's copy of blockchain
blockchain = blockchain.Blockchain()

############################# Connection Test ###############################
@app.route('/', methods=['POST'])
def hello_world():
    return 'Hello, World!'


@app.route('/hello')
def hello():
    return 'Hello, World'
################################################################



@app.route('/new_transaction', methods=['GET'])
def new_transaction():
    #block_string = json.dumps("123456")
    #proof_string = json.dumps("000234567")

    transactions = transaction.Transaction(
        version=0,
        transaction_id=123456,
        transaction_type="test",
        tx_generator_address="1234567",
        time_stamp=time.time(),
       # public_key=sha256((block_string.encode()).hexdigest()),
       # proof=sha256((proof_string.encode()).hexdigest()),
        #inputs="\tPrevious tx: \n\t Index: 0 \n\t scriptSig: ",
        #outputs="\tValue: 5000000000 \n\t scriptPubKey:",
        lock_time=12334
    )
    tx_data = json.dumps(
        {"transaction": transactions.__dict__}, sort_keys=True)

    return tx_data


#unit test to see whether we can create a block 
@app.route('/new_block', methods=['GET'])
def new_block():
    blocks = block.Block(
        version = 0,
        id = 0,
        transactions = new_transaction(),
        previous_hash = '1231asdfas',
        merkle_hash = 'asdfas112',
        timestamp = time.time(),
        block_generator_address = 'asdfs1as',
        block_generation_proof = 'asdfsdwe1211',
        nonce = 1,
        status = 'accepted',
        t_counter = 1,
    )
    
    block_data = json.dumps(
        {"block": blocks.__dict__}, sort_keys=True)
    return block_data


#testing whether we can add a new block to the blockchain  
@app.route('/add_new_block', methods=['GET'])
def add_new_block():
    block_string = ""
    version = 0
    id = 0
    transactions = new_transaction()
    previous_hash = "" #no link to the previous block, currently this is a random hash, will be implemented later  
    merkle_hash = "" #currently this is a random hash, will be implemented later
    block_generator_address = sha256( ("1234567".encode())).hexdigest()
    block_generation_proof = ""
    time_stamp = time.time()
    nonce = 0
    status = ''
    t_counter = 1
    type_of_status = ['accepted', 'rejected', 'proposed', 'confirmed']
    random_string = [0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f']
    for i in range(5):
        blocks = block.Block(
            version,
            id,
            transactions,
            previous_hash,
            merkle_hash,
            time_stamp,
            block_generator_address,
            block_generation_proof,
            nonce,
            status,
            t_counter
        )
        block_data = json.dumps({"block" : blocks.__dict__}, sort_keys=True)
        blockchain.add_block(block_data, 'proof of work')
        id = i + 1
        previous_hash = random.getrandbits(128)
        merkle_hash = random.getrandbits(128)
        block_generator_address = sha256( (str(random_string).encode())).hexdigest()
        shuffle(random_string)
        block_generation_proof = random.randint(1,101)
        nonce = random.randint(1,101)
        status = type_of_status[random.randint(1,3)]
        shuffle(type_of_status)
        time_stamp = time.time()
        t_counter = i + 1
        # for a_block in blockchain.chain:
        #     block_data = json.dumps(a_block.__dict__)
        #     block_string = block_string + block_data
        block_chain_data = json.dumps(blockchain.chain.__dict__, sort_keys=True) 
    return block_chain_data


# endpoint to query unconfirmed transactions
@app.route('/add_new_transactions', methods=['GET'])
def add_new_transactions():

    unconfirmed_transactions_test = blockchain.unconfirmed_transactions

    version = 0 
    t_id = 123456
    transaction_type="Admin"
    tx_generator_address= sha256( ("1234567".encode())).hexdigest() 
    s = '0 1 2 3 4 5 6 7 8 9 A B C D E F'.split()
    type = ["Admin", "Regular"]

    for i in range(5):
        transactions = transaction.Transaction(
        version, 
        t_id, 
        transaction_type, 
        tx_generator_address, 
        time_stamp = time.time(),
        lock_time = 12334
    )
        tx_data = json.dumps({"transaction" : transactions.__dict__}, sort_keys=True)
        blockchain.add_new_transaction(tx_data)
        t_id = t_id + i

        shuffle(type)
        transaction_type = type[0] 

        tx_generator_address = sha256( (str(s).encode())).hexdigest() 
        shuffle(s)
    
    tx_data = json.dumps( unconfirmed_transactions_test, sort_keys=True)

    return tx_data


@app.route('/genesis_block', methods=['GET'])
def get_genesis():
    #chain_test = blockchain.chain
    blockchain.create_genesis_block()
    chain_test = blockchain.last_block

    b_data = json.dumps(chain_test.__dict__, sort_keys=True)

    return b_data 


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)





app.run(debug=True, port=8000)
