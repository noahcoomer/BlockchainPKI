# PKI functionalty tests

import json

import sys
sys.path.append('../')
from network import client
from data_structs import blockchain, block, transaction

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

def register_transaction():
    client_ = client.Client(name="test_client")
    client_.blockchain = create_test_chain()
    tx = client_.pki_register(TEST_KEY_1, "noah", TEST_KEY_1)
    if tx == -1:
        print("Exited with error.")
        return
    print_transaction_info(tx)


def query_transaction():
    client_ = client.Client(name="test_client")
    tx = client_.pki_query("123", "noah")
    if tx == -1:
        print("Exited with error.")
        return
    print_transaction_info(tx)


def create_test_chain():
    chain = blockchain.Blockchain()
    
    inp_1 = { "REGISTER" : { "name": "noah_coomer", "public_key" : TEST_KEY_1 } }
    inp_1 = json.dumps(inp_1)
    tx_1 = transaction.Transaction(inputs=inp_1)
    
    inp_2 = { "REGISTER" : { "name": "lebron_james", "public_key" : TEST_KEY_2 } }
    inp_2 = json.dumps(inp_2)
    tx_2 = transaction.Transaction(inputs=inp_2)

    inp_3 = { "REGISTER" : { "name": "ben_simmons", "public_key" : TEST_KEY_3 } }
    inp_3 = json.dumps(inp_3)
    tx_3 = transaction.Transaction(inputs=inp_3)

    txs = [tx_1, tx_2, tx_3]
    new_block = block.Block(transactions=txs)
    chain.add_block(new_block, "1234")
    return chain
    

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
    register_transaction()


if __name__ == '__main__':
    main()
