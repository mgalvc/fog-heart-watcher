import socketserver, atexit, sys
from connection_handler import ConnectionHandler

host = "localhost"
port = 8000

@atexit.register
def close_socket():
	""" shutdown method to close the sockets """
	print("closing server socket...")
	server.server_close()

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

server = Server((host, port), ConnectionHandler)
print("waiting connection...")
server.serve_forever()