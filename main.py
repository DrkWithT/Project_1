"""
    main.py
    Main code for the chat app peer. See instructions and docs folder for details.
    Group 6 of CS 4470 Fall 2024
"""
import socket
import threading
import sys
import select

def command_help():
    help_message = ("1.help - Display this help message \n"
                    "2.myip - Display the IP address of the host\n"
                    "3.myport - Display the port number of the host\n"
                    "4.connect <destination> <port no> - \n"
                    "5.list - Display a numbered list of all the coonections this process is part of\n"
                    "6.terminate <connection id> - Will terminate the connection\n"
                    "7.send <connection id> <message> - will send the message to the host on the connection\n"
                    "8.exit - Close the connection")
    return help_message


def command_myip():
    ## getting the hostname by socket.gethostname() method
    hostname = socket.gethostname()
    print(hostname)
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def start_server(port):
    server_side = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_side.bind((command_myip(), int(port)))
    server_side.listen(5)

    print(f"Server start, ip: {command_myip()}, port: {port}")

    def connect_link():
        pass

    while True:
        command = input().strip().split(" ")
        print(command)

        if command[0] == "help":
            print(command_help())
        elif command[0] == "myip":
            print(command_myip())
        elif command[0] == "myport":
            print(f"The port number is {port}")


    sys.exit(0)

if __name__ == '__main__':
    # start main code here
    if len(sys.argv) != 2:
        print("Wrong format, please re-enter")
        sys.exit(1)

    port_number = sys.argv[1]
    start_server(port_number)

