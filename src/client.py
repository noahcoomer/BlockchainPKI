from random import randint
from threading import Thread
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20
from os.path import expanduser

import os, ssl, json, time, errno, socket, base64, pickle

import validator
import transaction
import blockchain


class Client(object):
    blockchain = None

    def __init__(self, name, addr="0.0.0.0", port=1234, validators_capath="~/.BlockchainPKI/validators/"):
        '''
            Initialize a Client object

            :param str name: A canonical name
            :param str addr: The ip address for serving inbound connections
            :param int port: The port for serving inbound connections
            :param str capath: 
        '''
        self.name = name or socket.getfqdn(socket.gethostname())
        self.address = addr, port 
        self.validators_capath = validators_capath
        self._init_net()
       # self._load_other_ca(capath=self.validators_capath)
        
        # Update the blockchain
        print("Updating blockchain. This may take a while.")
        self.blockchain = self.update_blockchain()
        print("Finished updating blockchain.")
        self.command_loop()

    def _init_net(self):
        '''
            Initializes a TCP socket for incoming traffic and binds it.

            If the connection is refused, -1 will be returned.
            If the address is already in use, a new random port will be recursively tried.
        '''
        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.settimeout(0.001)  # Blocking socket
            self.net.bind(self.address)  # Bind to address
            self.net.listen()  # Listen for connections
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                # Connection refused error
                return -1, e
            elif e.errno == errno.EADDRINUSE:
                # Address already in use, try another port
                addr, port = self.address
                new_port = randint(1500, 5000)
                print("Address %s:%d is already in use, trying port %d instead" %
                      (addr, port, new_port))
                self.address = addr, new_port
                self._init_net()  # Try to initialize the net again
        finally:
            self.context = ssl.create_default_context()
        
    def _load_other_ca(self, capath=None):
        '''
            Loads a set of CAs from a directory 
            into the sending context
        '''
        assert self.context != None, "Initialize the send context before loading CAs."

        capath = capath.replace("~", os.environ["HOME"])

        if not os.path.exists(capath):
            print("Directory %s does not exist" % capath)
            cont = input("Would you like to create %s? (y/n)" % capath)
            if cont.strip() == 'y':
                os.mkdir(capath)
                print("Created %s" % capath)
        elif len(os.listdir(capath)) == 0:
            raise FileNotFoundError(
                "No other Validator CAs were found at %s. You will be unable to send any data without them." % capath)
        else:
            self.context.load_verify_locations(
                capath=capath or self.validators_capath)

    def send_transaction(self, val, tx):
        '''
            Send a transaction to the validator network

            :param Transaction tx: The transaction to send
        '''
        #
        if self.net and self != val:
            # Connect to validators's inbound net using client's outbound net
            address = val.address
            # Serialize the transaction as a bytes object
            txn = pickle.dumps(tx)
            # Create a new socket (the outbound net)
            print("Attempting to send to %s:%s" % val.address)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setblocking(True)
                try:
                    # Connect to the validator
                    s.connect(address)
                    # Send the entirety of the message
                    s.sendall(txn)
                except OSError as e:
                    # Except cases for if the send fails
                    if e.errno == errno.ECONNREFUSED:
                        print(e)
                        # return -1, e
                except socket.error as e:
                    print(e)
        else:
            raise Exception(
                "The validator must be initialized and listening for connections")
        

    def update_blockchain(self):
        '''
            Update blockchain to be current
        '''
        chain = blockchain.Blockchain()
        return chain

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

        inputs = { "REGISTER" : { name : pub } }

        # Validate that the name is not already in the blockchain, break if found
        flag = False
        for block in reversed(self.blockchain.chain):
            for tx in block.transactions:
                inp = json.loads(tx.inputs)
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
        if flag == False:
            outputs = { "REGISTER" : { "success" : True } }
        else:
            outputs = { "REGISTER" :
                            {
                                "success" : False,
                                "message": "This name is already registered."
                            }
                      }

        # dump to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        # send the transaction and return it for std.out
        tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=gen, inputs=inputs, outputs=outputs)
        # Create an entry point to the validator network that the client can connect to

        ############## UNCOMMENT BEFORE GOING LIVE #################
        #validator = validator.Validator(Alice = name="Validator", addr="10.228.112.126", port=4321)
        #self.send_transaction(validator, tx)

        return tx

    def pki_query(self, generator_public_key, name):
        '''
            Query the blockchain for a public key given a name
        '''

        # input verification
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return -1

        # Query blockchain, break if we find our public key
        public_key = None
        for block in reversed(self.blockchain.chain):
            for tx in block.transactions:
                inputs = json.loads(tx.inputs)
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
            outputs = { "QUERY" : { "success": True, "query" : True, "public_key" : public_key } }
        else:
            outputs = { "QUERY" :
                            {
                                "success" : False,
                                "message" : "Name not found."
                            }
                      }

        # dump to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=gen,
                                    inputs=inputs, outputs=outputs)

        ####### UNCOMMENT BEFORE PRODUCTION ########
        #self.send_transaction(tx)

        return tx

    def pki_validate(self, generator_public_key, name, public_key):
        '''
        enable the user to check whether the name and public key are valid
        return true if it is valid and false if it is not valid
        '''
        flag = False
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return - 1

        pub = self.verify_public_key(public_key)
        if not pub:
            print("The register public key is incorrectly formatted. Please try again.")
            return -1
        
        if len(name) < 1 or len(name) > 255:
            print("The name value must be between 1-255 characters.")
            return -1 
        flag = True

        inputs = { "VALIDATE" : { "name" : name, "generator_public_key" : gen, "public_key" : pub } }
        
        outputs = dict()

        if flag == True:
            outputs = { "VALIDATE" : { "success" : True, "Validated" : True, "name" : name, "public_key" : pub } }
        else:
            outputs = { "VALIDATE" : { "success" : False, "message" : "cannot validate name and public key" } }


        #dumps to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)


        tx = transaction.Transaction(transaction_type='standard', tx_generator_address=gen, inputs= inputs, outputs= outputs)

        #self.send_transaction(tx)
        return tx

    def pki_update(self, name, old_public_key, new_public_key):
        '''
        enable the user to update the public key with the new public key 
        return: the transaction with the new public key 
        '''

        '''
        check whether the name and the old_public_key are in the blockchain  
        '''

        #verify the old_public_key
        old_key = self.verify_public_key(old_public_key)
        if not old_key:
            print('this old public key is not formatted correctly')
            return -1 
        
        #verify the new_public_key
        new_key = self.verify_public_key(new_public_key)
        if not new_key:
            print('This new public key is not formatted correctly')
            return -1 
            

        flag = False
        for block in self.blockchain.chain:
            for tx in block.transactions:
                inputs = json.loads(tx.inputs)
                for key in inputs.keys():
                    try:
                        if name == inputs[key]['name'] and old_public_key == inputs[key]['public_key']:
                            flag = True
                    except:
                        continue
                if flag == True:
                    break
            if flag == True:
                break
        

        # Create the input for the update, for the input we have the name, old_public_key and the new_public_key 
        inputs = { "UPDATE" : { "name" : name, "old_public_key" : old_key, "new_public_key" : new_key } }

        # Create the output for the update 
        outputs = dict()
         
        if flag == True:
            outputs = { "UPDATE" : { "success" : True, "update" : True, "new_public_key" : new_key } }
        else:
            outputs = { "UPDATE" : { "success" : False, "message" : "cannot find the name and old public key" } }


        #dumps to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        '''
        this means that we found the name and the old_public_key in one of the transactions
        Goal: need to add a new transaction that will have the same name but with a new public key 
        '''
        tx = transaction.Transaction(transaction_type='standard', inputs= inputs, outputs= outputs)
        #self.send_transaction(tx)
        return tx

    def pki_revoke(self, public_key, private_key):
        '''

        '''
        tx = transaction.Transaction()

        self.send_transaction(tx)
        return tx

    @staticmethod
    def generate_keys():
        '''
            Generate public and private keys using RSA key generation
        '''
        # Specify the IP size of the key modulus
        modulus_length = 256 * 8
        # Using a Random Number Generator and the modulus length as parameters
        # For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_length, Random.new().read)

        # create the key dir if not created
        home_path = expanduser("~")
        key_path = os.path.join(home_path, ".BlockchainPKI","keys")
        if not os.path.exists(key_path):
            print("Directory %s does not exist" % key_path)
            cont = input("Would you like to create %s? (y/n): " % key_path)
            if cont.strip() == 'y':
                os.mkdir(key_path)
                print("Created %s" % key_path)

        # write out the private key
        file_out = open(os.path.join(key_path, "private.pem"), 'wb')
        file_out.write(private_key.export_key())
        print("Sucessfully wrote out new private RSA key to ~/.BlockchainPKI/keys/private.pem")

        # write out the public key
        file_out = open(os.path.join(key_path, "public.pem"), 'wb')
        file_out.write(private_key.publickey().export_key())
        print("Successfully wrote out new public RSA key to ~/.BlockchainPKI/keys/public.pem")

        # Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key

    @staticmethod
    def encrypt_message(a_message, public_key):
        '''
            Encrypt and sign a message
        '''
        #Serialize message object
        serialized_message = pickle.dumps(a_message)
        # Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        # Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(serialized_message)
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
        #Dserialize message object
        deserialized_message = pickle.loads(decoded_decrypted_msg)
        return deserialized_message

    @staticmethod
    def verify_public_key(public_key):
        '''
            Verify a public key is correctly formatted by making an RSA key object
            :params: public_key - a file object of the public key to be verified
                    passphrase - if the key requires a passphrase use it, otherwise passphrase should be None
        '''
        try:
            key = RSA.import_key(public_key.read())
            key = key.publickey().export_key()
            return key.decode()
        except ValueError:
            return None

    def command_loop(self):
        # Ensure that the auxillary data folder is set up
        home_path = expanduser("~")
        home_path = os.path.join(home_path, ".BlockchainPKI/")
        if not os.path.exists(home_path):
            os.mkdir(home_path)

        # Finished set up, enter command loop
        print("PKChain Client successfully set up. Type 'help' for a list of commands")
        while True:
            command = input(">>> ").split(" ")
            if command[0] == 'help':
                print("Transactional Functions:\n\n ")
                print("register                         -Register a name and public key on the blockchain.")
                print("query                            -Query for a public key given a name.\n\n")
                print("validate                         -verifies whether a pair of (name, public key) is valid or not")
                print("update                           -Update a user's public key")
                print("Local Functions:\n\n")
                print("generate                         -Generate a public and private key pair.")
                print("encrypt <public_key> <message>   -Encrypt a message with a public key.")
                print("decrypt <private_key> <message>  -Decrypt a message with a private key.\n\n")
            elif command[0] == 'exit':
                self.close()
                break
            elif command[0] == 'register':
                client_pub_key_path = input("Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input("Enter the name you would like to register to a public key: ")
                reg_pub_key_path = input("Enter the path of the public key you would like to register: ")
                reg_pub_key = open(reg_pub_key_path, 'r')
                tx = self.pki_register(client_pub_key, name, reg_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'query':
                client_pub_key_path = input("Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input("Enter the name you would like to query for: ")
                tx = self.pki_query(client_pub_key, name)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'validate':
                client_pub_key_path = input("Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, "r")
                reg_pub_key_path = input("Enter the path of the public key you would like to register: ")
                reg_pub_key_path = open(reg_pub_key_path, "r")
                name = input("Enter the name you would like to validate: ")
                tx = self.pki_validate(client_pub_key, name, reg_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'update':
                new_client_pub_key_path = input("Enter the path of your new public key (generator address): " )
                new_client_pub_key = open(new_client_pub_key_path, "r")
                old_client_pub_key_path = input("enter the path of your old public key (generator address): ")
                old_client_pub_key = open(old_client_pub_key_path, "r")
                name = input('Enter the name you would like to update: ')
                tx = self.pki_update(name, old_client_pub_key, new_client_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'revoke':
                pass
            elif command[0] == 'generate':
                private_key, public_key = self.generate_keys()
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
