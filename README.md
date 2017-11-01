# Heart Watcher

## Setting up the environment

- Before cloning this repository, please make sure that you have python3 and its pip version installed.
- Clone the project, get into its root folder and run ` pip3 install -r requirements.txt`. This command will install the GeoPy library.

## Tutorial 

- First, you must run the cloud server that requires an IP Address as an argument, according to this example: 
`python3 cloud_server/server.py 127.0.0.1`. Just change "127.0.0.1" to your IP Address.
- Please open the server.log file in order to watch what is going to happen on the cloud server. You can do this running `tail -f server.log`.
- Before the next steps, please open the file `fog_server/connection_handler.py` and change the variable `cloud`, right in line 7, putting there the IP Address where you intend to run the fog server.
- Then, run the fog server passing three more arguments just like the following: 
`python3 fog_server/server.py [your_ip_address] [ip_address_of_cloud_server] [location_of_this_node]`. In that third argument you can just pass an address, in order to simulate the location of the fog node. That's why you need the GeoPy library installed.
- Now, let's start a sensor. Just run `python3 sensor/sensor.py [your_ip_address] [ip_address_of_cloud_server] [patient_name] [patient_location]`. Once the sensor is running, you can change the data of this patient, typing numbers according to this model: `[heart_rate] [systolic_pressure] [diastolic_pressure] [movement]`, where movement 0 means resting and 1 means moving.
- In order to start a doctor, you need to run `python3 doctor/doctor.py [your_ip_address] [ip_address_of_cloud_server]`. Then you can type a patient's ID and you will start watching its data. You can choose the patient according to the log file or tracking the outputs of the fog server (though it's quite more challenging).
- To close any of the servers, you can press `Ctrl+C`. Just remember that it will break the entire application.
