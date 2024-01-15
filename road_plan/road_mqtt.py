import random
import threading
import time
import math
from paho.mqtt import client as mqtt_client

## mqtt set
# broker = '121.43.37.161'
broker = '192.168.11.87'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'Python_mqtt_Send_realtime'
password = '**********'
topic = 'Route_mode'


def azimuthangle(x1, y1, x2, y2):
    """ 已知两点坐标计算角度 -
    :param x1: 原点横坐标值
    :param y1: 原点纵坐标值
    :param x2: 目标点横坐标值
    :param y2: 目标纵坐标值
    """
    angle = 0.0
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1:
            angle = 0.0
        elif y2 < y1:
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif x2 > x1 and y2 < y1:
        angle = math.pi / 2 + math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1:
        angle = math.pi + math.atan(dx / dy)
    elif x2 < x1 and y2 > y1:
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
    return angle * 180 / math.pi


def connect_MQTT():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("成功连接 MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


list_temp = []

location0 = {'id': 0, 'x': 60, 'y': 90}
# location1 = {'id': 1, 'x': 50, 'y': 200}
# location2 = {'id': 2, 'x': 200, 'y': 200}
# location3 = {'id': 3, 'x': 200, 'y': 50}
# location4 = {'id': 4, 'x': 50, 'y': 50}

# angle = azimuthangle(location0['x'],location0['y'],location1['x'],location1['y'])
# locationend = {'id': location1['id'],'x':  location1['x'], 'y': location1['y'],'angle':angle}
# print(angle)
list_temp.append(location0)
# list_temp.append(location1)
# list_temp.append(location2)
# list_temp.append(location3)
# list_temp.append(location4)

msg = str({"data": list_temp})

MQTT_client = connect_MQTT()
result = MQTT_client.publish(topic, msg)

status = result[0]
if status == 0:
    print(f"成功发布消息:{msg}给主题:{topic}")
else:
    print(f"Failed to send message to topic {topic}")

# location = { 'picid': 0, 'x': 100, 'y': 100}
# list_temp=[]
# list_temp.append(location)
# msg = str({"data": list_temp})
# MQTT_client = connect_MQTT()
# result = MQTT_client.publish('Location', msg)
# status = result[0]
# if status == 0:
#   print(f"成功发布消息:{msg}给主题:{'Location'}")
# else:
#   print(f"Failed to send message to topic {'Location'}")
