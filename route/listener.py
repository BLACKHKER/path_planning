# python 3.6
import json
import random

from paho.mqtt import client as mqtt_client

from route.convertimage import create_grids
from route.getpath import find_path
from route.utils import parse_xml_file

broker = '8.137.120.144'
port = 1883

topic = "Location"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

xml_dict = parse_xml_file('map.xml')
grid_size = int(xml_dict['map_info']['grid_size'])
grids_map = create_grids('map.png', grid_size, xml_dict)


def on_connect(client, userdata, flags, rc):
    print("Connected MQTT, result code " + str(rc))
    client.subscribe("Route_set")


def on_message(client, userdata, msg):
    print("=" * 30 + "new msg" + "=" * 30)
    print("get message from topic", msg.topic)
    print("this message payload: " + str(msg.payload))
    path = []
    data = json.loads(str(msg.payload)[2:-1].replace("'", "\""))['data']
    for i in range(len(data) - 1):
        start_point = (int(data[i]['x']), int(data[i]['y']))
        end_point = (int(data[i + 1]['x']), int(data[i + 1]['y']))
        path_dict = find_path(grids_map, start_point, end_point, save=True)
        print("start point: ", start_point, "end point:", end_point, path_dict)
        if path_dict is None:
            path = None
            break
        path.extend(path_dict)
    if path is not None:
        publish_data(client, path)


def publish_data(client, data):
    msg = json.dumps({'data': data})
    result = client.publish("Route_mode", msg)
    status = result[0]
    if status == 0:
        print('publish to topic Route_mode' + msg)
    else:
        print(f"Failed to send message to topic Location")


# Create an MQTT client instance
client = mqtt_client.Client()

# Assign callbacks to client
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)

# Start the loop to process incoming messages
client.loop_forever()
