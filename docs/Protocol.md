# Chat Protocol Spec. 2

### Authors (Group 6)
Derek, Runyi, Kyle

### 1.0 Brief:
This document describes a mini specification of our protocol designed for Programming Project 1 of CS 4470.

### 2.0 Purpose:
Provide a simple, working application layer protocol that fulfills connection management and usage. This protocol will be text-based too for easier debugging.

### 3.0 Key Ideas:
 - Protocol is text-based.
 - Connections are stateful, depending on protocol actions and certain commands like `exit`.
 - Uses framed messages are line-formatted between newline delimiters, containing action verb and an argument list.
 - A dictionary per peer should track IPs by an ID. It's like a phonebook the peer has to talk to its friends!

### 4.0 Connection Lifecycle:
 - Create -> Active -> Terminate
 - A connection is created by the `connect` command.
 - A connection is active after creation. It can be used for chatting during this stage, specifically by the `send` command.
 - A connection is closed by the `terminate` command or on `exit`.

### 5.0 Protocol Types:
 - Verb: names network action by peer
 - Argument list: text delimited by single spaces until newline.

### 6.0 protocol:
This section describes how the protocol frames messages. Connections are managed or used relative to some required commands.

#### 6.1 "Ack":
For affirming when a connection protocol action succeeded, e.g connecting, sending a chat message, etc.
```
Action: "ACK"
OK-Flag: "true" / "false"
LF
```

#### 6.2 Connect:
Opens a connection and give the app instance's address to a peer. This cannot be run when the target address is to self or invalid.
```
Action: "CONN"
Sender-Addr: "IP:PORT"
Target-Addr: "IP:PORT"
LF
```

#### 6.3 Terminate One:
Closes a connection with a specific peer. This action can be repeated to all _other_ peers on exiting, and all other peers must act accordingly. They must remove that exiting peer's IP from their dictionaries. However, this action must fail on an invalid address (given from local dictionary's ID)
```
Action: "TERM"
Exiting-Addr: "IP:PORT"
LF
```

#### 6.4 Send chat action:
Send a message to a peer. This cannot be done with a closed / absent connection.
```
Action: "CHAT"
Sender-Addr: "IP:PORT"
Message: "..." // quotes necessary
LF
```

#### 7.0 Other Notes:
The CLI command choices of `help`, `myip`, `myport`, and `list` can be implemented without the protocol. This is because each peer can store important data: IP, PORT, and the dictionary of peer addresses.

### 8.0 Examples:
 - Note 1: LF is the '\n' character which ends any message.
 - Note 2: 127.0.0.1:8080 is the fake sender.
 - Note 3: 127.0.0.1:8081 is the fake reciever or disconnect target.

#### 8.1 Sample messages:
 - ACK: `ACK true LF`
 - CONN: `CONN 127.0.0.1:8080 127.0.0.1:8081 LF`
 - TERM: `TERM 127.0.0.1:8080 LF`
 - SEND: `SEND 127.0.0.1:8081 LF`
