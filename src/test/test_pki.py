# PKI functionalty tests

import sys
sys.path.append('../')
from network import client

def register_transaction():
    client_ = client.Client(name="test_client")
    tx = client_.pki_register("123", "noah", "123")
    print_transaction_info(tx)


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
