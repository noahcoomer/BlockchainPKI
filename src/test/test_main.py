import sys
sys.path.append('../')
#import pytest
from hashlib import sha256
import json
import requests
import time
from flask import Flask, request
from data import transaction
from data import blockchain
from data import block
from random import shuffle

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
        time_stamp = time.time(),
        lock_time = 12334
    )
    tx_data = json.dumps({"transaction" : transactions.__dict__}, sort_keys=True)

    return tx_data

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
