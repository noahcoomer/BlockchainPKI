import sys
sys.path.append('../')

import json
#import requests
import time
#from flask import Flask, request
from data import transaction
from data import blockchain
from data import block









''' app = Flask(__name__)
# the node's copy of blockchain
blockchain = blockchain.Blockchain()
@app.route('/', methods=['POST'])
def hello_world():
    return 'Hello, World!'
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404
    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)
    return "Success", 201
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
app.run(debug=True, port=8000) '''
