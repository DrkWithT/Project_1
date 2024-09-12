# Chat Protocol Spec. 1

### Authors: Group 6 (Derek, Runyi, Kyle)

### 1.0 Brief:
This document describes a mini specification of our protocol designed for Programming Project 1 of CS 4470.

### 2.0 Purpose:
Provide a reliable and simple application layer protocol that fulfills connection management and usage. This protocol will not be text-based since extra or mixed spacing can create confusion in parsing messages.

### 3.0 Key Ideas:
 - Protocol is binary.
 - Connections are stateful, changing their data upon actions. 
 - Uses framed messages follow action code, payload.
 - Types have a special binary encoding: Type-Code, Payload 
    - Int, String
 - A dictionary per peer should track IPs by an ID. It's like a phonebook the peer has to talk to its friends!

### 4.0 Connection Lifecycle:
 - Create -> Active -> Terminate
 - A connection is created by the `connect` command.
 - A connection is active after creation. It can be used for chatting during this stage, specifically by the `send` command.
 - A connection is closed by the `terminate` command. 

### 5.0 Protocol Types:
 - Cap (0x00): 2 bytes of `0x00 0x00` ending any message
 - Bool (0x01): byte representing true/false as `0x01 or 0x00`
 - Int (0x02): 2-byte short
 - Str (0x03): Int length N & then N ASCII characters 

### 6.0 protocol:
This section describes how the protocol frames messages. Connections are managed or used relative to some required commands.

#### 6.1 Connect:
Opens a connection and give the app instance's address to a peer. This cannot be run when the target address is to self or invalid.
```
Action: Int (0x1)
Target-Addr: Str (IP:PORT)
Cap
```

#### 6.2 Terminate One:
Closes a connection with a specific peer. This action can be repeated to all _other_ peers on exiting, and all other peers must act accordingly. They must remove that exiting peer's IP from their dictionaries. However, this action must fail on an invalid address (given from local dictionary's ID)
```
Action: Int (0x2)
Exiting-Addr: Str (IP:PORT)
Cap
```

#### 6.3 Send chat action:
Send a message to a peer. This cannot be done with a closed / absent connection.
```
Action: Int (0x3)
Sender-Addr: Str (IP:PORT)
Message: Str
Cap
```

#### Other Notes:
The CLI command choices of `help`, `myip`, `myport`, and `list` can be implemented without the protocol. This is because each peer can store important data: IP, PORT, and the dictionary of peer addresses.
