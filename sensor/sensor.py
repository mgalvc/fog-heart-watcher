import socket, json, random, time, sys, threading, random, atexit

# your IP address in the first argument
host = sys.argv[1]
# IP address of cloud server in the second argument
cloud = sys.argv[2]

cloud_port = 8000
udp_frog_port = 8002

# name of the patient in the third argument
name = sys.argv[3]
#location of the patient in the fourth argument
location = sys.argv[4]

@atexit.register
def close_socket():
	""" shutdown function to close the sockets """
	print("closing server socket...")
	socket_to_fog.close()

# tcp connection to authenticate sensor on cloud server
socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_cloud.connect((cloud, cloud_port))

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

# get the address of the closest fog node
closest_fog_node_address = response.get("payload").get("closest_fog_server")

print("this sensor will connect to {}".format(closest_fog_node_address))

# create an UDP socket to talk with fog node
socket_to_fog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# generate first random data
heart_rate = random.randint(50, 120)
pressure = [random.randint(80, 200), random.randint(60, 90)]
movement = 0

def send_data():
	""" function to send patient's data to fog node periodically """

	while True:
		data = {
			"from": "sensor",
			"action": "patient_data",
			"payload": {
				"id": my_id,
				"name": name,
				"heart_rate": heart_rate,
				"pressure": pressure,
				"movement": False if movement == 0 else True
			}
		}

		socket_to_fog.sendto(json.dumps(data).encode(), (closest_fog_node_address[0], udp_frog_port))

		time.sleep(5)

# start thread to run function in parallel with user input in the loop below
t = threading.Thread(target=send_data)
t.start()

# this loop allow you to change the patient's data
while True:
	heart_rate, pressure[0], pressure[1], movement = [int(value) for value in input().split()]


