### Blockchain PKI
### main.py
### Driver/interface file for blockchain application
### Created by Noah Coomer


def establish_connection():
    print()


def main():
    print("Welcome to PKChain - A blockchain based PKI solution.")
    
    print("Establishing a connection with the network...")
    ###
    establish_connection()
    ###
    print("Successfully established connection with the network.")

    print("Checking current block height...")
    ### if local machine block height < remote block height: download new blocks
    print("Your blockchain is now up to date.")

    role = None
    while role != 'c' and role != 'v':
        role = input("Are you a [c]lient or a [v]alidator? ")
        if role == 'c':
            ### Run the client interface pipeline
            print()
        elif role == 'v':
            ### Set up the machine as a validator
            print()
    
        

if __name__ == '__main__':
    main()
