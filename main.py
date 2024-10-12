"""
    main.py
    Main code for the chat app peer. See instructions and docs folder for details.
    Group 6 of CS 4470 Fall 2024
"""
import socket
import threading
import sys
import time

# Store connection information
connections = {}
connections_lock = threading.Lock()
my_port = None
my_ip = None
connection_index = 0

def handle_client(conn, addr):
    terminate_flag = False
    try:
        while True:
            message = conn.recv(4096).decode("utf-8")
            if not message:
                break
            if message == "TERMINATE":
                terminate_flag = True
                break
            print(f"\nMessage received from {addr[0]}")
            print(f"Sender’s Port: {addr[1]}")
            print(f"Message: \"{message}\"")
            print("> ", end='', flush=True)

    except Exception as e:
        print(f"\nError with {addr[0]}:{addr[1]} - {e}")

    finally:
        if terminate_flag:
            with connections_lock:
                conn.close()
                connection_id = next((cid for cid, c in connections.items() if c[0] == conn), None)
                if connection_id:
                    del connections[connection_id]
            print(f"\nConnection from {addr[0]}:{addr[1]} closed.")
            print("> ", end='', flush=True)

def command_help():
    help_message = ("1.help - Display this help message \n"
                    "2.myip - Display the IP address of the host\n"
                    "3.myport - Display the port number of the host\n"
                    "4.connect <destination> <port no> \n"
                    "5.list - Display a numbered list of all the coonections this process is part of\n"
                    "6.terminate <connection id> - Will terminate the connection\n"
                    "7.send <connection id> <message> - will send the message to the host on the connection\n"
                    "8.exit - Close the connection")
    return help_message

def command_myip():
    # ## getting the hostname by socket.gethostname() method
    # hostname = socket.gethostname()
    # ## getting the IP address using socket.gethostbyname() method
    # ip_address = socket.gethostbyname(hostname)
    available_addresses = socket.gethostbyname_ex(socket.gethostname())[2]

    # set IP result... default is loopback ONLY IF no other alternatives are found!
    ip_address = "127.0.0.1"

    # traverse list of available addresses for host machine...
    for temp_ip in available_addresses:
        if temp_ip != "127.0.0.1":
            ip_address = temp_ip

    return ip_address

def command_send(connection_id, message):
    try:
        connection_id = int(connection_id)
        with connections_lock:
            if connection_id in connections:
                conn = connections[connection_id][0]
                conn.send(message.encode("utf-8"))
                print(f"Message sent to connection ID {connection_id}.")
            else:
                print(f"Connection ID {connection_id} does not exist.")

    except Exception as e:
        print(f"Error sending message: {e}")

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def is_valid_port(port):
    try:
        # Convert to integer and check if it's in the valid range
        port = int(port)
        return 1 <= port <= 65535
    except ValueError:
        # Not a number
        return False

def command_connect(target_ip, port):
    global connection_index
    if not is_valid_ip(target_ip) or not is_valid_port(port):
        print("Error: IP address or port number is invalid.")
        return

    if target_ip == my_ip and int(port) == int(my_port):
        print("Error: Cannot connect to self.")
        return

    with connections_lock:
        for conn in connections.values():
            if conn[1][0] == target_ip and int(conn[1][1]) == int(port):
                print("Error: Duplicate connection.")
                return

    try:
        connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_socket.connect((target_ip, int(port)))

        connect_socket.send(str(my_port).encode('utf-8'))
        peer_listening_port = connect_socket.recv(1024).decode('utf-8')

        with connections_lock:
            connection_index += 1
            connections[connection_index] = (connect_socket, (target_ip, peer_listening_port))

        print(f"Connected to {target_ip}:{peer_listening_port} as ID: {connection_index}")
        threading.Thread(target=handle_client, args=(connect_socket, (target_ip, peer_listening_port))).start()
    except ConnectionRefusedError as e:
        if e.errno == 10061:
        # Handle the case where no service is running on the specified port
            print(f"No service is running on {target_ip}:{port}, try another one.")
    except Exception as e:
        print(f"Connection error: {e}")


def command_terminate(connection_id):
    try:
        connection_id = int(connection_id)
        with connections_lock:
            if connection_id in connections:
                conn, addr = connections[connection_id]
                conn.send("TERMINATE".encode('utf-8'))
                time.sleep(1)  # Allow time for the message to be sent and received

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

                del connections[connection_id]
                print(f"Connection ID {connection_id} terminated.")
            else:
                print(f"Connection ID {connection_id} does not exist.")

    except Exception as e:
        print(f"\nError terminating connection: {e}")

def command_exit(server_socket):
    # Close all existing connections
    with connections_lock:
        for cid in list(connections.keys()):
            conn, addr = connections[cid]
            try:
                conn.send("TERMINATE".encode('utf-8'))
                time.sleep(1)  # Allow time for the message to be sent and received
                conn.shutdown(socket.SHUT_RDWR) # check it later
                conn.close()
                del connections[cid]
            except:
                pass

    print("Shutting down the server...")
    sys.exit(0)

def command_list():
    """Display a list of all active connections."""
    with connections_lock:
        if connections:
            print("id: IP Address       Port No.")
            for cid, (conn, addr) in connections.items():
                print(f"{cid}:   {addr[0]:<15} {addr[1]}")
        else:
            print("No active connections.")

def start_ServerClient(port):
    global my_ip, my_port
    my_port = port
    my_ip = command_myip()

    server_side = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_side.bind((command_myip(), int(port)))
    server_side.listen(5)

    print(f"Server started, listening on: {my_ip}:{port}")

    # start a thread to accept one client connection
    def accept_connect():
        #make it keep running
        global connection_index
        while True:
            conn, addr = server_side.accept()

            peer_listening_port = conn.recv(1024).decode('utf-8')
            conn.send(str(my_port).encode('utf-8'))

            with connections_lock:
                connection_index += 1
                connections[connection_index] = (conn, (addr[0], peer_listening_port))

            threading.Thread(target=handle_client, args=(conn, (addr[0], peer_listening_port))).start()
            print(f"\nAccepted connection from {addr[0]}:{peer_listening_port} as ID: {connection_index}")
            print("> ", end='', flush=True)

    #start a thread to keep running and accept one client connection, so we can continue the code
    threading.Thread(target=accept_connect, daemon=True).start()

    while True:
        command = input("> ").strip()
        if not command:
            continue
        parts = command.split()
        cmd = parts[0]

        if cmd == "help":
            print(command_help())
        elif cmd == "myip":
            print(my_ip)
        elif cmd == "myport":
            print(f"The port number is {my_port}")
        elif cmd == "connect" and len(parts) == 3:
            command_connect(parts[1], parts[2])
        elif cmd == "send" and len(parts) >= 3:
            connection_id = parts[1]
            message = ' '.join(parts[2:])
            command_send(connection_id, message)
        elif cmd == "terminate" and len(parts) == 2:
            command_terminate(parts[1])
        elif cmd == "list":
            command_list()
        elif cmd == "exit":
            command_exit(server_side)
        else:
            print("Invalid command. Type 'help' for a list of commands.")

if __name__ == '__main__':
    # start main code here
    # if command length nor right then exit
    if len(sys.argv) != 2:
        print("Wrong format, please re-enter. Usage: ./chat <port no.>")
        sys.exit(1)

    port_number = sys.argv[1]
    start_ServerClient(port_number)

