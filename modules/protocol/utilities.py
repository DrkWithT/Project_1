"""
    utilities.py\n
    Implements reader-writer class for application level protocol from `docs/Protocol.md`.\n
    Derek T. - Group 6 of CS 4470 Fall 2024\n
    Source: https://realpython.com/python-sockets/
"""

import modules.protocol.constants as proto_consts
import socket as sock

MAX_RECV_SIZE = 1024

class Messager:
    def __init__(self):
        pass

    def read_raw_message(self, socket: sock.socket):
        # read raw bytes
        data = socket.recv(MAX_RECV_SIZE)

        if not data:
            return (False, None)
        
        # convert bytes to text, delimited by '\n'
        return (True, data.decode('utf-8').split(proto_consts.PROTO_MSG_DELIM)[0])

    def read_message(self, socket: sock.socket):
        read_ok, raw_msg = self.read_raw_message(socket)

        # check read flag and discard msg if it fails for correctness
        if not read_ok:
            return None
        
        msg_pieces = raw_msg.split(proto_consts.PROTO_MSG_ARGS_DELIM)
        action = msg_pieces[0]
        args = msg_pieces[1:]

        return (action, args)

    def write_message(self, socket: sock.socket, verb: str, args: list[str] | None):
        # format message as "verb arg1 arg2...\n"
        framed_args = None
        framed_msg = None

        if args is not None:
            framed_args = " ".join(args)
            framed_msg = f"{verb} {framed_args}\n"
        else:
            framed_msg = f"{verb} \n"
        
        msg_bytes = framed_msg.encode()

        # write entire formatted message from before
        socket.sendall(msg_bytes)
