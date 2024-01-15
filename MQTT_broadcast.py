# python 3.10
# MQTT 转发小车实时位置 方向盘信息
import math
import random
import threading
import time

import numpy as np
import pymongo
import requests
from paho.mqtt import client as mqtt_client
from router.mqtt_receive import mqtt_rec, get_rec_data, human_thread_lock

# MQTT
# broker = '192.168.0.0'
broker = '8.137.120.144'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'mqtt_backend'
password = '**********'
send_time = 0
index = 0
rec_index = 0

# Mongo
Mongo_client = pymongo.MongoClient(host='127.0.0.1', port=27019)
mongo_db = Mongo_client.YOLO
start_time = 0
log_name = "log_name_ori"

human_static_time = 0
human_static_time_s = 0
human_pos = [0, 0]


def log_name_update():
    global log_name, start_time
    # slience_time = time.time() - start_time
    # beijing_time = time.localtime(time.mktime(time.gmtime()) + 8 * 3600)
    # beijing_str = time.strftime("%Y-%m-%d-%H-%M-%S", beijing_time)
    # if slience_time > 50:
    #     log_name = beijing_str
    #     with open("logs/Send%s.txt" % log_name, "a+") as f:
    #         f.write("'  picid  ', '  X  ', '  Y  ','  Index  ','  SendTime  '\n")


def monitor_collection(collection, MQTT_client, topic):
    '''
    监测数据库 向各个topic publish最新数据
    Parameters
    ----------
    collection: str mongoDB collection name
    MQTT_client: pymongo.MongoClient MQTT_client
    topic: str MQTT 主题
    '''
    global send_time, index, start_time, human_pos, human_static_time, human_static_time_s, human_thread_lock
    # Get the collection
    if topic == 'wifiheatmap':
        coll = Mongo_client['magic_wifi_box']['data']
        print('正在监测数据库表：', 'wifiheatmap')
        latest_doc = coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp = latest_doc['_id']
    else:
        coll = Mongo_client['YOLO'][collection]
        print('正在监测数据库表：', collection)
        latest_doc = coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp = latest_doc['_id']
    # Loop indefinitely
    while True:
        # 获取最新collection数据
        latest_doc = coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
        if latest_doc and latest_doc.get('_id') != last_timestamp:
            # log_name_update()
            last_timestamp = latest_doc['_id']
            # 删去_id
            latest_doc.pop('_id')
            # 获取最新collection数据
            # "Location"：小车实时坐标
            if (topic == "Location"):
                list_temp = []
                # data_temp = {'picid': latest_doc['picid'], 'x': latest_doc['x'], 'y': latest_doc['y']}
                data_temp = {'picid': latest_doc['picid'], 'x': latest_doc['x'], 'y': latest_doc['y']}

                '''
                
                
                
                '''
                list_temp.append(data_temp)
                msg = str({"data": list_temp})

            elif (topic == 'wifiheatmap'):
                list_temp = []
                data_temp = {'x': latest_doc['local_info']['x'], 'y': latest_doc['local_info']['y'],
                             'rssi': latest_doc['radiotap']['dbm_antsignal']}
                list_temp.append(data_temp)
                msg = str({"data": list_temp})
            elif (topic == "kalman"):
                list_temp = []
                latest_doc_location = Mongo_client['YOLO']['RealTimeLocation'].find_one(
                    sort=[('$natural', pymongo.DESCENDING)])
                latest_doc['kalman_parameters']['receive_location'] = [latest_doc_location['x'],
                                                                       latest_doc_location['y']]
                print('latest_doc', latest_doc['kalman_parameters']['receive_location'])
                list_temp.append(latest_doc)
                msg = str({"data": list_temp})

            # 'vehicle_data': 其余车辆 "Manual_mode" 方向盘模式
            elif (topic == 'vehicle_data' or topic == "Manual_mode"):
                list_temp = []
                list_temp.append(latest_doc)
                msg = str({"data": list_temp})
            # 路径规划
            elif (topic == 'rt_road_plan'):
                list_temp = []
                list_temp = latest_doc['data']
                print('list_temp', list_temp)
                # list_temp.append(latest_doc)
                msg = str({"data": list_temp})
            # 人体识别
            elif (topic == 'Route_mode'):
                latest_mec_location = Mongo_client['YOLO']['RealTimeLocation'].find_one(
                    sort=[('$natural', pymongo.DESCENDING)])
                d_mec_human = math.sqrt((latest_doc['x'] - latest_mec_location['x']) ** 2 + (
                        latest_doc['y'] - latest_mec_location['y']) ** 2)

                d = math.sqrt((latest_doc['x'] - human_pos[0]) ** 2 + (latest_doc['y'] - human_pos[1]) ** 2)

                if (d > 10):
                    human_static_time = 0
                    human_static_time_s = time.time()
                    print('human_static_time', round(human_static_time, 1), 'distance', round(d, 1),
                          human_thread_lock.locked())
                else:
                    human_static_time = time.time() - human_static_time_s
                    print('human_static_time', human_static_time, 'distance', d, human_thread_lock.locked())

                if (human_static_time >= 3):
                    if (d_mec_human < 10):
                        continue
                    list_temp = []
                    lf_coll = Mongo_client['YOLO']['left_hand']
                    latest_lefthand_doc = lf_coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
                    data_temp = {'id': 0, 'x': latest_lefthand_doc['x'], 'y': latest_lefthand_doc['y']}
                    list_temp.append(data_temp)
                    msg = str({"data": list_temp})
                    human_pos = [latest_doc['x'], latest_doc['y']]
                else:
                    human_pos = [latest_doc['x'], latest_doc['y']]
                    continue

            elif (topic == 'mouse_position'):
                list_temp = []
                data_temp = {'x': latest_doc['x'], 'y': latest_doc['y'], 'z': latest_doc['z']}
                list_temp.append(data_temp)
                msg = str({"data": list_temp})

            # pubilsh
            if topic != "Route_mode":
                result = MQTT_client.publish(topic, msg, qos=0)
                status = result[0]
                if status == 0:
                    send_time = int(round(time.time() * 1000))
                    # print(f"成功发布消息:{msg}给主题:{topic}\n")
                else:
                    print(f"Failed to send message to topic {topic}")
            else:
                if not human_thread_lock.locked() and human_static_time >= 3:
                    human_thread_lock.acquire()
                    result = MQTT_client.publish(topic, msg, qos=0)
                    status = result[0]
                    if status == 0:
                        # print(f"成功发布消息:{msg}给主题:{topic}\n")
                        send_time = int(round(time.time() * 1000))
                    else:
                        print(f"Failed to send message to topic {topic}\n")
    time.sleep(1)


