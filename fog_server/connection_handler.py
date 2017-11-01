import socketserver, json, threading, socket, time

# structure to store patients in risk
patients_in_risk = []

# please define the IP address of the cloud on this variable below
cloud = "localhost"
cloud_port = 8000

#structure to map the doctor and its patient
doctors = []

def send_risk_to_cloud():
	""" function to send patients in risk to the cloud"""

	while True:
		# first check if there is any patient in risk
		if len(patients_in_risk) > 0:
			# connect through TCP to cloud
			socket_to_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_to_cloud.connect((cloud, cloud_port))

			message = {
				"from": "fog_server",
				"action": "risk_patients",
				"payload": patients_in_risk
			}

			# send data to cloud
			socket_to_cloud.sendall(json.dumps(message).encode())
			socket_to_cloud.close()

			# once the data was sent, it can clean the structure
			del patients_in_risk[:]
		
		# wait for 5 seconds until send data again
		time.sleep(5)

# start thread to send data to cloud in parallel with server
t = threading.Thread(target=send_risk_to_cloud)
t.start()

def patient_is_in_risk(data):
	""" function that checks if the patient is in risk """

	heart_rate = data.get("heart_rate")
	pressure = data.get("pressure")
	movement = data.get("movement")

	# this is the only case which the patient is OK
	if (heart_rate >= 60 and heart_rate <= 100) and (pressure[0] <= 120 and pressure[1] <= 80):
		return False

	return True

def send_to_doctors(data):
	""" function to send data to the doctor that is watching the given sensor """
	socket_to_doctor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	for doctor in doctors:
		if data.get("id") == doctor.get("monitoring"):
			print("will send it to doctor {}".format(doctor.get("address")))
			socket_to_doctor.sendto(json.dumps(data).encode(), doctor.get("address"))

# these classes below work just like the handler class on cloud_server/server.py
class TCPConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request.recv(1024).decode())
		
		if data.get("from") == "doctor":
			if data.get("action") == "connect":
				# doctor is telling that he wants to watch some patient

				wants_to_watch = data.get("payload").get("patient_id")

				# store the doctor in the structure
				doctors.append({
					"address": (self.client_address[0], 8003),
					"monitoring": wants_to_watch
				})

				# tell doctor that the request has been received
				response = {
					"from": "fog_server",
					"status": 3
				}

				self.request.send(json.dumps(response).encode())


class UDPConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request[0].decode())

		print(data)

		# process data coming from sensor
		if data.get("from") == "sensor":
			if data.get("action") == "patient_data":
				in_risk = patient_is_in_risk(data.get("payload"))

				# check if patient is in risk and isn't already in the structure
				if in_risk and data.get("payload").get("id") not in patients_in_risk:
					# insert ID of the patient in risk into the structure
					data.get("payload").update({"in_risk": in_risk})
					patients_in_risk.append(data.get("payload").get("id"))

				# send this data to the doctors that want to watch this sensor
				send_to_doctors(data.get("payload"))