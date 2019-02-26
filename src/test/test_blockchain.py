from data.blockchain import Blockchain
from data.transaction import Transaction
# create a dummy transaction to be added to blockchain
my_transaction = Transaction(1, 'asfasdfss112', 'Admin', 'sd3lkaslkf2',
                             'registration', 'asdkljfskdj232', 1231201.012, 2181208, 'alice', 'aslkjhwou12121lash23', 'byzantine')


# this function will test whether the transaction has been added to the mempool
def test_add_transaction(transaction):
    pass