class RoboticArm():
    def __init__(self):
        self.frame_idx = 0
        self.static_time = 5
        self.static_time_end = time.time()
        self.mouth_static_end = [120, 148, 100]
        self.mecanum = []
        self.mouth = [120, 148, 100]
        self.theta = 0
        # 车嘴距离
        self.distance = np.inf
        # 小车执行完路径 ：1
        self.flag = 1
        self.config = {
            'mouth-mecanum-distance-threshold': 50,
            'static_time-threshold': 3
        }
        self.RoArmUrl = "http://192.168.0.117"
        self.firstflag = 1
        self.armflag = 1

    def static_time_update(self, latest_doc):
        '''
        更新人脸静止时间
        :param latest_doc:
        :return:
        '''
        v = np.array([latest_doc['x'] - self.mouth_static_end[0], latest_doc['y'] - self.mouth_static_end[1]])
        d = np.linalg.norm(v)
        print('mouth d is {}\n'.format(d))
        if (d > 10):
            # 人脸移动
            self.static_time = 0
            self.static_time_end = time.time()
            self.mouth_static_end = self.mouth
            print('mouth is moving which re-distance is {}\n'.format(d))
        else:
            self.static_time = time.time() - self.static_time_end
            print('mouth static time is {} which re-distance is {}\n'.format(self.static_time, d))

    def distance_update(self):
        '''
        更新人车距离
        :param
        :return
        '''
        v = np.array([self.mecanum[0] - self.mouth[0], self.mecanum[1] - self.mouth[1], 80 - self.mouth[2]])
        self.distance = np.linalg.norm(v)
        print('mec-mouth-distance is {}\n'.format(self.distance))

    def Roboticarm_control(self):
        '''
        机械臂控制
        :return:
        '''
        print('-----正在运行机械臂控制-----')
        coll_mou = Mongo_client['YOLO']['mouse_position']
        latest_doc_mou = coll_mou.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp_mou = latest_doc_mou['_id']

        coll_mec = Mongo_client['YOLO']['RealTimeLocation']
        latest_doc_mec = coll_mec.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp_mec = latest_doc_mec['_id']

        coll_theta = Mongo_client['YOLO']['Raspberry_Kalman']
        latest_doc_theta = coll_theta.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp_theta = latest_doc_theta['_id']

        coll_flag = Mongo_client['YOLO']['stop_flag']
        latest_doc_flag = coll_flag.find_one(sort=[('$natural', pymongo.DESCENDING)])
        last_timestamp_flag = latest_doc_flag['_id']
        # Loop indefinitely
        while True:
            # get theta
            latest_doc = coll_theta.find_one(sort=[('$natural', pymongo.DESCENDING)])
            if latest_doc and latest_doc.get('_id') != last_timestamp_theta:
                # log_name_update()
                last_timestamp_theta = latest_doc['_id']
                # 删去_id
                latest_doc.pop('_id')
                self.theta = latest_doc["kalman_parameters"]['really_angle']

            # get mouth location
            latest_doc = coll_mou.find_one(sort=[('$natural', pymongo.DESCENDING)])
            if latest_doc and latest_doc.get('_id') != last_timestamp_mou:
                # log_name_update()
                last_timestamp_mou = latest_doc['_id']
                # 删去_id
                latest_doc.pop('_id')
                '''
                    {'picid': 0, 'inserttime': 'Wed Mar 27 13:24:10 2024', 'x': 39.2, 'y': 21.0, 'z': 4.0,'euler_angle': [-14, 47, 21]}
                '''

                # self.mouth = [latest_doc['x'] , latest_doc['y'] , latest_doc['z']]
                # try:
                #     self.static_time_update(latest_doc)
                # except:
                #     self.mouth_static_end = self.mouth
                #     print('frist frame RoboticArm initiation\n')
                print('mouth location is {}\n'.format(self.mouth))

            # get mec location
            latest_doc = coll_mec.find_one(sort=[('$natural', pymongo.DESCENDING)])
            if latest_doc and latest_doc.get('_id') != last_timestamp_mec:
                # log_name_update()
                last_timestamp_mec = latest_doc['_id']
                # 删去_id
                latest_doc.pop('_id')
                self.mecanum = [latest_doc['x'], latest_doc['y']]
                try:
                    self.distance_update()
                except:
                    print('distance update error , self.mecanum is {}\n'.format(self.mecanum))
                '''
                    {'data': [{'picid': 98, 'x': 28.0, 'y': 58.3}]}
                '''
            # 人脸静止3s

            if self.static_time > self.config['static_time-threshold']:
                if self.distance > self.config['mouth-mecanum-distance-threshold']:
                    # print(self.flag , self.mecanum)
                    if self.flag and self.mecanum:
                        self.publish_road_pt()
                        self.flag = 0
                        self.firstflag = 0
                        self.armflag = 1
                        # flag update
                else:
                    # 小车停下 机械臂不在运动
                    if self.flag and self.armflag:
                        x = self.mouth[0] - self.mecanum[0]
                        y = self.mouth[1] - self.mecanum[1]
                        z = float(self.mouth[2] - 80)
                        self.RoArm_move()
                        time.sleep(2)
                        self.RoArm_init()
                        self.flag = 0
                        self.firstflag = 0
                        self.armflag = 0
                    else:
                        if not self.flag:
                            print('无法进行机械臂控制-小车正在移动\n')
                        if not self.armflag:
                            print('无法进行机械臂控制-机械臂正在移动\n')

            if not self.firstflag:
                latest_doc = coll_flag.find_one(sort=[('$natural', pymongo.DESCENDING)])
                if latest_doc and latest_doc.get('_id') != last_timestamp_flag:
                    print('-----update self.flag-----')
                    last_timestamp_flag = latest_doc['_id']
                    self.flag = 1
                else:
                    self.flag = 0

    def publish_road_pt(self):
        topic = 'Route_mode'

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
        print('-----self.mecanum-----', self.mecanum)
        # list_temp.append({'id': 0, 'x': self.mecanum[0], 'y': self.mecanum[1]})
        list_temp.append({'id': 1, 'x': self.mouth[0], 'y': self.mouth[1] - 20})
        # print(list_temp)
        msg = str({"data": list_temp})

        MQTT_client = connect_MQTT()
        result = MQTT_client.publish(topic, msg)

        status = result[0]
        if status == 0:
            print(self.flag)
            print(f"机械臂控制-小车运动路径点发送成功:{msg}")
        else:
            print(f"机械臂控制-控制mecanum运动消息发送失败")

    def RoArm_request(self, data: str):
        # 小车命令发送函数，每次开机后url会变，当天一般是同一个url
        url = self.RoArmUrl + "/js?json=" + data
        try:
            res = requests.get(url, timeout=10)
            print(res.text)
            # print(f"机械臂控制消息:{data} 返回值为{res.text}\n")
        except requests.exceptions.ConnectionError:
            print("机械臂连接错误\n")
        except requests.exceptions.Timeout:
            print("机械臂连接超时\n")
        except:
            print("机械臂链接关闭\n")

    def RoArm_move(self):
        # coordinate 是嘴部和小车的相对x,y,z坐标单位是厘米，这里z轴坐标应为嘴部坐标减去80cm,sita是小车角度计读数，以x轴方向sita=0
        # 控制机械臂到达指定位置
        """
        try:
            while True:
                command = input("input your json cmd: ")
                url = "http://" + ip+ "/js?json=" + command
                response = requests.get(url)
                content = response.text
                print(content)
        except KeyboardInterrupt:
            pass"""
        x = self.mouth[0] - self.mecanum[0]
        y = self.mouth[1] - self.mecanum[1]
        z = float(self.mouth[2] - 80)
        angle = math.radians(self.theta)
        if (x * x + y * y + z * z) < 2500:
            new_x = 10 * (x * math.cos(angle) + y * math.sin(angle))
            new_y = 10 * (y * math.cos(angle) - x * math.sin(angle))
            new_z = 10 * z
            move_order = {"T": 104, "x": round(new_x, 2), "y": round(new_y, 2), "z": round(new_z, 2), "t": 3.14,
                          "spd": 0.25}
            print(str(move_order))
            self.RoArm_request(str(move_order))
        else:
            return 0

    def RoArm_init(self):
        # 控制机器臂归位
        self.RoArm_request(data='{"T":104,"x":130,"y":0,"z":70,"t":3.14,"spd":0.25}')


