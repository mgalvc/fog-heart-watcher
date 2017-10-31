import socket, json, random, time, sys, threading, random

host = "localhost"
cloud_port = 8000
tcp_frog_port = 8001
udp_frog_port = 8002

# tcp connection to authentication on server

socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_cloud.connect((host, cloud_port))

auth_message = {
	"from": "doctor",
	"action": "auth"
}	

socket_to_cloud.sendall(json.dumps(auth_message).encode())

response = json.loads(socket_to_cloud.recv(1024).decode())

my_id = response.get("payload").get("id")

patient_id = int(input())

request_specific_patient = {
	"from": "doctor",
	"action": "specific_patient",
	"payload": {
		"id": patient_id
	}
}

socket_to_cloud.sendall(json.dumps(request_specific_patient).encode())

response_specific_client = json.loads(socket_to_cloud.recv(1024).decode())

fog_node_address = response_specific_client.get("payload").get("fog_node_address")[0]

print("patient {} is connected to fog node {}".format(patient_id, fog_node_address))

socket_to_fog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_fog.connect((host, tcp_frog_port))

request_fog_connection = {
	"from": "doctor",
	"action": "connect",
	"payload": {
		"patient_id": patient_id,
		"id": my_id
	}
}

socket_to_fog.sendall(json.dumps(request_fog_connection).encode())

socket_to_udp_fog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_to_udp_fog.bind(("localhost", 8003))

while True:
	data = json.loads(socket_to_udp_fog.recv(1024).decode())
	print(data)

socket_to_cloud.close()