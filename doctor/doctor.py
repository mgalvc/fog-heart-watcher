import socket, json, random, time, sys, threading, random, datetime, atexit

# your IP address in the first argument
host = sys.argv[1]
# IP address of cloud server in the second argument
cloud = sys.argv[2]

cloud_port = 8000
tcp_frog_port = 8001
udp_frog_port = 8002

@atexit.register
def close_socket():
	""" shutdown function to close the sockets """
	print("closing server socket...")
	socket_to_cloud.close()
	socket_to_fog.close()
	socket_to_udp_fog.close()

# tcp connection to authenticate doctor on server
socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_cloud.connect((cloud, cloud_port))

auth_message = {
	"from": "doctor",
	"action": "auth"
}	

# send auth_message to cloud
socket_to_cloud.sendall(json.dumps(auth_message).encode())

# get the response
response = json.loads(socket_to_cloud.recv(1024).decode())

my_id = response.get("payload").get("id")

# wait a input with the ID of the patient that this doctor will watch
patient_id = int(input())

# ask the server about the location of the patient
request_specific_patient = {
	"from": "doctor",
	"action": "specific_patient",
	"payload": {
		"id": patient_id
	}
}

socket_to_cloud.sendall(json.dumps(request_specific_patient).encode())

response_specific_client = json.loads(socket_to_cloud.recv(1024).decode())

# the address of the fog node where the specified patient is connected to
fog_node_address = response_specific_client.get("payload").get("fog_node_address")[0]

print("patient {} is connected to fog node {}".format(patient_id, fog_node_address))

# connect to the fog node through TCP and ask for the patient's data
socket_to_fog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_fog.connect((fog_node_address, tcp_frog_port))

request_fog_connection = {
	"from": "doctor",
	"action": "connect",
	"payload": {
		"patient_id": patient_id,
		"id": my_id
	}
}

socket_to_fog.sendall(json.dumps(request_fog_connection).encode())

# create udp socket to listen the fog node
socket_to_udp_fog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_to_udp_fog.bind((host, 8003))

while True:
	# wait patient's data coming from the fog node
	data = json.loads(socket_to_udp_fog.recv(1024).decode())
	
	print("\n--- {} ---".format(datetime.datetime.now()))
	
	print("Name:		{}".format(data.get("name")))
	print("Heart rate:	{}".format(data.get("heart_rate")))
	print("Pressure:	{}/{}".format(data.get("pressure")[0], data.get("pressure")[1]))
	print("Movement:	{}".format("Resting" if data.get("movement") == 0 else "Moving"))
	print("State:		{}".format("In risk" if data.get("in_risk") else "Healthy"))

socket_to_cloud.close()