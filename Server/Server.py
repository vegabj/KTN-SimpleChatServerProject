# -*- coding: utf-8 -*-
import SocketServer
import json
import time
import datetime
import re
import signal

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""
#List over connections
clientsConnection = []
#List over used usernames
clientsUsernames = []
#Chat history
history = []

"""
Match only a-z, A-Z and 0-9, whole string must match
"""
namereg = re.compile("\A[a-zA-z0-9]+\B")

class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
    def handle(self):
    	"""
        This method handles the connection between a client and the server.
        """
        self.connection = self.request
        clientsConnection.append(self.connection)
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        
        self.daemon = True

        self.clientname = ''

        # Loop that listens for messages from the client
	while self.connection:
			received_json = self.connection.recv(4096)
			received_string = ""
			try:
				received_string = json.loads(received_json)
			except ValueError:
				break
			request = received_string['request']
			
			# ------------------------ Login handle ------------------------
			if request == 'login':
				if self.clientname == '':
					self.clientname = received_string['content']
					if self.isValidUserName(self.clientname):
						if self.clientname not in clientsUsernames:
							clientsUsernames.append(self.clientname)
							self.sendResponse('info','Login successful')
							if len(history)>0:
								self.sendResponse('history', history)
						else:
							self.sendResponse('error', 'username taken')
							self.clientname=''
					else:
						self.clientname=''
						self.sendResponse('error', 'username contains illegal characters, only a-z A-Z and 0-9 allowed')
				else:
					self.sendResponse('error', 'Already logged in, logout to login with another name')
			# ------------------------ Help handle ------------------------
			elif request == 'help':
				self.sendResponse('info', '\n\n-----HELP TEXT-----\nlogin <username> - Login to chat server\nlogout - Logout of chat server\nmsg <message> - Send message\nnames - List over users in chat\nhelp - View help text\n')
			# ------------------------ Names handle ------------------------
			elif self.clientname == '':
				self.sendResponse('error', 'not logged in')
			elif request == 'names':
				clientusernamesAsString = '\t'.join(clientsUsernames)
				self.sendResponse('info',clientusernamesAsString)
			# ------------------------ Logout handle ------------------------
			elif request == 'logout':
				if self.clientname in clientsUsernames:
					clientsConnection.remove(self.connection)
					clientsUsernames.remove(self.clientname)
					self.sendResponse('info', 'you are now logged out')	
					#TODO Kill this clienthandler object?
					self.clientname = ''
				else:
					sendResponse('error', 'not logged inn')
			# ------------------------ Message handle ------------------------
			elif request =='message':
				sendtime = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
				json_message = json.dumps({
						'timestamp' : sendtime,
						'sender' : self.clientname,
						'response' : 'message',
						'content' : received_string['content']
						})
				for client in clientsConnection:
					client.send(json_message)
				history.append(json_message)
			else:
				pass
	if self.clientname != '':
		clientsUsernames.remove(self.clientname)

    def sendResponse(self, response, content):
    	json_response = json.dumps({
            		'timestamp': datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'),
            		'sender' : self.clientname,
            		'response' : response,
            		'content' : content
            		})
    	self.connection.sendall(json_response)

    def isValidUserName(self, name):
		return namereg.match(name)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

server = None

def sighandle(signum,sigvar):
    server.shutdown()
    server.server_close()
    exit()

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    
    signal.signal(signal.SIGINT,sighandle)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
