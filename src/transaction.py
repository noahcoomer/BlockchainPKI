import time
import hashlib
import pickle

class Transaction:
    def __init__(self, version=0.1, transaction_type=None, tx_generator_address=None,
                 inputs=None, outputs=None, lock_time=None):
        self.version = version  # specifies which rules this transaction follows
        # transaction sequence #
        self.transaction_type = transaction_type  # Admin/Regular
        # public key of transaction generator-Client or Block validators
        self.tx_generator_address = tx_generator_address
        self.inputs = inputs  # type of services requested
        self.outputs = outputs  # request result
        # a unix timestamp or block number-locktime defines the earlier time that a transaction can be added
        self.lock_time = lock_time
        self.time_stamp = int(time.time())  # transaction generation time
        self.transaction_id = self.compute_hash()
        self.status = "Open"  # Open/Pending/Complete

    def admin_tx(self, round_change, leader_selection):
        if leader_selection == True:
            round_change = False
        else:
            round_change = True

    def regular_tx(self, registration, query, update, revoke):
        pass

    def output(self):
        pass

    def compute_hash(self):
        tx_info = str(pickle.dumps(self))
        hash_256 = hashlib.sha256(tx_info.encode()).hexdigest()
        return hash_256

    def __eq__(self, other):
        return self.compute_hash() == other.compute_hash()

    def __str__(self):
        s = "<Transaction>\n"
        for attr, value in self.__dict__.items():
            s += "\t --%s: %s\n" % (attr, value or "None")
        s += "</Transaction>"
        return s
