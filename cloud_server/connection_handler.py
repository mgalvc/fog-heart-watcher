import json, socketserver, time, socket, logging
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from datetime import datetime

# structure to map all devices connected to this server and to the fog servers
mapping = {
	"fog_nodes": [],
	"sensors": [],
	"doctors": []
}

# log to server monitoring
logging.basicConfig(filename='server.log', level=logging.INFO)

def find_closest_fog_server(location):
	""" this function finds the closest fog node to the given location """
	
	fog_nodes = mapping.get("fog_nodes")

	closest = None
	
	geolocator = Nominatim()

	for fog_node in fog_nodes:
		# get coordinates for the given location and for the current fog node location
		origin_geocode = geolocator.geocode(location)
		origin = (origin_geocode.latitude, origin_geocode.longitude)
		destination_geocode = geolocator.geocode(fog_node.get("location"))
		destination = (destination_geocode.latitude, destination_geocode.longitude)
		
		# calculate the distance in miles between the two points
		distance = vincenty(origin, destination).miles

		if closest == None:
			closest = [fog_node.get("address"), distance]
		elif closest[1] > distance:
			closest = [fog_node.get("address"), distance]

	# return list containing the closest frog node address and its distance to the sensor
	return closest

def look_for_patient_id(patient_id):
	""" auxiliar function that searches a sensor given its ID
	and returns the fog node which it's connected to """

	sensors = mapping.get("sensors")

	for sensor in sensors:
		if sensor.get("id") == patient_id:
			return sensor.get("connected_to")

	return None


class ConnectionHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		""" overriden function that handles new connections """

		while True:
			# wait for some message
			data = json.loads(self.request.recv(1024).decode())

			# process the received message (who sent and what want to do)
			if data.get("from") == "fog_server":
				if data.get("action") == "auth":
					location = data.get("payload").get("location")
					
					# give and ID to the new node
					new_id = len(mapping.get("fog_nodes"))

					# store device address to further comunications
					new_node = {
						"id": new_id,
						"address": self.client_address[0],
						"location": location
					}

					# store it in the mapping structure
					mapping.get("fog_nodes").append(new_node)
					
					response = {
						"from": "cloud_server",
						"status": 1,
						"payload": {
							"id": new_id
						}
					}

					logging.info("{}: fog node {} is connected".format(datetime.now(), self.client_address[0]))

					# send response back to the client
					self.request.send(json.dumps(response).encode())
				
				elif data.get("action") == "risk_patients":
					# here I should have stored the data permanently
					logging.info("{}: got {} in risk".format(datetime.now(), data.get("payload")))

			elif data.get("from") == "sensor":
				if data.get("action") == "auth":
					location = data.get("payload").get("location")
					name = data.get("payload").get("name")

					# find the closest fog node
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

					# response containing the closest fog node
					response = {
						"from": "cloud_server",
						"status": 1,
						"payload": {
							"closest_fog_server": closest_fog_server,
							"id": new_id
						}
					}

					logging.info("{}: sensor {} is connected".format(datetime.now(), self.client_address[0]))

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

					logging.info("{}: doctor {} is connected".format(datetime.now(), self.client_address[0]))

					self.request.send(json.dumps(response).encode())

				elif data.get("action") == "specific_patient":
					patient_id = data.get("payload").get("id")

					# look for the fog node connected to the specified sensor
					fog_address = look_for_patient_id(patient_id)

					response = None

					if fog_address == None:
						# response telling that the sensor hasn't been found
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