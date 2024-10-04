import socket
import threading
import sys

# Store connection information
connections = {}
connections_lock = threading.Lock()
my_port = None
my_ip = None

def handle_client(conn, addr):
    while True:
        try:
            message = conn.recv(4096).decode("utf-8")
            if not message:
                break
            if message == "TERMINATE":
                print(f"\nConnection terminated by {addr[0]}:{addr[1]}")
                break
            print(f"\nMessage received from {addr[0]}")
            print(f"Sender's Port: {addr[1]}")
            print(f"Message: \"{message}\"")
            print("> ", end='', flush=True)
        except Exception as e:
            print(f"Error: {e}")
            break
    conn.close()
    # Remove connection from the list
    with connections_lock:
        for cid, (c_conn, c_addr) in list(connections.items()):
            if c_conn == conn:
                del connections[cid]
                break
    print(f"Connection from {addr} closed.")

def command_help():
    return (
        "1. help - Display this help message\n"
        "2. myip - Display the IP address of the host\n"
        "3. myport - Display the port number of the host\n"
        "4. connect <destination> <port no> - Connect to another peer\n"
        "5. list - Display a numbered list of all connections\n"
        "6. terminate <connection id> - Terminate the connection\n"
        "7. send <connection id> <message> - Send a message to a peer\n"
        "8. exit - Close all connections and exit the program"
    )

def command_myip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def command_send(connection_id, message):
    connection_id = int(connection_id)
    with connections_lock:
        if connection_id in connections:
            conn = connections[connection_id][0]
            conn.send(message.encode("utf-8"))
            print(f"Message sent to connection ID {connection_id}.")
        else:
            print(f"Connection ID {connection_id} does not exist.")

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def command_connect(target_ip, port):
    if not is_valid_ip(target_ip):
        print("Error: Invalid IP address.")
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
        # Exchange listening ports
        connect_socket.send(str(my_port).encode('utf-8'))
        peer_listening_port = connect_socket.recv(1024).decode('utf-8')

        with connections_lock:
            connection_id = len(connections) + 1
            connections[connection_id] = (connect_socket, (target_ip, peer_listening_port))
        print(f"Connected to {target_ip}:{peer_listening_port} as ID: {connection_id}")

        threading.Thread(target=handle_client, args=(connect_socket, (target_ip, peer_listening_port))).start()
    except Exception as e:
        print(f"Error: {e}")

def command_terminate(connection_id):
    connection_id = int(connection_id)
    with connections_lock:
        if connection_id in connections:
            conn = connections[connection_id][0]
            # Send termination message
            try:
                conn.send("TERMINATE".encode('utf-8'))
            except:
                pass
            conn.close()
            del connections[connection_id]
            print(f"Connection ID {connection_id} terminated.")
        else:
            print(f"Connection ID {connection_id} does not exist.")

def command_list():
    with connections_lock:
        if connections:
            print("id: IP Address       Port No.")
            for cid, (conn, addr) in connections.items():
                print(f"{cid}: {addr[0]:<15} {addr[1]}")
        else:
            print("No active connections.")

def start_server_client(port):
    global my_ip, my_port
    my_port = port
    my_ip = command_myip()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((my_ip, int(port)))
    server_socket.listen(5)

    print(f"Server started, listening on: {my_ip}:{port}")

    def accept_connections():
        while True:
            conn, addr = server_socket.accept()
            # Exchange listening ports
            peer_listening_port = conn.recv(1024).decode('utf-8')
            conn.send(str(my_port).encode('utf-8'))

            with connections_lock:
                connection_id = len(connections) + 1
                connections[connection_id] = (conn, (addr[0], peer_listening_port))
            threading.Thread(target=handle_client, args=(conn, (addr[0], peer_listening_port))).start()
            print(f"Accepted connection from {addr[0]}:{peer_listening_port} as ID: {connection_id}")

    threading.Thread(target=accept_connections, daemon=True).start()

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
            with connections_lock:
                for cid in list(connections.keys()):
                    command_terminate(cid)
            sys.exit(0)
        else:
            print("Invalid command. Type 'help' for a list of commands.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong format, please re-enter. Usage: ./chat <port no.>")
        sys.exit(1)

    port_number = sys.argv[1]
    start_server_client(port_number)
