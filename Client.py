import socket
import pickle
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys
from Game import game


my_move = ''
opp_move = ''
source = ''
room_id = None  # default value for room_id
waiting_list = []   # hold waiting_list of all clients of a specific room
host = 'localhost'
port = 7005
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host,port))
message = None
clients_list = [] # holds all clients connected to the server to avoid duplicate names
# Listening to Server and Sending Nickname

GUI, _ = loadUiType('GUI.ui') # Load GUI file

# Creating MainGUI class
# Subclass QMainWindow to customize application's main window
class MainGUI(QMainWindow, GUI):
    def __init__(self, parent=None):
        super(MainGUI, self).__init__(parent)
        QMainWindow.__init__(self, parent)
        self.nicknames = []
        self.setupUi(self)
        self.handle_button()
        self.write = Write()
        self.receive = Receive()
        self.request = Request()
        self.reset_game = ResetGame()
        self.receive.start()
        self.tabWidget.tabBar().setVisible(False)

    # this function handles all push buttons of GUI
    def handle_button(self):
        self.pushButton.clicked.connect(self.send_to_server)  # start send_to_server function if pb is clicked

        # start onClicked function if item in list widget is clicked
        self.listWidget.itemDoubleClicked.connect(self.onClicked)
        self.listWidget_2.itemDoubleClicked.connect(self.onClicked)

    # this function works if the user has entered a nickname
    def send_to_server(self):
        global nickname, clients_list
        nickname = self.lineEdit.text() # set nickname variable to the text that user added in text bar
        if nickname not in clients_list and nickname != '':

            # set nickname for all tabs
            self.label_7.setText(nickname)
            self.label_8.setText(nickname)
            self.label_9.setText(nickname)

            # start write Thread
            self.write.start()

            # start receive Thread
            self.receive.start()
            self.tabWidget.setCurrentIndex(1) # set current tab to 1

            # when receive Thread returns output waitin_list function will be called
            self.receive.update_join_list.connect(self.waiting_list)

        # this condition avoid invalid input
        elif nickname == '':
            QMessageBox.information(self, "Info", 'Enter a valid Username !')

        # this condition avoid duplicated names
        else:
            QMessageBox.information(self, "Info", 'This Nickname exists \nChoose another one !')

    def waiting_list(self,vals):
        global nickname, waiting_list
        try:
            for val in vals:
                if val not in waiting_list:
                    if nickname != val:

                        # add list of clients received from the server to listWidget
                        self.listWidget.addItem(val)
                        self.listWidget_2.addItem(val)

                        # append_waiting list by clients to monitor all clients added to listWidget
                        waiting_list.append(val)

            # update waiting list number and send it to server
            data_frame = [('remaining',len(waiting_list) + 1,room_id)]
            data = pickle.dumps(data_frame) # dump data_frame to data
            client.sendall(data) # send data to server
        except:
            print('an error occurred')

    # this function removes clients from waiting list
    def remove_item(self,val):
        global nickname
        global waiting_list
        try:
            if nickname != val:
                x = waiting_list.index(val)
                print(f'this is index {x}')
                self.listWidget.takeItem(x)  # remove client from listWidget by giving index of client
                self.listWidget_2.takeItem(x)
                waiting_list.remove(val)  # remove client from waiting list

                # update waiting list number and send it to server
                data_frame = [('remaining',len(waiting_list) + 1,room_id)]
                data = pickle.dumps(data_frame)
                client.sendall(data)
        except:
            pass

    # this function works if the client send request to other client
    def onClicked(self,item):
        global opp
        opp = item.text() # item.text
        self.request.start()
        txt = f'Sending request to {item.text()}...'
        QMessageBox.information(self, "Info", txt)

    # this function handles incoming requests
    def approve(self,source):
        self.tabWidget.setCurrentIndex(2)
        self.label_5.setText(f'{source} wants to connect')
        for index, clients in enumerate(waiting_list):
            items = self.listWidget_2.item(index)
            items.setFlags(Qt.NoItemFlags)
        self.pushButton_2.clicked.connect(self.accept)  # connect to accept function if user accepted request
        self.pushButton_3.clicked.connect(self.refuse)   # connect to refuse function if user refused request

    def accept(self):
        global nickname, source
        data_frame = ['yes', nickname, source, 'response']
        data = pickle.dumps(data_frame)  # send accepted signal to server to start session
        client.sendall(data)

    def refuse(self):
        self.tabWidget.setCurrentIndex(1)
        data_frame = ['no', nickname, source, 'response']
        data = pickle.dumps(data_frame)  # send refused signal to server to start session
        client.sendall(data)

    # initiate session
    def initiate_session(self):
        self.tabWidget.setCurrentIndex(3)

        # connect to return back method if player pressed exit button
        self.commandLinkButton.clicked.connect(self.return_back)

        # connect to rock_move method if player pressed rock pb
        self.pushButton_rock.clicked.connect(self.rock_move)

        # connect to paper_move method if player pressed paper pb
        self.pushButton_paper.clicked.connect(self.paper_move)

        # connect to scissor_move method if player pressed scissor pb
        self.pushButton_scissors.clicked.connect(self.scissor_move)

    def rock_move(self):
        global opponent, my_move, opp_move
        frame = ('move', nickname, opponent, 'Rock')
        my_move = 'R'
        df = pickle.dumps(frame)
        client.sendall(df)  # send rock move to server
        self.disable_pb()   # disable pushbutton when player pressed pushbutton
        self.result(opp_move) # call result method to return the result


    def paper_move(self):
        global opponent, my_move, opp_move
        frame = ('move', nickname, opponent, 'Paper')
        my_move = 'P'
        df = pickle.dumps(frame)
        client.sendall(df) # send rock move to server
        self.disable_pb()
        self.result(opp_move)


    def scissor_move(self):
        global opponent, my_move, opp_move
        frame = ('move', nickname, opponent, 'Scissors')
        my_move = 'S'
        df = pickle.dumps(frame)
        client.sendall(df) # send rock move to server
        self.disable_pb()
        self.result(opp_move)


    def result(self, opp_move):
        global my_move
        if my_move and opp_move: # if both players move
            result = game(my_move[0], opp_move[0]) # return result from game method
            if result == True:
                self.reset_game.start()     # start reset_game Thread
                self.label_result.setText(f'You Win')
                self.reset_game.reset.connect(self.reset) # call reset method to reset the game
            elif result == False:
                self.reset_game.start()
                self.label_result.setText(f'You Lost')
                self.reset_game.reset.connect(self.reset)
            else:                                                # if both players enters the same move
                self.reset_game.start()
                self.label_result.setText(f'Tie Game')
                self.reset_game.reset.connect(self.reset)
            self.label_opponen_move.setText(f'Opponent Move {opp_move}')

    # if one player exit the game this function will be called to send 'session_ended to server'
    def return_back(self):
        global waiting_list, nickname
        waiting_list = []
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.tabWidget.setCurrentIndex(1)
        frame = ('session_ended', nickname, opponent, 'end')
        df = pickle.dumps(frame)
        client.sendall(df)  # send 'session_ended' signal to server

    # if the client received 'session_ended' from the sever end_session will be called
    def end_session(self):
        global room_id
        self.tabWidget.setCurrentIndex(1) # automatically return back to waiting list tab
        print('session ended')
        frame = ('session_ended', nickname, opponent, 'end')
        df = pickle.dumps(frame)
        client.sendall(df) # send 'session_end' signal to confirm that the session ended

    # reset the game automatically after 3 seconds when the game finished
    def reset(self, val):
        global my_move, opp_move
        if val == 'reset':
            my_move = ''    # reset moves
            opp_move = ''
            self.label_result.setText('') # remove text
            self.label_opponen_move.setText('')
            self.reset_game.exit()  # stop the thread
            self.pushButton_rock.setEnabled(True) # enable push button
            self.pushButton_paper.setEnabled(True)
            self.pushButton_scissors.setEnabled(True)

    # disable pushbutton after the player move
    def disable_pb(self):
        self.pushButton_rock.setEnabled(False)
        self.pushButton_paper.setEnabled(False)
        self.pushButton_scissors.setEnabled(False)

    # clear listWidget when initiating the game
    def clear_widget(self):
        self.listWidget.clear()
        self.listWidget_2.clear()


