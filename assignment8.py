# CECS 327 - Assignment 8
# Samuel Barcarse and Jan Montemayor
# May 5, 2025

import socket
import psycopg2
from datetime import datetime, timedelta
import pytz

def averageMoisture():
    conn = psycopg2.connect("postgresql://neondb_owner:npg_9gx6WRFVwoYE@ep-quiet-frost-a67ek0uk-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require")
    cursor = conn.cursor()
    # SQL query to grab devices that are only of 'fridge' type
    cursor.execute('SELECT "assetUid" FROM "Assignment8_metadata" WHERE "assetType" = %s', ('Fridge',))
    utc = pytz.utc
    end_time = datetime.now(utc)
    start_time = end_time - timedelta(hours=3)
    # SQL query to grab the day of since need to determine past three hour interval
    cursor.execute('SELECT payload FROM "Assignment8_virtual" WHERE time BETWEEN %s AND %s', (start_time, end_time))
    total, count = 0.0, 0
    # Loops through each payload
    for (payload,) in cursor.fetchall():
        # Fridges have moisture meters (both have different names though). Grabs ammeter values of fridge devices
        if "Moisture Meter - FridgeMoistureMeter" in payload:
            rh = float(payload["Moisture Meter - FridgeMoistureMeter"])
            total += rh
            count += 1
        if "Moisture Meter - FridgeMoistureMeter2" in payload:
            rh = float(payload["Moisture Meter - FridgeMoistureMeter2"])
            total += rh
            count += 1
    cursor.close()
    conn.close()
    if count == 0:
        return "No moisture data found in past 3 hours."
    return f"Average fridge moisture over past 3 hours: {total / count:.2f}% RH"

def averageWaterUsage():
    conn = psycopg2.connect("postgresql://neondb_owner:npg_9gx6WRFVwoYE@ep-quiet-frost-a67ek0uk-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require")
    cursor = conn.cursor()

    # SQL query to grab unique identifier of dishwasher devices
    cursor.execute('SELECT "assetUid" FROM "Assignment8_metadata" WHERE "assetType" = %s', ('Dishwasher',))

    # Time filter (last 24 hours or past day)
    utc = pytz.utc
    end_time = datetime.now(utc)
    start_time = end_time - timedelta(days=1)

    # # SQL query to grab the day of cycles
    cursor.execute('SELECT payload FROM "Assignment8_virtual" WHERE time BETWEEN %s AND %s', (start_time, end_time))

    total, count = 0.0, 0
    for (payload,) in cursor.fetchall():
        # Dishwashers are the only device in the smart home with water sensors, so only look for that
        if "Water Consumption Sensor" in payload:
            liters = float(payload["Water Consumption Sensor"])
            gallons = liters * 0.264172
            total += gallons
            count += 1

    cursor.close()
    conn.close()

    if count == 0:
        return "No dishwasher water usage data found."
    return f"Average water consumption per cycle: {total / count:.2f} gallons"

def highestElectric():
    conn = psycopg2.connect("postgresql://neondb_owner:npg_9gx6WRFVwoYE@ep-quiet-frost-a67ek0uk-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require")
    cursor = conn.cursor()
    # Grabs device identifiers from metadata table
    cursor.execute('SELECT "assetUid", "assetType" FROM "Assignment8_metadata"')
    utc = pytz.utc
    end_time = datetime.now(utc)
    start_time = end_time - timedelta(days=1)
    cursor.execute('SELECT payload FROM "Assignment8_virtual" WHERE time BETWEEN %s AND %s', (start_time, end_time))

    # Tracks device usage
    usage = {"Fridge 1": 0.0, "Fridge 2": 0.0,"Dishwasher": 0.0}


    for (payload,) in cursor.fetchall():
        # Dishwasher Ammeter
        if "DishwasherAmmeter" in payload:
            wh = float(payload["DishwasherAmmeter"])
            usage["Dishwasher"] += wh / 1000
        # Fridge 1 Ammeter
        elif "FridgeAmmeter" in payload:
            wh = float(payload["FridgeAmmeter"])
            usage["Fridge 1"] += wh / 1000
        # Fridge 2 Ammeter
        elif "FridgeAnmeter2" in payload:
            wh = float(payload["FridgeAnmeter2"])
            usage["Fridge 2"] += wh / 1000
        else:
            continue
    cursor.close()
    conn.close()
    most_device = max(usage, key=usage.get)
    return f"{most_device} used the most electricity: {usage[most_device]:.2f} kWh"

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
    while choice != "Q":
        choice = input("\nEnter Selection (1-3, or Q to quit): ").strip().upper()
        if choice in ["1", "2", "3"]:
            TCPSocket.send(bytearray(choice, encoding="utf-8"))
            serverResponse = TCPSocket.recv(1024).decode("utf-8")
            print(f"\nServer Response: {serverResponse}")
        elif choice == "Q":
            print("\nExiting client...")
        else:
            print("\nSorry, this query cannot be processed. Please try one of the following: [1, 2, 3, Q].")

    TCPSocket.close()

# Server creates a TCP socket
def server(IP, portNumber):
    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsocket.bind((IP, int(portNumber)))
    TCPsocket.listen(5)
    print("Server is now listening for connections...\n")

    while True:
        incomingSocket, incomingAddress = TCPsocket.accept()
        print(f"Connection from {incomingAddress}\n")
        with incomingSocket:
            while True:
                data = incomingSocket.recv(1024).decode("utf-8")
                if not data:
                    break

                if data == "1":
                    response = averageMoisture()
                elif data == "2":
                    response = averageWaterUsage()
                elif data == "3":
                    response = highestElectric()
                else:
                    response = "Invalid query."

                incomingSocket.send(bytearray(response, encoding="utf-8"))
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