"""
    main.py
    Main code for the chat app peer. See instructions and docs folder for details.
    Group 6 of CS 4470 Fall 2024
"""
import socket
import threading
import sys
import select

#storing connection
connection_list = []


def handle_client(conn, addr):
    print(f"New connection from {addr} connected.")
    connection_list.append(conn)
    while True:
        # might change this part, not sure
        try:
            message = conn.recv(4096).decode("utf-8")
            if not message:
                break
            message = f"Message received: {message}"
            conn.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Error {e}")
    conn.close()

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
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def command_send(connection_id, message):
    try:
        #-1 because of the index
        print(connection_list)
        connection = connection_list[int(connection_id) - 1]
        connection[0].send(message.encode("utf-8"))
        print(f"Message sent")
    except Exception as e:
        print(f"Error {e}")

def command_connect(target_ip, port):
    try:
        connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_socket.connect((target_ip, int(port)))
        print(f"Connected to {target_ip}:{port}")

        connection_list.append(connect_socket)
    except Exception as e:
        print(f"Error {e}")

def commend_terminate(connection_id):
    try:
        connection = connection_list[int(connection_id) - 1]
        connection[0].close()
    except Exception as e:
        print(f"Error {e}")

def start_ServerClient(port):
    server_side = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_side.bind((command_myip(), int(port)))
    server_side.listen(5)

    print(f"Server start, listening on:{command_myip()}:{port}")

    # start a thread to accept one client connection
    def accept_connect():
        #make it keep running
        while True:
            conn, addr = server_side.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"Accepted connection from {addr}")

    #start a thread to keep running and accept one client connection, so we can continue the code
    threading.Thread(target=accept_connect).start()

    while True:
        command = input("> ").strip().split(" ")

        if command[0] == "help":
            print(command_help())
        elif command[0] == "myip":
            print(command_myip())
        elif command[0] == "myport":
            print(f"The port number is {port}")
        elif command[0] == "connect":
            command_connect(command[1], command[2])
        elif command[0] == "send":
            command_send(command[1], command[2])


    sys.exit(0)

if __name__ == '__main__':
    # start main code here
    # if command length nor right then exit
    if len(sys.argv) != 2:
        print("Wrong format, please re-enter")
        sys.exit(1)

    port_number = sys.argv[1]
    start_ServerClient(port_number)
