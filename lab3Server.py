import configparser
import logging
import socket
import time
import json
import pickle
import os

#reads the config file
config = configparser.ConfigParser()
config.read("3461-Project3Server.conf")

# File name for storing the list data
file_items = 'my_items.pickle'
file_name = 'my_list.pickle'

#sets up the logging file
logging.basicConfig(filename="serverLogFile.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 
logger=logging.getLogger()
logger.setLevel(logging.DEBUG) 


#read the serverHost and serverPort 
serverHost = config.get('project3', 'serverHost')
serverPort = config.getint('project3', 'serverPort')
logging.info("Host address:" + serverHost)
logging.info("Port number:" + str(serverPort))

#read log details
logFile = config.get('logger', 'logFile')
logLevel = config.get('logger', 'logLevel')
logFileMode = config.get('logger', 'logFileMode')


# create a socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logging.info("Opened TCP socket")

# Open a socket and bind to the IP address and port
serverSocket.bind((serverHost, serverPort))

# servers listens for incoming connections
serverSocket.listen()

# accept new connection
conn, address = serverSocket.accept()  
print("Server starting on: " + serverHost)
logging.info("Server starting on: " + serverHost)

list_items = []  # list to store items in the list
list_name = []

# Check if file exists
if os.path.exists(file_name) and os.path.exists(file_items) :
    # Load the list from the saved file using pickle
    with open(file_items, 'rb') as file1:
        list_items= pickle.load(file1)
    with open(file_name, 'rb') as file1:
        list_name = pickle.load(file1)
while True:
    
    #recieve the request
    data = conn.recv(1024).decode()
    if not data:
        logging.error("Server is not responding")
        continue

    #convert to python
    convert = json.loads(data)
    logging.info("Client request: " + str(convert))
         # process client requests
    if convert['request'].strip() == "QUIT":
        logging.info("Processing client request QUIT")
        logging.debug("Preparing to shutdown server")
         # If a list has been created, but not deleted, save the list for next application start
        if len(list_name) == 1:
            with open(file_items, 'wb') as file:
                pickle.dump(list_items, file)
            with open(file_name, 'wb') as file:
                pickle.dump(list_name, file)

        # Format and send a server response stating the server is closing
        response = {'response': 'Server shutting down ...', 'parameter': None}
        print("Server shutting down ...")
        logging.warning("Server is shutting down ...")
        convertBack = json.dumps(response)
        conn.send(convertBack.encode())
        # Close the client connection and exit the application gracefully
        conn.close()
        serverSocket.close()
        logging.info("Server shutting down")
        exit(0)
    elif convert['request'].strip() == "ADD":
        if len(list_name) < 1:
            response = {'response': 'ERROR', 'parameter': 'No list created'}
            logging.warning("Server response: " + str(response))
        else:
            item = convert['parameter']
            if item not in list_items:
                list_items.append(item)
                response = {'response': 'ADD', 'parameter': 'Item added to the list'}
                logging.info("Server response: " +str(response))
            else:
                response = {'response': 'ERROR', 'parameter': 'Item already exists in the list'}
                logging.warning("Server response: " + str(response))

    elif convert['request'].strip() == "CREATE":
        # If a list has not been created, initialize a new list using the client request parameter as its name
        item = convert['parameter']
        if len(list_name) == 0 : 
            list_name.append(item)
            list_items = []
            response = {'response': 'CREATE', 'parameter': 'Created new list ' + item}
            logging.info("Server response: " +str(response))
        else:
            response = {'response': 'WARNING', 'parameter': 'List ' + list_name[0] + ' already exists'}
            logging.warning("Server response: " + str(response))
    
    elif convert['request'].strip() == "DELETE":
        item = convert['parameter'].strip()
        if  list_name and list_name[0] == item:
            response = {'response': 'DELETE', 'parameter': 'Deleted ' + item + ' list '}
            logging.info("Server response: " +str(response))
            #  Load the list from the file using pickle
            with open(file_name, 'rb') as file:
                list_name = pickle.load(file)
            with open(file_items, 'rb') as file:
                list_items = pickle.load(file)
            # Clear the list data
            list_name.clear()
            list_items.clear()

            # Save the empty list back to the file using pickle
            with open(file_name, 'wb') as file:
                pickle.dump(list_name, file)
            with open(file_items, 'wb') as file:
                pickle.dump(list_items, file)
        else:
            response = {'response': 'WARNING', 'parameter': 'List ' + item + ' does not exists'}
            logging.warning("Server response: " + str(response))
    
    elif convert['request'].strip() == "REMOVE":
        # If a list has been created and the list item is in the list, remove the item from the list
        if list_name and convert['parameter'] in list_items:
            list_items.remove(convert['parameter'])
            response = {'response':'REMOVE', 'parameter': 'Item ' + convert['parameter'] + ' removed from the list'}
            logging.info("Server response: " +str(response))
        else:
            response = {'response':'ERROR' , 'parameter' : 'Item not found in the list'}
            logging.warning("Server response: " + str(response))

    elif convert['request'].strip() == "SHOW":
        # If a list has been created, send the current list items as response
        if list_name:
            response = {'response': 'SHOW', 'parameter': list_items}
            logging.info("Server response: " +str(response))
        else:
            response = {'response': 'WARNING', 'parameter': 'List is empty'}
            logging.warning("Server response: " + str(response))

    else:
        response = {'response': 'Error',
                    'parameter': 'Invalid request'
                    }
        logging.error("Invalid request")
      
    #convert back to json and send to client
    convertBack= json.dumps(response)
    conn.send(convertBack.encode())  # send data to the client

        
    

    

