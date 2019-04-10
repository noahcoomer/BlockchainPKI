# PKI functionalty tests

import json
from os.path import expanduser

import sys
sys.path.append('../src/')
from block import Block
from client import Client
from blockchain import Blockchain
from transaction import Transaction

TEST_KEY_1 = """-----BEGIN PUBLIC KEY-----
                MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQYD1K9cQt+FLYL4WsiiuDhsE6
                ut40BWhbkpk0yIfuZX13bg4sQ1aL5AKFswzvEGMM9ACNg6AYh2DOdWDKEkQVGLdD
                PRqtSCORDX+l74BWxwhYIUPf4nqiKHF0/D5QF5cNvw7aSrbZxtc5AlPHhVziQgVW
                0NBEFXgdCpJC1BTjWQIDAQAB
                -----END PUBLIC KEY-----
             """

TEST_KEY_2 = """-----BEGIN PUBLIC KEY-----
                MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCXR/KUONEBMAkZez6tQAey26Yn
                uhSMyDd4mrfDZl7Dtz9dhIC0z96QWLHzbFD3euKLfpgqN+ft3be6/Ufg6V0j0TAs
                4mILwgEpalRNP77jcP6OO+AWGqiimh+uGeK5TXlK8b7XvOUkfXmZYkYVzARbbVgW
                8GWnWZu9Q4yT1nST0wIDAQAB
                -----END PUBLIC KEY-----
             """

TEST_KEY_3 = """-----BEGIN PUBLIC KEY-----
                MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCw9Eh1ZBmpWoj9HMMq7JbuR8Vz
                C/sknsE1KFaXIRWMOR6K3U9xwqH5QAbcr9QdI0O+hUvaQLFdzg2mYlP+3Xd1DbFQ
                JfxFmYOBcXckpvNDEn+PZAqXRbT896SQyKXh9aGyNaiSHT726ogKEUO9luFej/DC
                Q2BbkJYRih2bx6/VpwIDAQAB
                -----END PUBLIC KEY-----
             """


#test_key_path = open("C:/Users/ryant/.BlockchainPKI/keys/public.pem","r")
TEST_KEY_PATH = "/Users/noahcoomer/.BlockchainPKI/keys/public.pem"
TEST_KEY_PATH_2 = "/Users/noahcoomer/.BlockchainPKI/keys/public.pem"
TEST_KEY_PATH_3 = "/Users/noahcoomer/test_key.txt"

def register_transaction(name):
    _client = Client()
    #print(TEST_KEY_PATH.read())
    _client.blockchain = create_test_chain()
    tx = _client.pki_register(TEST_KEY_PATH, name, TEST_KEY_PATH)
    try:
        if tx == -1:
            print("Exited with error.")
            return
    except:
        return tx

def query_transaction(query):
    _client = Client()
    _client.blockchain = create_test_chain()
    tx = _client.pki_query(TEST_KEY_PATH, query)
    try:
        if tx == -1:
            print("Exited with error.")
            return
    except:
        return tx

def revoke_transaction():
    _client = Client()
    _client.blockchain = create_test_chain()
    tx = _client.pki_revoke(TEST_KEY_PATH, TEST_KEY_PATH_3)
    try:
        if tx == -1:
            print("Exited with error.")
            return
    except:
        return tx

def validate_transaction():
    _client = Client()
    _client.blockchain = create_test_chain()
    tx = _client.pki_validate(TEST_KEY_PATH, "test_user", TEST_KEY_PATH_3)
    try:
        if tx == -1:
            print("Exited with error.")
            return
    except:
        return tx
    
def update_transaction():
    _client = Client()
    _client.blockchain = create_test_chain()
    tx = _client.pki_update(TEST_KEY_PATH, "test_user", TEST_KEY_PATH_3, TEST_KEY_PATH_2)
    try:
        if tx == -1:
            print("Exited with error.")
            return
    except:
        return tx


def create_test_chain():
    chain = Blockchain()

    inp_1 = {"REGISTER": {"name": "noah_coomer", "public_key": TEST_KEY_1}}
    inp_1 = json.dumps(inp_1)
    tx_1 = Transaction(inputs=inp_1)

    inp_2 = {"REGISTER": {"name": "lebron_james", "public_key": TEST_KEY_2}}
    inp_2 = json.dumps(inp_2)
    tx_2 = Transaction(inputs=inp_2)

    inp_3 = {"REGISTER": {"name": "ben_simmons", "public_key": TEST_KEY_3}}
    inp_3 = json.dumps(inp_3)
    tx_3 = Transaction(inputs=inp_3)

    inp_4 = {"REGISTER": {"name": "test_user", "public_key": open(TEST_KEY_PATH_3, 'r').read()}}
    inp_4 = json.dumps(inp_4)
    tx_4 = Transaction(inputs=inp_4)

    txs = [tx_1, tx_2, tx_3, tx_4]
    new_block = Block(
        transactions=txs, previous_hash=chain.last_block.hash)
    success = chain.add_block(new_block, new_block.hash)
    if success:
        return chain
    else:
        print("Error")

def print_transaction_info(tx):
    print("Transaction Info")
    print("Version: ", tx.version)
    print("ID: ", tx.transaction_id)
    print("Type: ", tx.transaction_type)
    print("Generator Address: ", tx.tx_generator_address)
    print("Inputs: ", tx.inputs)
    print("Outputs: ", tx.outputs)
    print("Lock time: ", tx.lock_time)
    print("Timestamp: ", tx.time_stamp)
    print()

def main():
    print("\nRegistration transaction tests:\n")
    # Passing registration transaction
    tx_reg_pass = register_transaction("unknown")
    print(tx_reg_pass)
    status_dict = json.loads(tx_reg_pass.outputs)
    assert(status_dict["REGISTER"]["success"]) == True
    # Failing registration transaction
    tx_reg_fail = register_transaction("noah_coomer")
    status_dict = json.loads(tx_reg_fail.outputs)
    print(tx_reg_fail)
    assert(status_dict["REGISTER"]["success"]) == False

    print("\nQuery transaction tests:\n")
    # Passing query transaction
    tx_query_pass = query_transaction("lebron_james")
    status_dict = json.loads(tx_query_pass.outputs)
    print(tx_query_pass)
    assert(status_dict["QUERY"]["success"]) == True
    # Failing query transaction
    tx_query_fail = query_transaction("noah")
    status_dict = json.loads(tx_query_fail.outputs)
    print(tx_query_fail)
    assert(status_dict["QUERY"]["success"]) == False

    print("\nRevoke transaction tests:\n")
    tx_revoke_pass = revoke_transaction()
    print(tx_revoke_pass)

    print("\nValidate transaction tests:\n")
    tx_val_pass = validate_transaction()
    print(tx_val_pass)

    print("\nUpdate transaction tests:\n")
    tx_update_pass = update_transaction()
    print(tx_update_pass)

if __name__ == '__main__':
    main()