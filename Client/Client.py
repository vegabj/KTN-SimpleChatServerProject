# -*- coding: utf-8 -*-
import socket
import json
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.server_port = server_port
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        self.msgParser = MessageParser()
        msgReceiver = MessageReceiver(self, self.connection)
        msgReceiver.start()

        print "INSTRUCTIONS\nUser must login first - type 'login <username>'\ntype 'help' for list over available commands\n\n"
        while self.connection:
            userinput = raw_input()
            if userinput == 'logout':
                self.disconnect()
            elif userinput == 'exit':
                exit()
            else:
                self.send_payload(userinput)
        
    def disconnect(self):
        print "Disconnecting client..."
        self.send_payload('logout')
        self.connection.close()

    def receive_message(self, message):
        print self.msgParser.parse(message)

    def send_payload(self, data):
        request = None
        if data.startswith("login"):
            request = {'request' : 'login', 'content' : data[6:] }
        elif data.startswith("logout"):
            request = { 'request' : 'logout', 'content' : None}
        elif data.startswith("msg"):
            request = {'request' : 'message', 'content' : data[3:]}
        elif data.startswith("names"):
            request = {'request' : 'names', 'content' : None}
        elif data.startswith("help"):
            request = {'request' : 'help', 'content' : None }
        else:
            print "did not recognize command"
        if request:
            self.connection.sendall(json.dumps(request))


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