def connect_MQTT():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("成功连接 MQTT Broker!\n")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def mqtt_run():
    Roboticarm = RoboticArm()
    MQTT_client = connect_MQTT()
    MQTT_client.loop_start()

    # # 方向盘数据
    # receive_thread = threading.Thread(target=mqtt_rec ,args = (broker,"Steering"))
    # receive_thread.start()
    # print('订阅主题：',"Steering")

    # 树莓派上传Kalman PID参数 插入数据库表单：kalman_test
    receive_thread = threading.Thread(target=mqtt_rec, args=(broker, "Raspberry_Kalman"))
    receive_thread.start()
    print('订阅主题：', "Raspberry_Kalman")

    receive_thread = threading.Thread(target=mqtt_rec, args=(broker, "Route_done"))
    receive_thread.start()
    print('订阅主题：', "Route_done")

    receive_thread = threading.Thread(target=mqtt_rec, args=(broker, "human_prediction"))
    receive_thread.start()
    print('订阅主题：', "human_prediction")

    # 下发小车实时坐标
    rt_location_thread = threading.Thread(target=monitor_collection, args=("RealTimeLocation", MQTT_client, "Location"))
    rt_location_thread.start()

    # # 机械臂控制
    # rt_location_thread = threading.Thread(target=Roboticarm.Roboticarm_control)
    # rt_location_thread.start()
    '''
    # React2D develop mode test
    DM_React_thread = threading.Thread(target=monitor_collection, args=("Raspberry_Kalman", MQTT_client, "kalman"))
    DM_React_thread.start()
    DM_React_thread = threading.Thread(target=monitor_collection, args=("vehicle_data_test", MQTT_client, "vehicle_data"))
    DM_React_thread.start()
    DM_React_thread = threading.Thread(target=monitor_collection, args=("rt_road_plan_test", MQTT_client, "rt_road_plan"))
    DM_React_thread.start()
    DM_React_thread = threading.Thread(target=monitor_collection, args=("rt_location_test", MQTT_client, "rt_location"))
    DM_React_thread.start()
    '''

    ''' 
    # 人体跟踪
    DM_React_thread = threading.Thread(target=monitor_collection, args=("RTHumanLocation", MQTT_client, "Route_mode"))
    DM_React_thread.start()
    '''

    # 手动模式
    manual_mode_thread = threading.Thread(target=monitor_collection,
                                          args=("Manual_mode_input", MQTT_client, "Manual_mode"))
    manual_mode_thread.start()

    # Keep the main thread running
    while True:
        time.sleep(1)


if __name__ == '__main__':
    mqtt_run()