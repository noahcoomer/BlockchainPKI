import json

from test_pki import register_transaction, create_test_chain


def transaction_eq_test():
    tx_1 = register_transaction("Noah")
    tx_2 = register_transaction("Noah")
    return (tx_1, tx_2)


def block_eq_test():
    blockchain = create_test_chain()
    block_1 = blockchain.last_block
    block_2 = blockchain.last_block
    return (block_1, block_2)


def main():
    txns = transaction_eq_test()
    assert(txns[0] == txns[1])
    #print(txns[0].transaction_id)
    #print(txns[1].transaction_id)

    blocks = block_eq_test()
    assert(blocks[0] == blocks[1])


if __name__ == '__main__':
    main()