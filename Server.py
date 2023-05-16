import socket
from _thread import *
import pickle
import time

host = 'localhost'  # set IP address for the server
port = 7005         # set listening port
source = None
destination = None
dict = {}
room_dict = {}
room_info = [(0,4)]
clients_id = {}
room_id = 0      # room_id is a unique number for each room
start = 0   # start filling clients on waiting list by room_id of 0
end = start + 6  # end variable is the limit of waiting list, 6 means max of waiting list clients


# AF_INET refers to the address-family ipv4 and SOCK_STREAM means connection-oriented TCP protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port)) # # binding host and port
server.listen() # put the socket into listening mode: empty parentheses to listen to unlimited clients
print("waiting for connection")


def client_threading(communication_socket, dict, nickname, room_id): # start threading for each client individually
    data = pickle.dumps(['id', room_id])    # dump information to data
    comm.sendall(data)   # send pickled date to client

    # start initiate function session where both player starts to play
    def initiate_connection(source, destination):
        frame1 = ['initiate', source]  # frame of player1, initiate keyword means to force player1 to init phase
        frame2 = ['initiate', destination] # frame of player2, initiate keyword means to force player1 to init phase
        data1 = pickle.dumps(frame1)
        data2 = pickle.dumps(frame2)
        dict[source][0].sendall(data2) # send the frame to player1
        dict[destination][0].sendall(data1) # send the frame to player1

        while True:
            try:
                msg = pickle.loads(communication_socket.recv(1024 * 4)) # msg received from clients

                # this condition responsible for forwarding move messages between players
                if type(msg) == tuple:          # format of incoming message ('move', nickname, opponent, 'Rock')
                    src = dict[msg[2]]          # grep index 2 of msg which gives opponent socket
                    data = pickle.dumps(msg)
                    src[0].sendall(data)        # forward received message to the other client

                    # this condition works if one of players exit the game
                    if msg[0] == 'session_ended':  # message format ('session_ended', nickname, opponent, 'end')
                        dist = dict[msg[2]]        # msg[2] is the opponent socket
                        data = pickle.dumps(msg)
                        dist[0].sendall(data)      # send 'session_ended signal' to other player to close session
                        relocate(nickname, msg[2])  # relocate the client again to waiting list after exit
                        recv()                       # return back again to recv() function
            except:
                print('A serious error occurred')

                # disconnect if the other player lost connection
                disconnect(nickname, destination, dict[destination][0])
                break

    # this function send request game signals between players
    def request_connection(dist_socket, source):
        frame = ['request', source, 1]  # 'request' keyword is a special signal to request a game
        data = pickle.dumps(frame)
        dist_socket.sendall(data)       # send request to the other player
        recv()

    # this function is responsible to receive any incoming messages from clients
    def recv():
        try:
            global source, destination, room_dict, room_info
            while True:
                frame = pickle.loads(communication_socket.recv(1024 * 4))
                if frame[0] == 'yes' or frame[0] == 'initiate now':  # if client accepted invitation session will start
                    print(f'Connection Initiated... for nickname {nickname}')

                    # temporarily remove clients from waiting list after start session
                    remove_client(nickname, room_id, 1)

                    # start initiate function between two players
                    initiate_connection(frame[1], frame[2])
                    print(f'breaking {nickname}')
                    break

                # if 'target' signal received that means one client sent invitation to other client
                elif frame[0] == 'target':   # message format ['target', source, destination]
                    dist_socket = dict[frame[2]][0]   # grep socket of destination client
                    destination = dist_socket
                    source = dict[frame[1]][0]
                    request_connection(dist_socket, frame[1]) # send request frame to client
                    break

                # this condition is responsible for indicate empty location on each room so that the server determine
                # where to distribute new clients
                # message format [('remaining',len(waiting_list) + 1,room_id)]
                elif type(frame[0]) == tuple and frame[0][0] == 'remaining':

                    # room_dict is a dictionary for room where keys is nickname and values is number of clients in room
                    room_dict[frame[0][2]] = frame[0][1]
                    room_info = []
                    for roomID, remaining in room_dict.items():

                        # room_info sorts a list of tuples of (room_id, empty_locations)
                        room_info.append((roomID,6 - remaining))  # 6 means max of waiting list clients
                        # sort room_info by second value x[1] (empty location) of tuple
                        room_info.sort(key= lambda x: x[1])
                        room_info.reverse() # organize the list in descending order so that the first tuple is the top
                        # priority room_id as it has the most empty locations for clients



        except:
            try:
                 # if the client lost connection remove function should be called to remove the client.
                remove_client(nickname,room_id, 0)
            except:
                pass

    # call recv() function to receive incoming messages
    recv()


