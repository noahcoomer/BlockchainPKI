import pickle
import time

import sys
sys.path.append('../src/')
from transaction import Transaction
from validator import Validator

if __name__ == '__main__':
    Alice = Validator(port=1234)
    Bob = Validator(name="marshal-mbp.memphis.edu", addr="10.101.7.184",
                    port=1234, bind=False)
    

    tx = pickle.dumps(Transaction(version=0.1, transaction_type='regular', tx_generator_address='0.0.0.0',
                                  inputs='', outputs='', lock_time=1234))
    try:
        while True:
            # Send the serialized object to Bob
            #Alice.message(Bob, tx)
            Alice.receive()
            Alice.message(Bob, tx)
            time.sleep(1)
    except KeyboardInterrupt:
        Alice.close()