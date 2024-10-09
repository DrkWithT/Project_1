"""
    constants.py\n
    Implements constants for custom chat protocol.
    Derek T. - Group 6 of CS 4470 Fall 2024
"""

# protocol msg. punctuation #

PROTO_MSG_DELIM = "\n"
PROTO_MSG_ARGS_DELIM = " "
PROTO_MSG_ADDR_DELIM = ":"

# protocol actions #

PROTO_ACTION_ACK = "ACK"
PROTO_ACTION_CONNECT = "CONN"
PROTO_ACTION_TERMINATE = "TERM"
PROTO_ACTION_SEND = "CHAT"

# other constants (see directions) #
PROTO_MAX_CHAT_LENGTH = 100
