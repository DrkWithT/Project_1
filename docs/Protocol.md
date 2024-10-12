# Chat Protocol Spec. 1

### Authors (Group 6)
Derek, Runyi, Kyle

### 1.0 Brief:
This document describes a mini specification of our protocol designed for Programming Project 1 of CS 4470.

### 2.0 Purpose:
Provide a reliable and simple application layer protocol that fulfills connection management and usage. This protocol will be text-based for simplicity.

### 3.0 Key Ideas:
 - Protocol is text based.
 - Connections are stateful, changing their state upon actions such as `connect`, `terminate`, or `exit`.
 - A dictionary per peer should track IPs by an ID. It's like a phonebook the peer has to talk to its friends!

### 4.0 Connection Lifecycle:
 - Create -> Active -> Terminate
 - A connection is created by the `connect` command.
 - A connection is active after creation. It can be used for chatting during this stage, specifically by the `send` command.
 - A connection is closed by the `terminate` command or multiple to a peer by `exit`. 

### 5.0 protocol:
This section describes how the protocol frames messages. Connections are managed or used relative to some required commands.
 - The "TERMINATE" string is sent on termination of a peer's connection to the host.
 - The chat messages contain a sequence of pure ASCII bytes including spaces between words after the command name.
 - The connection messages contain the stringified port number of the connecting peer so that the legitimate port is known in the connections dictionary.

#### Other Notes:
The CLI command choices of `help`, `myip`, `myport`, and `list` can be implemented without the protocol. This is because each peer can already store some important state: IP, PORT, and the dictionary of peer addresses.