def main():
    global window
    app = QApplication(sys.argv)
    window = MainGUI()  # create an instance of MainGUI class
    window.show()   # show window
    app.exec_()  # execute the application


# receiving thread is handling all incoming messages from server
class Receive(QThread):
    update_join_list = pyqtSignal(list)

    def run(self):
        global message, source,window, nickname, opp_move, room_id,clients_list
        while True:

            # Receive Message From Server
            message = pickle.loads(client.recv(1024*8))

            # if incoming frame of index[0] is request this condition will be executed
            if message[0] == 'request':
                source = message[1]
                window.approve(source)  # call approve method to accept or refuse request

            # if incoming frame of index[0] is initiate this condition will be executed
            elif message[0] == 'initiate':
                global opponent
                frame = ['initiate now', nickname, message[1]]
                df = pickle.dumps(frame)
                client.sendall(df)  # send initiate signal to confirm initiation phase
                opponent = message[1]
                room_id = None
                waiting_list.clear()  # temporary remove clients from waiting_list
                window.clear_widget()
                window.initiate_session()  # calling initiate methode to start initiation

            # if opponent send his move this condition will be called
            # message format ('move', nickname, opponent, 'Rock')
            elif type(message) == tuple and message[0] == 'move':
                opp_move = message[3]
                # call result method to return the result of the game
                window.result(opp_move)

            # if 'end_session' signal received this condition will be executed
            # message format ('session_ended', nickname, opponent, 'end')
            elif type(message) == tuple and message[0] == 'session_ended':
                # call end_session method to close the session
                window.end_session()

            else:
                # this condition set the room_id for the client
                # message format [list_of_clients,[room_id]]
                if type(message[1]) == list and nickname in message[0]:
                    room_id = message[1][0]

                # this condition update the waiting list by receoving all clients with same room_id
                # message format list_of_clients,[room_id]]
                if type(message) != tuple and message[0] != 'id' and type(message[1]) == list and message[1][0] == room_id:
                    self.update_join_list.emit(message[0])

                # this condition call remove_item method if the server send signal to remove client
                elif type(message) == tuple and message[0] == 'remove' and message[2] == room_id:
                    window.remove_item(message[1])

                # when client connects to the server, server will send all clients to the client to avoid duplication
                if type(message[0]) == list and message[0] != 'id' and message[1] == 'list_clients':
                    clients_list = message[0]


# Write Thread class sends the nickname to the server
class Write(QThread):
    def run(self):
        global message, source, nickname
        msg = pickle.dumps(nickname)
        client.sendall(msg)


# Request Thread send request invitation to the client
class Request(QThread):
    def run(self):
        global opp
        target = ['target', nickname, opp]  # [msg_type, source, destination]
        if target[1] != target[2]:
            data = pickle.dumps(target)
            client.sendall(data)


# RestGame Thread reset the game after both players send their moves
class ResetGame(QThread):
    reset = pyqtSignal(str)

    def run(self):
        time.sleep(3)
        self.reset.emit('reset') # emit 'reset' keyword after 3 seconds

# run the code only if the program is the main program executed
if __name__ == '__main__':
    main()