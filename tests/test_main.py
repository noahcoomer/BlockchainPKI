import sys
sys.path.append('../')
from src import transaction
from src import blockchain
from src import block
#import pytest
from hashlib import sha256
import json
import requests
import time
import random
from flask import Flask, request

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

    version = 0.1 
    t_id = 123456
    transaction_type="Admin"
    tx_generator_address= sha256( ("1234567".encode())).hexdigest() 
    s = '0 1 2 3 4 5 6 7 8 9 A B C D E F'.split()
    type = ["Admin", "Regular"]

    for i in range(5):
        transactions = transaction.Transaction(
        version = version,
        transaction_type = transaction_type, 
        tx_generator_address = tx_generator_address, 
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


#unit test to see whether we can create a block 
@app.route('/new_block', methods=['GET'])
def new_block():
    blocks = block.Block(
        version = 0,
        id = 0,
        transactions = new_transaction(),
        previous_hash = '1231asdfas',
        block_generator_address = 'asdfs1as',
        block_generation_proof = 'asdfsdwe1211',
        nonce = 1,
        status = 'Accepted',
    )
    
    block_data = json.dumps(
        {"block": blocks.__dict__}, sort_keys=True)
    return block_data


#testing whether we can add blocks to the blockchain  
#can now add multiple blocks in a chain
@app.route('/add_new_block', methods=['GET'])
def add_new_block():
    block_string = ""
    #set the block_number to 0 
    block_number = 0
    #set the version number of the block to 0
    version = 0
    #set the id number to 0 
    id = 0
    
    #set the merkle hash. currently this will be random, will be implemented later
    merkle_hash = random.getrandbits(128)
    #set the block_generator_address, this is the public key of the client or validator 
    block_generator_address = sha256( ("1234567".encode())).hexdigest()
    #set the block_generation_proof will be random for now 
    block_generation_proof = ""
    #set nonce to be zero, but will be randomize later on 
    nonce = 0
    #set the status as propose for now 
    status = 'proposed'
    #set the amount of transactions to be 0 because the genesis block do not have any transactions
    t_counter = 0
    #set the type of statuses 
    type_of_status = ['accepted', 'rejected', 'proposed', 'confirmed']
    #this is to create random hash 
    random_string = [0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f']
    #go through for loop to add the blocks to the chain 
    for i in range(5):
        #add transactions to the block will be 5 each time based on the add_new_transaction() function
        transactions = add_new_transactions()
        #update the amount of transaction in the current block
        t_counter = t_counter + 5
        #update previous hash 
        my_last_block = blockchain.last_block
        previous_hash = my_last_block.hash
        #create a block
        blocks = block.Block(
            version=version,
            id=id,
            transactions=transactions,
            previous_hash=previous_hash,
            block_generator_address=block_generator_address,
            block_generation_proof=block_generation_proof,
            nonce=nonce,
            status=status,
        )


        #create a hash for the current block
        #current_block_hash = blocks.compute_hash()  
        #add the block to the chain  
        blockchain.add_block(blocks, hash(blocks))  
        #update the id for the next block
        id = i + 1
        #update the merkle root for next block
        merkle_hash = random.getrandbits(128) 
        #update the block_generator_address
        block_generator_address = sha256( (str(random_string).encode())).hexdigest() 
        #randomize the random_string array
        shuffle(random_string)
        #randomize the block_generation_proof of the next block
        block_generation_proof = random.randint(1,101)
        #update the nonce value to be random 
        nonce = random.randint(1,101)
        #randomize the status of the next block
        status = type_of_status[random.randint(1,3)]
        #randomize the type_of_status for the next block
        shuffle(type_of_status)
    #go through all the blocks in the chain and add it to block_string to return because flask can't return a list of objects    
    for my_block in blockchain.chain:
        block_data = json.dumps(my_block.__dict__)
        block_string = block_string + '\nblock ' + str(block_number) + ': ' + block_data    
        block_number = block_number + 1
    return block_string


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
