from data.blockchain import Blockchain
from data.transaction import Transaction

# create a dummy transaction to be added to blockchain
my_transaction = Transaction(1, 'asfasdfss112', 'Admin', 'sd3lkaslkf2',
                             'registration', 'asdkljfskdj232', 1231201.012, 2181208, 'alice', 'aslkjhwou12121lash23', 'byzantine')


# this function will test whether the transaction has been added to the mempool
# to execute this test, run pytest in terminal
def test_add_transaction():
    my_blockchain = Blockchain()  # first, initiate a blockchain object
    # add it to the mempool
    my_blockchain.add_new_transaction(my_transaction)
    # loop through all the transactions and check to see if that transaction is in the pool
    for transaction in my_blockchain.unconfirmed_transactions:
        # check whether our transaction is in the list of uncofirmed transaction
        assert transaction == my_transaction
