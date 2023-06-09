import socket
import sys
import select
import time
from datetime import datetime

def closeServer():
    clientsocket.close()
    serversocket.close()
    file.close()

def Connect():
    # Create a TCP socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setblocking(True)
    # Bind the socket to the host and port
    try:
        serversocket.bind((host, port))
    except Exception as fail:
        print(str(fail))
        print("NOT ABLE TO BIND PORT")
        print("EXITING...")
        sys.exit()

    print(f"Server IP address: {host}")
    print(f"Server port number: {port}")
    # Start listening for incoming connections
    serversocket.listen()  #one connection enabled
    print(f"Listening on {host}:{port}...")

    # Wait for a client to connect
    clientsocket, addr = serversocket.accept()
    print(f"Got a connection from {addr}")
    return clientsocket, serversocket

def OpenFile():
    file = open('/Users/dominikpapp/Desktop/egyetem/6felev/onlab/web/data.txt', 'a')
    print("Appending data to: data.txt")
    return file
# Define the host and port to listen on
host = socket.gethostbyname(socket.gethostname())
#host = '192.168.1.249'  #otthoni wifi
#host = '192.168.0.102'  #koli wifi
port = 9999             #random port
#open database
file = OpenFile()

# Connect to the client
clientsocket, serversocket = Connect()

# Receive data from the client until a space character is encountered
data = b""
message = ""

while True:
    # Wait for data to be received or for the timeout to expire
    ready_sockets, _, _ = select.select([clientsocket], [], [], 10)

    if len(ready_sockets) == 0:
        # Timeout expired, assume client disconnected
        print("Presumably Client disconnected. Attempting reinstating connection in 10 seconds")
        closeServer()
        time.sleep(10) # Wait for os to free port
        file = OpenFile()
        clientsocket, serversocket = Connect()

    chunk = clientsocket.recv(1024)
    data += chunk
    if b"q" in data:
        message = data.decode()
        message = message.replace('q', '\r')
        data = b""
        print(f"Received message: {message}")
    if "exit" in message:
        break
    else:
        # Get current date and time
        current_datetime = datetime.now()
        # Format the date and time as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # Append Celsius symbol to the temperature without newline
        messageWithCels = f"{message.rstrip()} \u2103"
        # Expected format: date 22.1 celsius\r
        file.write(formatted_datetime + "  " + messageWithCels + '\r')
        file.flush()       #'live' data writing

#close everything
closeServer()
