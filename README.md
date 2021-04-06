# IAS_Chat Package

This is a Software written for an exercise of the "Internet and Security" lecture at the University of Basel
This Version consists of 5 executable Scripts, that are executed to start chatting with one of three Methods.

**Package available at**: https://test.pypi.org/project/IAS-Chat-rt/

## TCP Chat
### Execute
Each comm-partner needs to execute /src/iaschat/tcp_direct.py ans give Ip, Port of the communicationpartner as well as 
the port you want to be reachable at.

**Example:** python3 tcp_direct.py -ip localhost -port 2020 -myport 2021

**With Package installed:** python3 -m iaschat.tcp_direct -ip localhost -port 2020 -myport 2021

### Usage
When the other side is not reachable the Program waits for incoming Connections at "myport" and accepts it when there is one
When the other side is reachable, then you can immediately start chatting: Just start typing and send messages with hitting "Enter"

## UDP Chat
The Constellation for the one-to-one chat consists of a Server and two Clients. The Server acts as a register where clients can register with a unique
nickname and can request the connection-information from other nicknames to chat with each other.

### Execute 

**Server**: give Own IP/Port,  Example: python3 udp_server.py -ip localhost -port 2020

**With Package installed:** python3 -m iaschat.udp_server -ip localhost -port 2020
            
**Client**: give Servers IP/Port and own Port(you want to be reachable at), Example: python3 udp_client.py -ip localhost -port 2020 -myport 2021

**With Package installed:** python3 -m iaschat.udp_client -ip localhost -port 2020 -myport 2021

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
The groupchat version of the udp-chat also consists of a server and several clients. The Server now serves as a register for all the Groups
available. The clients can register itself with names, can create groups, ask for all groups available and enter one

### Execute
**Server:** Example: python3 udp_groupchat_server.py -p 1234, gives port of the server

**With Package installed:** python3 -m iaschat.udp_groupchat_server -p 1234

**Client:** Example: python3 udp_groupchat_client.py -p 1234 -ip localhost -mp 5678, gives port and Ip of the Server as well as the
own port

**With Package installed:** python3 -m iaschat.udp_groupchat_client -p 1234 -ip localhost -mp 5678

### Usage
**cmd:register MYNICKNAME**

**cmd:groups** Servers response is a list with the names of existing groups

**cmd:create NAME IP PORT** Server Creates a Group if ip and name are not used by any other group on the server

**cmd:enter NAME** Server sends group-info if group exists. Client then reconfigures socket to work on Group Multicast

After that one can just type and send messages.

## Task 3
To add the feature, that one can list all members of a group, one could solve it on application-level:
One Could add a new command to the ClientProtocol. This command would lead all the clients connected to the Multicast to
send their name/information to the multicast. So all the Clients will know the names of each other.
