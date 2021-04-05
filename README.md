# IAS_Chat Package

This is a Software written for an exercise of the "Internet and Security" lecture at the University of Basel
This Version consists of 5 executable Scripts, that are executed to start chatting with one of three Methods.

## TCP Chat
### Execute
Each comm-partner needs to execute /src/iaschat/tcp_direct.py ans give Ip, Port of the communicationpartner as well as 
the port you want to be reachable at.
**Example:** python3 tcp_direct.py -ip localhost -port 2020 -myport 2021

### Usage
When the other side is not reachable the Program waits for incoming Connections at "myport" and accepts it when there is one
When the other side is reachable, then you can immediately start chatting: Just start typing and send messages with hitting "Enter"

## UDP Chat
The Constellation for the one-to-one chat consists of a Server and two Clients. The Server acts as a register where clients can register with a unique
nickname and can request the connection-information from other nicknames to chat with each other.

### Execute 

**Server**: give Own IP/Port,  Example: python3 udp_server.py -ip localhost -port 2020
            
**Client**: give Servers IP/Port and own Port(you want to be reachable at), Example: python3 udp_server.py -ip localhost -port 2020
-myport 2021

### Usage
When the server is started no further interaction is required.

When the Client is started, you can type in Commands and Messages:
**cmd:register MYNAME**: Register at the Server with a unique Nickname, severs response will tell you if the name is occupied or
you successfully registered.

**cmd:request OTHERNAME**: The Servers Response is empty when the name is unknown and the information (ip, port) associated 
with the name, if registered on Server. If so, your Client Script sends a direct connection request to the other client.
The Other Client then sees the incoming request and is also setup to text with the other client.

When Connected, all things except the commands are send as messgaes to the other client.

## UDP Group Chat
### Execute
### Usage