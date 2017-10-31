import socketserver, threading, atexit, socket, json, sys
from connection_handler import TCPConnectionHandler, UDPConnectionHandler

host = "localhost"
cloud_server_port = 8000
tcp_port = 8001
udp_port = 8002
location = sys.argv[1]

# connection with cloud server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, cloud_server_port))

auth_message = {
	"from": "fog_server",
	"action": "auth",
	"payload": {
		"location": location
	}
}

sock.sendall(json.dumps(auth_message).encode())

response_message = json.loads(sock.recv(1024).decode())

my_id = response_message.get("payload").get("id")

sock.close()

@atexit.register
def close_socket():
	""" shutdown method to close the sockets """
	print("closing server socket...")
	tcp_server.server_close()
	udp_server.server_close()

#server to connect with doctor and patient

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass
class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer): pass

tcp_server = TCPServer((host, tcp_port), TCPConnectionHandler)
udp_server = UDPServer((host, udp_port), UDPConnectionHandler)

tcp_thread = threading.Thread(target=tcp_server.serve_forever)
tcp_thread.start()

print("runnin tcp")

udp_thread = threading.Thread(target=udp_server.serve_forever)
udp_thread.start()

print("runnin udp")
