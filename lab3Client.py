import configparser
import logging
import socket 
import json


#reads the config file
config = configparser.ConfigParser()
config.read("3461-Project3Server.conf")



#sets up the logging file
logging.basicConfig(filename="clientLogFile.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 
logger=logging.getLogger()
logger.setLevel(logging.INFO) 


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
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
clientSocket.connect((serverHost, serverPort))

# Function to display usage message
def display_usage():
    print("\nusage:")
    print("add <item> - Add list item")
    print("create <list name> - Create list")
    print("delete <list name> - Delete list")
    print("help - Help")
    print("quit - Quit")
    print("remove <item> - Remove list item")
    print("show - Show items\n")


#loops till user quits
while True:

    #Gets user input
    phrase= input()
    logging.info("INFO Command entered: " + phrase)

    if not phrase:
        print('Error: Empty command entered.')
        logging.warning('Empty command entered.')
        continue

    #intializes variables
    words = []
    beginning=0
    end=0
    noSpace=True

    #if string is one word
    if len(phrase) <=1:
        output= phrase
    
    else:
        #parses through string
        for x in phrase:
            end=end+1 #contains value of last character thats stored in the list
            if (x.isspace()) == True:
                noSpace=False
                if len(words) == 0: #if first word of input
                    words.append(phrase[beginning:end].upper())
                else:
                    words.append(phrase[beginning:end])
                beginning=end 
            if end == len(phrase)-1 : #if the last character of input is reached, store last word in list
                if(noSpace==True): #if there is only one word in user input
                    words.append(phrase[beginning:end+1].upper())
                else:
                    words.append(phrase[beginning:end+1])    
        
        #reverses list and displays output
        words.reverse()
        output = words.pop() #first word
        request = output
    # concatenate the 2nd to the last tokens into a string, each separated by whitespace (blanks). 
    # This string will be known as the parameter 
    parameter = ""
    while len(words) > 0:
        parameter= parameter + words.pop()

    #creates request in dict form to covert to json
    clientRequest = {"request": request,
                     "parameter": parameter
                     }
    request = request.strip()
    # Verify if request is a valid command
    valid_commands = ['ADD', 'CREATE', 'DELETE', 'HELP', 'QUIT', 'REMOVE', 'SHOW']
    multiple_commands= ['ADD', 'CREATE', 'DELETE', 'REMOVE']
    one_param = ['QUIT' , 'SHOW']
    if request in multiple_commands or request in one_param: 
        if not parameter.strip() and request not in one_param:
            print("Missing element in command")
            logging.error("Missing element in command: {}".format(request))
            display_usage()
        else:
            server_Request = json.dumps(clientRequest)

            #sends data to server
            clientSocket.sendall(server_Request.encode())

            # Receive the response
            data = clientSocket.recv(1024).decode()
            if not data:
                logging.error("Server is not responding")
                continue
            
            #converts back to python
            value= json.loads(data)
            logging.info("Server response: " + str(value))
            if value["response"] == 'SHOW':
                    # Display response parameter as numbered list
                    print('List Items:\n')
                    itemNum = 1
                    for item in value["parameter"]:
                         print(str(itemNum) + ': ' + item)
                         itemNum += 1
            elif value["response"] in ['WARNING', 'ERROR']:
                    # Display response and parameter
                    print('{}: {}'.format(value["response"], value["parameter"]))
                    logging.warning('{}: {}'.format(value["response"], value["parameter"]))
            elif output == "QUIT":
                    print(value["response"])
                    print("Client shutting down...")
                    logging.info("Response recieved: " + value["response"])
                    break
            else:
                print("Response recieved: " + value["parameter"])
                logging.info("Response recieved: " + value["parameter"])
    elif request.upper() not in valid_commands:
        print('Error: Invalid command entered.')
        logging.warning('Invalid command entered: {}'.format(request))
        display_usage()
    elif request == "HELP":
        display_usage()
    
   
# Close socket
clientSocket.close()


    
