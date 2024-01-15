import threading
import time
import paho.mqtt.client as mqtt
import pymongo

Mongo_client = pymongo.MongoClient(host='127.0.0.1', port=27019)
data_insert = 0
data_rec = 0
receive_time = 0
start_time = 0
log_name = 0
human_thread_lock = threading.Lock()


def log_name_update():
    global log_name, start_time
    slience_time = time.time() - start_time
    beijing_time = time.localtime(time.mktime(time.gmtime()) + 8 * 3600)
    beijing_str = time.strftime("%Y-%m-%d-%H-%M-%S", beijing_time)
    if slience_time > 50:
        log_name = beijing_str
        # with open("logs/Rec%s.txt" % log_name, "a+") as f:
        #     f.write("'  picid  ', '  X  ', '  Y  ','  Index  ','  receive_time  '\n")


def ping_rec_process(data):
    global data_rec, receive_time
    if (type(data_rec) == dict):
        data_rec = data['Index']
        print('——Ping Test——：收到回传信息：', data_rec)
        receive_time = int(round(time.time() * 1000))


def get_rec_data():
    return data_rec, receive_time


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
        print("Connected with result code " + str(rc))


def on_message_ping(client, userdata, msg):
    global data_rec, log_name, start_time
    print('receive', msg.payload)
    # log_name_update()
    mqttdata = eval(str(msg.payload, encoding="utf-8"))
    location = mqttdata['data']
    # data_input = eval(location)
    data_input = location
    data_insert = data_input[0]
    ping_rec_process(data_insert)
    # with open("logs/Rec%s.txt" % log_name, "a+") as f:
    #     f.write("{:0>5.0f} {:0>7.2f} {:0>7.2f} {:0>5.0f} \n".format(
    #                                                                       data_insert['x'],
    #                                                                       data_insert['y'],
    #                                                                       data_insert['index'],
    #                                                                       int(round(time.time() * 1000))
    #                                                                       )
    #     )
    # start_time = time.time()


def on_message_steering(client, userdata, msg):
    global data_rec
    mqttdata = eval(str(msg.payload, encoding="utf-8"))
    location = mqttdata['data']
    data_input = eval(location)
    data_insert = data_input[0]
    print('——手动模式——：收到方向盘信息：', data_insert)
    Mongo_client['YOLO']['Manual_mode_input'].insert_one(data_insert)


def on_message_kalman(client, userdata, msg):
    global data_rec

    mqttdata = eval(str(msg.payload, encoding="utf-8"))

    location = mqttdata['data']
    # print(location[0])
    kalman_mongo = {
        "kalman_parameters": {
            "Q": location[0]['Q'],
            "R": location[0]['R'],
            "camera_angle": 45,
            "really_angle": location[0]['really_angle'],
            "receive_location": [0, 0],
            "Kalman_location": [location[0]['Kalman_location_x'], location[0]['Kalman_location_y']]
        },
        "PID": {
            "P": location[0]['P'],
            "I": location[0]['I'],
            "D": location[0]['D']
        }
    }
    # print('——树莓派消息——：收到Kalman信息：', kalman_mongo)
    Mongo_client['YOLO']['Raspberry_Kalman'].insert_one(kalman_mongo)
    # data_input = eval(location)
    # data_insert = data_input[0]
    # print('——树莓派消息——：收到Kalman信息：', data_insert)
    # Mongo_client['YOLO']['Kalman_test'].insert_one(data_insert)


def on_message_route_done(client, userdata, msg):
    '''
    修改为插入数据到mongoDB
    :param client:
    :param userdata:
    :param msg:
    :return:
    '''
    stop_flag = {
        "flag": 1
    }
    Mongo_client['YOLO']['stop_flag'].insert_one(stop_flag)
    # mqttdata = eval(str(msg.payload, encoding="utf-8"))
    # print('——树莓派消息——：收到路径执行完毕信息：', mqttdata)
    human_flag_update()


def human_flag_update():
    print('——树莓派消息——：收到路径执行完毕信息')
    global human_thread_lock
    if human_thread_lock.locked():
        human_thread_lock.release()


def on_message_Pedestrian(client, userdata, msg):
    global data_rec
    mqttdata = eval(str(msg.payload, encoding="utf-8"))
    data_list = mqttdata['data']
    # data_input = eval(data_list)
    # data_insert = data_input[0]
    if data_list:
        insert_data = {}
        print('——手动模式——：收到行人信息：', data_list)
        for i, Pedestrian in enumerate(data_list):
            insert_data['Pred%s' % (i)] = Pedestrian
            print(insert_data)
        Mongo_client['YOLO']['human_prediction'].insert_one(insert_data)


def mqtt_rec(broker, topic):
    client = mqtt.Client(protocol=3)
    client.username_pw_set("BackEndReceive_%s" % topic, "password")
    client.on_connect = on_connect
    if topic == 'Ping':
        client.on_message = on_message_ping
    elif topic == 'Steering':
        client.on_message = on_message_steering
    elif topic == 'Raspberry_Kalman':
        client.on_message = on_message_kalman
    elif topic == 'Route_done':
        client.on_message = on_message_route_done
    elif topic == 'human_prediction':
        client.on_message = on_message_Pedestrian
    client.connect(host=broker, port=1883, keepalive=60)  # 订阅频道
    time.sleep(1)
    client.subscribe([(topic, 0)])
    client.loop_forever()
