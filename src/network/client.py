"""
    Generate public-private key pairs
"""

import socket


class Client(object):
    blockchain = []
    sock = None
    port = 1234
    host = '10.101.99.92'

    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_network(self.ip, self.port)
        self.blockchain = [] #update_blockchain()
        

    # connect to the p2p network
    def connect_to_network(self, host, port):
        try:
            self.sock.connect((host, port))
            print("Successfully connected to the network")
        except Exception as e:
            print(e)


    # update the blockchain to be current
    def update_blockchain(self):
        return 1


example = Client()
    

        
