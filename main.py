"""
    main.py\n
    Main code for the chat app peer. See instructions and docs folder for details.\n
    Group 6 of CS 4470 Fall 2024
"""

import sys
import socket
import threading

import modules.protocol.utilities as proto
import modules.protocol.constants as pconsts

DEFAULT_BACKLOG = 12

class Peer:
    def __init__(self, port: int) -> None:
        self.my_address = socket.gethostbyname(socket.gethostname())
        self.my_port = port
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # group of currently added connections, imitate a unique set
        self.connection_dict: dict[str, tuple[socket.socket, socket._RetAddress]] = {}
        # for holding both peer initiated and other initiated connection states
        self.connection_list: list[tuple[socket.socket, socket._RetAddress]] = []
        # for outgoing messages by our protocol
        self.proto_out = proto.Messager()

    def do_help_cmd(self):
        # show all required commands' descriptions
        print("1.help - Display this help message \n"
                    "2.myip - Display the IP address of the host\n"
                    "3.myport - Display the port number of the host\n"
                    "4.connect <destination> <port no> - \n"
                    "5.list - Display a numbered list of all the connections this process is part of\n"
                    "6.terminate <connection id> - Will terminate the connection\n"
                    "7.send <connection id> <message> - will send the message to the host on the connection\n"
                    "8.exit - Close the connection")
    
    def do_myip_cmd(self):
        print(f"My IP is: {self.my_address}")

    def do_myport_cmd(self):
        print(f"My port is: {self.my_port}")

    def do_connect_cmd(self, dest_addr_arg: str = None, port_arg: str = None):
        if dest_addr_arg is None or port_arg is None:
            print("Error: expected target address and port!")
            return

        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_addr = (dest_addr_arg, int(port_arg))
            temp_conn = (temp_socket, temp_addr)

            # validate connecting arguments by excluding duplicate or self-directed ones...

            if dest_addr_arg == self.my_address and port_arg == self.my_port:
                print("Error: self-connections disallowed.")
                return

            if self.connection_dict.get(dest_addr_arg) is not None:
                print("Error: cannot duplicate connection!")
                return
            
            if len(self.connection_dict) == 3:
                print("Error: cannot exceed 3 peer connections!")
                return

            temp_socket.connect(temp_addr)

            print(f"Connected to {dest_addr_arg}:{port_arg}")
            self.connection_list.append(temp_conn)
            self.connection_dict[dest_addr_arg] = temp_conn
        except Exception as err:
            print(f"Error: {err}")

    def do_list_cmd(self):
        displayed_id = 1
        for conn in self.connection_list:
            print("id:  IP address:\t\tPort no.")
            print(f"{displayed_id}:  {conn[1][0]}\t\t{conn[1][1]}")
            displayed_id += 1

    def do_terminate_cmd(self, id_arg: str = None):
        if id_arg is None:
            print("Error: expected peer ID!")
            return
        
        real_id_pos = int(id_arg) - 1

        if real_id_pos < 0 or real_id_pos >= len(self.connection_list):
            print("Error: invalid connection ID, cannot terminate it!")
            return

        target = self.connection_list[real_id_pos]

        # NOTE We get the socket to send TERMINATE message first. Then we send that to the selected peer for graceful notification before closing (thus that connection too!)
        self.proto_out.write_message(target[0], pconsts.PROTO_ACTION_TERMINATE, None)

        del self.connection_dict[target[1]]
        self.connection_list.remove(target)
    
    def do_send_cmd(self, id_arg: str, msg: str):
        if id_arg is None or msg is None:
            print("Error: expected ID and message!\n")
            return
        
        real_peer_cid = int(id_arg) - 1

        # validate send command arguments by two criteria: ID exists and len(msg) <= 100...
        if real_peer_cid < 0 or real_peer_cid >= len(self.connection_list):
            print("Error: invalid recipient ID!")
            return
        
        if len(msg) > pconsts.PROTO_MAX_CHAT_LENGTH:
            print("Error: message too long!")
            return
        
        for conn in self.connection_list:
            self.proto_out.write_message(conn[0], pconsts.PROTO_ACTION_SEND, [msg])

    def repl(self):
        while True:
            cmd_str = input("> ").strip().split(" ")

            if cmd_str[0] == "help":
                self.do_help_cmd()
            elif cmd_str[0] == "myip":
                self.do_myip_cmd()
            elif cmd_str[0] == "myport":
                self.do_myport_cmd()
            elif cmd_str[0] == "connect":
                self.do_connect_cmd(cmd_str[1], cmd_str[2])
            elif cmd_str[0] == "list":
                self.do_list_cmd()
            elif cmd_str[0] == "terminate":
                self.do_terminate_cmd(cmd_str[1])
            elif cmd_str[0] == "send":
                self.do_send_cmd(cmd_str[1], " ".join(cmd_str[2:]))
            elif cmd_str[0] == "exit":
                break
            else:
                print("Error: unknown command!")
        
        self.finalize()

    def run(self):
        # NOTE We setup listening socket for its usability...
        self.listen_socket.bind(self.my_address)
        self.listen_socket.listen(DEFAULT_BACKLOG)

        # NOTE We define local functions to contain connection handling logic since Python lambdas are less flexible (possibly limited to one-line functions)
        def handle_peer(args: tuple[socket.socket, socket._RetAddress]):
            """
                @brief Runnable function on Python thread for mainly recieving messages from other peers. See Protocol.md for messaging format details.
                @param args State of the currently handled peer connection.
            """
            protocol_util = proto.Messager()
            peer_sock, peer_addr = args
            try:
                while True:
                    verb, argv = protocol_util.read_message(peer_sock)

                    if verb == pconsts.PROTO_ACTION_TERMINATE:
                        print(f"Peer at {peer_addr} left the chat.")
                        # NOTE We must end this worker thread since its connection is dead.
                        break
                    elif verb == pconsts.PROTO_ACTION_SEND:
                        print(f"Message recieved from {peer_addr}"
                          f"Sender's port: {peer_addr[1]}"
                          f"Message: \"{' '.join(argv)}\"")
            except Exception as sock_err:
                print(f"Error: bad I/O on connection of {peer_addr}: {sock_err}")

            # NOTE By instructions, remove dead peer connection state after peer leaves!
            del self.connection_dict[peer_addr[0]]
            self.connection_list.remove(peer_addr)

        def handle_incoming():
            """
            @brief Runnable function on Python thread for only accepting peer connections to serve. A sub-thread is spawned for each connection after connection state is saved to the parent class.
            @param args: the listening socket accepting connections\n
            """
            try:
                while True:
                    # NOTE accept incoming peer connection to handle soon with a worker-like thread (see handle_peer)
                    new_conn = self.listen_socket.accept()
                    self.connection_dict[new_conn[0]] = new_conn
                    self.connection_list.append(new_conn)

                    threading.Thread(target=handle_peer, args=new_conn).start()
            except Exception as sock_err:
                print("Stopped listening for connections...")
        
        threading.Thread(target=handle_incoming).start()
        self.repl()

    def finalize(self):
        """
            For cleanup after REPL exiting: closes listening socket and its other accepted connections, etc.
        """
        self.listen_socket.close()

        # TODO send exiting / closing messages per protocol to all other peers for their notice
        for conn in self.connection_list:
            try:
                temp_sock = conn[0]
                self.proto_out.write_message(temp_sock, pconsts.PROTO_ACTION_TERMINATE, None)
                temp_sock.close()
            except Exception as io_err:
                pass

# NOTE We must begin the main code here under guarding if: no accidental runs on import in Python!
if __name__ == '__main__':
    # check input: invocation of peer program must have port argument after Python script
    if len(sys.argv) != 2:
        print("Invalid arguments!\nUsage: python main.py <port>")
        sys.exit(1)

    port_number = -1

    # only allow valid port numbers
    try:
        port_number = int(sys.argv[1])
    except TypeError as type_err:
        print(f"Error: {type_err}")
        sys.exit(1)

    if port_number <= 1024:
        print("Error: cannot use reserved port!")
        sys.exit(1)

    # start peer application by wrapper class
    app = Peer(port_number)
    app.run()
