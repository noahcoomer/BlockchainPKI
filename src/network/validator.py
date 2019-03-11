"""
    Listen for transactions on the network and validate them
"""
import socket
from Crypto.Signature import PKCS1_v1_5
#from data import transaction
import client as client


class Validator(object):
    def __init__(self):

        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("Socket cannot be created")

        host = ''#socket.gethostname()
        port = 9058
        self.serversocket.bind((host,port))
        self.serversocket.listen(5)
        print('Validator started and listening for transactions')

    def listen(self):
        (clientsocket, address) = self.serversocket.accept()
        while True:
            print("Connection found")
            try:
                data = clientsocket.recv(1024).decode("utf-8")
            finally:
                pass

    def sign_message(self, private_key, message):
        signer = PKCS1_v1_5.new(private_key)
        sig = signer.sign(message)
        return sig
        
    def verify_message(self, public_key, message):
        verifier = PKCS1_v1_5.new(public_key)
        verified = verifier.verify(message,sign_message())
        assert verified, "Signature Verification Failed"

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

def main():
    #validator = Validator()
    #validator.listen()
    #mytransaction = transaction.Transaction()
    print(client.private_key)

main()
# if __name__ =='__main__':
#     main()
