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
import random
app = Flask(__name__)

# the node's copy of blockchain
blockchain = blockchain.Blockchain()


@app.route('/', methods=['POST'])
def hello_world():
    return 'Hello, World!'

@app.route('/hello')
def hello():
    return 'Hello, World'

@app.route('/new_transaction', methods=['GET'])
def new_transaction():
    block_string = json.dumps("123456")
    proof_string = json.dumps("000234567")

    transactions = transaction.Transaction(
        version=0, 
        transaction_id=123456, 
        transaction_type="test", 
        tx_generator_address="1234567", 
        time_stamp = time.time(),
        public_key = sha256((block_string.encode()).hexdigest()),
        proof = sha256((proof_string.encode()).hexdigest()),
        inputs="\tPrevious tx: \n\t Index: 0 \n\t scriptSig: ", 
        outputs="\tValue: 5000000000 \n\t scriptPubKey:",
        lock_time = 12334
    )
    tx_data = json.dumps({"transaction" : transactions.__dict__}, sort_keys=True)
    #print(tx_data)
    ''' for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data) '''

    return tx_data

@app.route('/add_new_transactions', methods=['GET'])
def add_new_transactions():

    version=0, 
    transaction_id=123456, 
    transaction_type="test", 
    tx_generator_address="1234567", 
    inputs="\tPrevious tx: \n\t Index: 0 \n\t scriptSig: ", 
    outputs="\tValue: 5000000000 \n\t scriptPubKey:"

    for i in range(5):
        transactions = transaction.Transaction(
        version, 
        transaction_id, 
        transaction_type, 
        tx_generator_address, 
        inputs, 
        outputs
    )

        blockchain.add_new_transaction(transactions)
        transaction_id = transaction_id + i
        tx_generator_address = randomString(8)

    #tx_data = 

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


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


app.run(debug=True, port=8000)
