import socketserver, atexit, sys, socket
from connection_handler import ConnectionHandler

# your IP address in the first argument
host = sys.argv[1]
port = 8000

@atexit.register
def close_socket():
	""" shutdown function to close the sockets """
	print("closing server socket...")
	server.server_close()

# multithreaded server class to work with TCP connections
class Server(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

# ConnectionHandler handles incoming connections
server = Server((host, port), ConnectionHandler)
print("waiting connection on {}".format(server.server_address))

# start server 
server.serve_forever()