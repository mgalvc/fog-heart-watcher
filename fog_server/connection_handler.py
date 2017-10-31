import socketserver, json, threading, socket, time

patients_in_risk = []

cloud = "172.16.103.110"
cloud_port = 8000

doctors = []

def send_risk_to_cloud():
	while True:
		if len(patients_in_risk) > 0:
			socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_to_cloud.connect((cloud, cloud_port))

			message = {
				"from": "fog_server",
				"action": "risk_patients",
				"payload": patients_in_risk
			}

			socket_to_cloud.sendall(json.dumps(message).encode())
			socket_to_cloud.close()

			del patients_in_risk[:]
		
		time.sleep(5)

t = threading.Thread(target=send_risk_to_cloud)
t.start()

def patient_is_in_risk(data):
	heart_rate = data.get("heart_rate")
	pressure = data.get("pressure")
	movement = data.get("movement")

	if (heart_rate >= 60 and heart_rate <= 100) and (pressure[0] <= 120 and pressure[1] <= 80):
		return False

	return True

def send_to_doctors(data):
	socket_to_doctor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	for doctor in doctors:
		if data.get("id") == doctor.get("monitoring"):
			print("will send it to doctor {}".format(doctor.get("address")))
			socket_to_doctor.sendto(json.dumps(data).encode(), doctor.get("address"))


class TCPConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request.recv(1024).decode())
		if data.get("from") == "doctor":
			if data.get("action") == "connect":
				wants_to_watch = data.get("payload").get("patient_id")

				doctors.append({
					"address": (self.client_address[0], 8003),
					"monitoring": wants_to_watch
				})

				response = {
					"from": "fog_server",
					"status": 3
				}

				self.request.send(json.dumps(response).encode())


class UDPConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request[0].decode())

		print(data)

		if data.get("from") == "sensor":
			if data.get("action") == "patient_data":
				in_risk = patient_is_in_risk(data.get("payload"))

				if in_risk and data.get("payload").get("id") not in patients_in_risk:
					patients_in_risk.append(data.get("payload").get("id"))

				send_to_doctors(data.get("payload"))