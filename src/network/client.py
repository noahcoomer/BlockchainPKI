# PKChain Client

import socket
import base64
import json
import time

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20

from .net import Net

# This needs to be the last imported line
import sys
sys.path.append('../')
from data_structs import transaction


class Client(object):
    blockchain = []  
  
    def __init__(self, name, addr="0.0.0.0", port=1234):
        '''
            Initialize a Client object

            :param str name: A canonical name
            :param str addr: The ip address for serving inbound connections
            :param int port: The port for serving inbound connections
        '''
        self.name = name
        self.net = Net(name=name, addr=addr, port=port, bind=True)

        # Poll for node connections and connect to the network
        # print("Connecting to the PKChain network...")
        # self.connect_to_network(self.host, self.port)

        # Update the blockchain
        print("Updating blockchain. This may take a while.")
        self.blockchain = self.update_blockchain()
        print("Finished updating blockchain.")
        
    def send_transaction(self, tx):
        '''
            Send a transaction to the validator network

            :param Transaction tx: The transaction to send
        '''
        pass
        
    def update_blockchain(self):
        '''
            Update blockchain to be current
        '''
        return []


    def pki_register(self, generator_public_key, name, public_key):
      '''
            Creates a register transaction
            :params: name - name to be associated with public key
                     public_key - the public key to be added
            :return: tx - the transaction that was just generated
      '''

      # input verification
      if len(name) < 1 or len(name) > 255:
        print("The name value must be between 1-255 characters.")
        return -1
      
      # public key verification
      gen = self.verify_public_key(generator_public_key)
      if not gen:
        print("The generator public key is incorrectly formatted. Please try again.")
        return -1

      pub = self.verify_public_key(public_key)
      if not pub:
        print("The register public key is incorrectly formatted. Please try again.")
        return -1

      inputs = { "REGISTER" : { name : public_key } }

      # Validate that the name is not already in the blockchain, break if found
      flag = False
      for block in self.blockchain.chain:
          for transaction in block.transactions:
              inp = json.loads(transaction.inputs)
              for key in inp.keys():
                  try:
                      if name == inp[key]["name"]:
                          flag = True
                          break
                  except:
                    continue
              if flag == True:
                  break
          if flag == True:
              break

      outputs = dict()                    
      if not flag:
          outputs = { "REGISTER" : { "register" : True } }
      else:
          outputs = { "REGISTER" : { "register" : False } }

      # dump to JSON
      inputs = json.dumps(inputs)
      outputs = json.dumps(outputs)

      # send the transaction and return it for std.out
      tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=generator_public_key, inputs=inputs, outputs=outputs)
      self.send_transaction(tx)
      return tx
  

    def pki_query(self, generator_public_key, name):
      '''
        Query the blockchain for a public key given a name
      '''

      # input verification
##      gen = self.verify_public_key(generator_public_key)
##      if not gen:
##        print("The generator public key is incorrectly formatted. Please try again.")
##        return -1

      # Query blockchain, break if we find our public key
      public_key = None
      for block in self.blockchain.chain:
          for transaction in block.transactions:
              inputs = json.loads(transaction.inputs)
              for key in inputs.keys(): # should only be 1 top level key - still O(1)
                  try:
                      if name == inputs[key]["name"]:
                          public_key = inputs[key]["public_key"]
                  except:
                    continue
              if public_key:
                break
          if public_key:
            break
      
      inputs = { "QUERY" : { "name" : name } }
      outputs = dict()
      if public_key:
          outputs = { "QUERY" : { "query" : True, "public_key" : public_key } }
      else:
          outputs = { "QUERY" : { "query" : False } }

      # dump to JSON
      inputs = json.dumps(inputs)
      outputs = json.dumps(outputs)                       
               
      tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=generator_public_key,
                                   inputs=inputs, outputs=outputs)

      self.send_transaction(tx)
      return tx


    def pki_validate(self, generator_public_key, name, public_key):
      '''

      '''
      tx = transaction.Transaction()

      self.send_transaction(tx)


    def pki_update(self, name, old_public_key, new_public_key):
      '''

      '''
      tx = transaction.Transaction()

      self.send_transaction(tx)


    def pki_revoke(self, public_key, private_key):
      '''

      '''
      tx = transaction.Transaction()

      self.send_transaction(tx)
    

    @staticmethod
    def generate_keys():
        '''
            Generate public and private keys using RSA key generation
        '''
        # Specify the IP size of the key modulus
        modulus_lenght = 256 * 4
        # Using a Random Number Generator and the modulus length as parameters
        # For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        # Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key

    @staticmethod
    def encrypt_message(a_message, public_key):
        '''
            Encrypt and sign a message
        '''
        # Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        # Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(a_message)
        # Encode your message using Base64 Encodings
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg

    @staticmethod
    def decrypt_message(encoded_encrypted_msg, private_key):
        '''
            Decrypt and verify a message
        '''
        # Set your public key as a decrpytor that will be using the PKCS1_OAEP cipher
        decryptor = PKCS1_OAEP.new(private_key)
        # Decrypt a message using your decryptor
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        # Decode your message using Base64 Encodings
        decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg


    @staticmethod
    def verify_public_key(public_key):
      '''
        Verify a public key is correctly formatted by making an RSA key object
        :params: public_key - a string or byte string of the public key to imported
                 passphrase - if the key requires a passphrase use it, otherwise passphrase should be None
      '''
      try:
        key = RSA.import_key(public_key)
        return key
      except ValueError:
        return False
      

    def close(self):
        '''
            Close the client and its net
        '''
        if self.net:
            self.net.close()


if __name__ == "__main__":
    # Generates private and public key
    ##    private_key, public_key = Client.generate_keys()
    ##    print(private_key, public_key)
    ##
    ##    message = b'This will be my test message'
    # Encrypt a message using the public key
    ##    encoded = Client.encrypt_message(message, public_key)
    # print(encoded)
    # Decrypt a message using the private key
    ##    decoded = Client.decrypt_message(encoded, private_key)
    # print(decoded)

    Client1 = Client(name="Client 1")

    # Finished set up, enter command loop
    print("PKChain Client successfully set up. Type 'help' for a list of commands")
    while True:
        command = input(">>> ").split(" ")
        if command[0] == 'help':
            print("Transactional Functions:\n\n ")
            print("register                         -Register a name and public key on the blockchain.")
            print("query                            -Query for a public key given a name.\n\n")
            print("Local Functions:\n\n")
            print("generate                         -Generate a public and private key pair.")
            print("encrypt <public_key> <message>   -Encrypt a message with a public key.")
            print("decrypt <private_key> <message>  -Decrypt a message with a private key.\n\n")
        elif command[0] == 'exit':
            Client1.close()
            break
        elif command[0] == 'register':
            pass
        elif command[0] == 'query':
            pass
        elif command[0] == 'generate':
            private_key, public_key = Client1.generate_keys()
            print()
            print("Your public key is:\n\n",
                  public_key.export_key().decode(), "\n\n")
            print("Your private key is:\n\n",
                  private_key.export_key().decode(), "\n\n")
        elif command[0] == 'encrypt':
            print("Implementation coming soon.")
        elif command[0] == 'decrypt':
            print("Implementation coming soon.")
        else:
            print("\nCommand not understood. Type 'help' for a list of commands.\n")