while True:
    # this function will broadcast clients name to all clients connected to specif room
    def send_by_id(clients_id, room_id):
        list_of_clients = []
        for name, roomID in clients_id.items():
            if room_id == roomID[0]:
                list_of_clients.append(name)    # add all clients with the same room id to the list
        data = pickle.dumps([list_of_clients,[room_id]])
        for client_socket in clients_socket:
            client_socket.sendall(data)  # broadcast clients and room id to all clients

    # this functions helps to distribute room_id for each client fairly
    def relocate(nickname, opponent):
        global room_id, start, end
        if room_info[0][0] == None:     # if room info has invalid tuple it should be deleted
            del room_info[0]

        # if room_info has tuples and shows an empty locations on room, therefore new room_id will not be created
        # and the current client shall be distributed to existing room.
        if len(room_info) >= 1 and room_info[0][1] > 0:
            room_id = room_info[0][0]  # room_id will take the first value of the tuple

            # check if this is a new client not existing one
            if nickname not in clients_id.keys():
                # clients_id dictionary stores keys: nickname with values: room_id
                clients_id[nickname] = [room_id]   # create a room_id for this client

                # this condition works when two clients exit the game and back to waiting list, so the client should
                # create a new room_id to him and his opponent
            if opponent != None and opponent not in clients_id.keys():
                clients_id[opponent] = [room_id]

            # execute this function
            send_by_id(clients_id, room_id)

        else:
            if len(clients_id.keys()) >= end:   # if the rooms have no empty locations this condition wil be executed

                # shift start to end for the new room
                start = end

                # offset end by 6 for the max capacity of waiting list
                end = start + 6

                # create new room_id
                room_id += 1

            clients_id[nickname] = [room_id]

            # send the new room_id to new clients
            data = pickle.dumps([list(clients_id.keys())[start:end], [room_id]])
            for client_socket in clients_socket[:]:
                client_socket.sendall(data)
    try:
        comm, address = server.accept()     # Establish connection with client.
        print(f'address {address} connected')

        # send current clients connected to the server to the new client to avoid duplicated clients
        data = pickle.dumps([list(dict.keys()), ('list_clients')])  # dump the list to data variable
        comm.sendall(data)   # send the data

        # the server receive the client username
        nickname = pickle.loads(comm.recv(1024))
        dict[nickname] = [comm]  # this dictionary stores keys 'clients' and values 'communication sockets'
        clients_socket = [i[0] for i in dict.values()]
        relocate(nickname, None)  # start relocate client
        print(f'starting with {nickname} {room_id}')

        # start a thread of client
        start_new_thread(client_threading, (comm, dict, nickname, room_id))
    except:
        print('An error occurred')


    def remove_client(nickname, room_id, status): # status (0) means lost connection abd
        # status (1) means temporary in a game
        global start, end
        if status == 0:
            try:
                # remove client from all dictionaries if connectio is lost
                clients_socket.remove(dict[nickname][0])
                del dict[nickname]
                del clients_id[nickname]
            except:
                pass
        else:

            # dictionaries remove till players return back to waiting list
            del clients_id[nickname]

        for client_socket in clients_socket:

            # send 'remove' keyword to all client to remove them from waiting list
            data = pickle.dumps(('remove',nickname,room_id))
            client_socket.sendall(data)

    # this function called if one or both clients lost connection to server
    def disconnect(nickname,opponent, opponent_sckt):

        # end session if one or both client lost connection
        frame = ('session_ended', nickname, opponent, 'end')

        df = pickle.dumps(frame)

        # send 'session_ended' signal to other client to exit from session
        opponent_sckt.sendall(df)


