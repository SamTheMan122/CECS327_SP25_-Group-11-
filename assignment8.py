# CECS 327 - Assignment 8
# Samuel Barcarse and Jan Montemayor
# May 5, 2025

import socket

# Sets up TCP client socket
def client(IP, portNumber):

    # Create socket via AF_INET and SOCK_STREAM
    TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to Server
    TCPSocket.connect((IP, int(portNumber)))

    # Loops through asking the user if they want to send a message.
    # Stops when user enters N (no)
    sendMessage = True
    choice = "Y"
    print("1. What is the average moisture inside my kitchen fridge in the past three hours?")
    print("2. What is the average water consumption per cycle in my smart dishwasher?")
    print("3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
    while choice is not "Q":
        choice = input("\nEnter Selection: ")
        if choice == "1" or choice == "2" or choice == "3":
            TCPSocket.send(bytearray(choice, encoding="utf-8"))
            serverResponse = TCPSocket.recv(1024).decode("utf-8")
            print(f"\nServer Response: {serverResponse}")
        else:
            print("\nSorry, this query cannot be processed. Please try one of the following: [1, 2, 3, Q].")
    TCPSocket.close()

# Server creates a TCP socket
def server(IP, portNumber):
    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Binds IP and port number
    TCPsocket.bind((IP, int(portNumber)))

    # Listens for incoming connections
    TCPsocket.listen(5)

    # Connects to client and receive messages until connection ends
    while True:
        incomingSocket, incomingAddress = TCPsocket.accept()
        print(f"\nConnection from {incomingAddress}\n")
        with incomingSocket:
            while True:
                data = incomingSocket.recv((1024)).decode("utf-8")
                if not data:
                    break
                # This is where the message is converted to uppercase
                data = data.upper()
                incomingSocket.send(bytearray(str(data), encoding="utf-8"))
            break
        incomingSocket.close()

def main():

    # Initialize program choice for menu, IP, and port number (converted to int later)
    programChoice = 0
    ip, port = "0.0.0.0", ""

    # Loops through with configurations, client, server menu
    while programChoice != 4:
        print("1. IP Address and Server Address Configurations \n2. Start Client Side Echo \n3. Start Server Side Echo \n4. Quit Program")
        programChoice = int(input("Enter choice: "))

        # Configurations
        if programChoice == 1:
            try:
                ip = input("\nEnter IP Address of server: (Ex: xxx.xxx.x.x) ")
                check = socket.inet_aton(ip)
            except check == 0:
                print("Invalid IP, check formatting and try again...")

            try:
                port = input("Enter port Address of server: (Ex: 1 - 65534) ")
            except ValueError:
                print("Invalid IP, check formatting and try again...")
            print("\nSuccessfully Configured IP and server addresses...\n")

        # Client Side Startup
        elif programChoice == 2:
            if(ip == "" or port == ""):
                print("\nNo IP address or server port provided. Please configure first...")
            else:
                print(f"Your IP Address configurations: {ip}")
                print(f"Your port number configurations: {port}")
                try:
                    client(ip, port)
                except TimeoutError:
                    print("\nERROR: Connection cannot be established. Check addresses and try again. \n")

        # Server Side Startup
        elif programChoice == 3:
            if (ip == "" or port == ""):
                print("\nNo IP address or server port provided. Please configure first...")
            else:
                print(f"Your IP Address configurations: {ip}")
                print(f"Your port number configurations: {port}")
                try:
                    server(ip, port)
                except TimeoutError:
                    print("\nERROR: Connection cannot be established. Check addresses and try again. \n")

        else:
            continue
    print("\nPress Enter to Close Program")

main()

