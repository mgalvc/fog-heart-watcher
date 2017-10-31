import json, socketserver, time
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
from datetime import datetime
import config

mapping = {
	"fog_nodes": [],
	"sensors": [],
	"doctors": []
}

def find_closest_fog_server(location):
	fog_nodes = mapping.get("fog_nodes")

	closest = None
	
	geolocator = Nominatim()

	for fog_node in fog_nodes:
		origin_geocode = geolocator.geocode(location)
		origin = (origin_geocode.latitude, origin_geocode.longitude)

		destination_geocode = geolocator.geocode(fog_node.get("location"))
		destination = (destination_geocode.latitude, destination_geocode.longitude)
		
		distance = vincenty(origin, destination).miles

		if closest == None:
			closest = [fog_node.get("address"), distance]
		elif closest[1] > distance:
			closest = [fog_node.get("address"), distance]

	return closest

def look_for_patient_id(patient_id):
	sensors = mapping.get("sensors")

	for sensor in sensors:
		if sensor.get("id") == patient_id:
			return sensor.get("connected_to")

	return None


class ConnectionHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		while True:
			data = json.loads(self.request.recv(1024).decode())

			if data.get("from") == "fog_server":
				if data.get("action") == "auth":
					location = data.get("payload").get("location")
					
					new_id = len(mapping.get("fog_nodes"))

					new_node = {
						"id": new_id,
						"address": self.client_address[0],
						"location": location
					}

					mapping.get("fog_nodes").append(new_node)
					
					response = {
						"from": "cloud_server",
						"status": 1,
						"payload": {
							"id": new_id
						}
					}

					print("fog node {} is connected".format(self.client_address[0]))

					self.request.send(json.dumps(response).encode())
				elif data.get("action") == "risk_patients":
					print("got {} in risk".format(data.get("payload")))

			
			elif data.get("from") == "sensor":
				if data.get("action") == "auth":
					location = data.get("payload").get("location")
					name = data.get("payload").get("name")

					closest_fog_server = find_closest_fog_server(location)

					new_id = len(mapping.get("sensors"))

					new_sensor = {
						"id": new_id,
						"name": name,
						"address": self.client_address,
						"location": location,
						"connected_to": closest_fog_server
					}
					
					mapping.get("sensors").append(new_sensor)

					response = {
						"from": "cloud_server",
						"status": 1,
						"payload": {
							"closest_fog_server": closest_fog_server,
							"id": new_id
						}
					}

					print("sensor {} is connected".format(self.client_address[0]))

					self.request.send(json.dumps(response).encode())
			
			elif data.get("from") == "doctor":
				if data.get("action") == "auth":
					new_id = len(mapping.get("doctors"))

					new_doctor = {
						"id": new_id,
						"address": self.client_address,
					}

					mapping.get("doctors").append(new_doctor)

					response = {
						"from": "cloud_server",
						"status": 1,
						"payload": {
							"id": new_id
						}
					}

					print("doctor {} is connected".format(self.client_address[0]))

					self.request.send(json.dumps(response).encode())

				elif data.get("action") == "specific_patient":
					patient_id = data.get("payload").get("id")

					fog_address = look_for_patient_id(patient_id)

					print(fog_address)

					response = None

					if fog_address == None:
						response = {
							"from": "cloud_server",
							"status": 4
						}
					else:
						response = {
							"from": "cloud_server",
							"status": 3,
							"payload": {
								"fog_node_address": fog_address
							}
						}

					self.request.send(json.dumps(response).encode())