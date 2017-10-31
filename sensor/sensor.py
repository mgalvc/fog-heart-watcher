import socket, json, random, time, sys, threading, random

host = "localhost"
cloud_port = 8000
udp_frog_port = 8002
name = sys.argv[1]
location = sys.argv[2]

# tcp connection to authentication on server

socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_cloud.connect((host, cloud_port))

auth_message = {
	"from": "sensor",
	"action": "auth",
	"payload": {
		"location": location,
		"name": name
	}
}	

socket_to_cloud.sendall(json.dumps(auth_message).encode())

response = json.loads(socket_to_cloud.recv(1024).decode())

socket_to_cloud.close()

my_id = response.get("payload").get("id")
closest_fog_node_address = response.get("payload").get("closest_fog_server")

print(closest_fog_node_address)

socket_to_fog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

heart_rate = random.randint(50, 120)
pressure = [random.randint(80, 200), random.randint(60, 90)]
movement = 0

def send_data():
	while True:
		data = {
			"from": "sensor",
			"action": "patient_data",
			"payload": {
				"id": my_id,
				"heart_rate": heart_rate,
				"pressure": pressure,
				"movement": False if movement == 0 else True
			}
		}

		socket_to_fog.sendto(json.dumps(data).encode(), (closest_fog_node_address[0], udp_frog_port))

		time.sleep(5)

t = threading.Thread(target=send_data)
t.start()

while True:
	heart_rate, pressure[0], pressure[1], movement = [int(value) for value in input().split()]


