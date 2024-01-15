from bson import ObjectId
from fastapi import APIRouter,Response
from pydantic import BaseModel
import time
from mongodb_control.MongoDB_controller import DBManage
import types
import pymongo
import sys

client = pymongo.MongoClient(host='127.0.0.1', port=27019)
start_time = 0
end_time = 0
slience_time = time.time()
log_name = "log_name_ori"

def log_name_update(slience_time):
    global log_name
    beijing_time = time.localtime(time.mktime(time.gmtime()) + 8 * 3600)
    beijing_str = time.strftime("%Y-%m-%d-%H-%M-%S", beijing_time)
    if slience_time > 50:
        log_name = beijing_str
        # with open("logs/test%s.txt" % log_name, "a+") as f:
        #     f.write("'  id  ', '  X  ', '  Y  ','  Index  ', '  SendTime  ','  ReceiveTime  '\n")


def monitor_collection(collection):
    # Get the collection
    coll = client['DevelopMode_React'][collection]
    latest_doc = coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
    latest_doc.pop('_id')
    return latest_doc
    #time.sleep(1)


class InfoList(BaseModel):
    data: list
    '''
    {
        "data": 
        [
            {
                "id": 1,
                "Name": "mecanum",
                "Ymin": 111.0,
                "Xmin": 398.0,
                "Ymax": 229.0,
                "Xmax": 513.0
            },
            {
                "id": 1,
                "Name": "mecanum",
                "Ymin": 111.0,
                "Xmin": 398.0,
                "Ymax": 229.0,
                "Xmax": 513.0
            }
        ]
    }
    '''


router = APIRouter()


@router.get("/api/position-get")
async def list_students():
    mongo_db = client.YOLO
    mongo_collection = mongo_db.CJY
    data = list(mongo_collection.find())  # 所有数据
    for i in range(len(data)):
        data[i]['_id'] = data[i]['_id'].__str__()
    print("前端可视化数据")
    for i in range(len(data)):
        print(data[i])
    return data


'''
@router.get("/api/road-get")  ##kong 路径坐标
async def list_road():
    mongo_db = client.YOLO
    mongo_collection = mongo_db.Kong
    data = list(mongo_collection.find())  # 所有数据
    for i in range(len(data)):
        data[i]['_id'] = data[i]['_id'].__str__()
    print("路径规划数据")
    for i in range(len(data)):
        print("照片编号：", data[i]["picid"], "路径点编号：", data[i]["Point"], "归一化X坐标为：", data[i]["x"],
              "归一化Y坐标为：", data[i]["y"], "像素X坐标范围(cm)为：", round((data[i]["x"] * 10 - 5) / 3), "-",
              round((data[i]["x"] * 10 + 4) / 3), "实际Y坐标范围(cm)为：", round((data[i]["y"] * 10 - 5) / 3), "-",
              round((data[i]["y"] * 10 + 4) / 3))
    return data


@router.get("/api/Realtime-location-get")  ##kong 实时位置和角度
async def list_road():
    mongo_db = client.AutoV
    mongo_collection = mongo_db.MecanumLocation
    data = list(mongo_collection.find())  # 所有数据
    for i in range(len(data)):
        data[i]['_id'] = data[i]['_id'].__str__()
    print("小车实时位置和角度数据")
    for i in range(len(data)):
        print("照片编号：", data[i]["picid"], "归一化X坐标为：", data[i]["x"], "归一化Y坐标为：", data[i]["y"],  "像素X坐标范围(cm)为：", round((data[i]["x"] * 10 - 5) / 3), "-",
              round((data[i]["x"] * 10 + 4) / 3), "实际Y坐标范围(cm)为：", round((data[i]["y"] * 10 - 5) / 3), "-",
              round((data[i]["y"] * 10 + 4) / 3))
    return data

'''

@router.get("/api/react/test1.2")  ##前端可视化
async def list_get():
    colle='test2'
    data = monitor_collection(colle)
    msg = {'data': [data]}
    print("前端可视化数据",'collection:',colle)
    return msg

@router.get("/api/react/test1.3")
async def list_get():
    colle='test-dyna'
    data = monitor_collection(colle)
    msg = {'data': [data]}
    print("前端可视化数据",'collection:',colle)
    return msg

@router.get("/api/react/test2.1")
async def list_get():
    colle='rt_location_test'
    data = monitor_collection(colle)
    msg = {'data':[data]}
    print("前端可视化数据",'collection:',colle)
    return msg

@router.get("/api/react/test2.2")
async def list_get():
    colle='rt_road_plan_test'
    data = monitor_collection(colle)
    print("前端可视化数据",'collection:',colle)
    return data

@router.get("/api/react/test2.3")
async def list_get():
    coll = client['DevelopMode_React']['rt_location_test']
    latest_docs = coll.find().sort([('$natural', pymongo.DESCENDING)]).limit(5)
    latest_docs_msg=[]
    num_doc = 1
    for doc in latest_docs:
        msg_node = {
            'point':num_doc,
            'x':doc['x'],
            'y':doc['y']
        }
        latest_docs_msg.append(msg_node)
        num_doc += 1
    msg = {'data':latest_docs_msg}
    return msg


@router.post("/api/position-post", tags=["info"])
async def insertInfo(info: InfoList,response: Response):
    global slience_time,start_time
    slience_time = time.time() - start_time
    print("slience_time",slience_time)
    log_name_update(slience_time)
    mongo_db = client.YOLO
    mongo_collection = mongo_db.YOLOpost

    if len(info.data) != -1:
        print("post数据")
        for datanum in range(len(info.data)):
            print(info.data[datanum])
    mongo_collection.insert_many(list(info.data))
    res_data = []
    mongo_collection = mongo_db.RealTimeLocation
    for postnum in range(len(info.data)):
        info.data[postnum]['index'] += 1
        res_data.append(info.data[postnum])
        if (info.data[postnum]['name'] == 'mecanum'):
            mongo_collection = mongo_db.RealTimeLocation
            mydict = {
                "picid": info.data[postnum]['id'],
                "index": info.data[postnum]['index'],
                "x": float(round(info.data[postnum]['x'],1 )),
                "y": float(round(info.data[postnum]['y'],1 )),
                # "Angle": angle1c
            }
            mongo_collection.insert_one(mydict)
            print('insert id:', info.data[postnum]['id'])
        elif (info.data[postnum]['name'] == 'human'):
            mongo_collection = mongo_db.RTHumanLocation
            mydict = {
                "picid": info.data[postnum]['id'],
                "index": info.data[postnum]['index'],
                "x": float(round(info.data[postnum]['x'], 1)),
                "y": float(round(info.data[postnum]['y'], 1)),
                # "Angle": angle1c
            }
            mongo_collection.insert_one(mydict)
            print('insert id:', info.data[postnum]['id'])

        elif (info.data[postnum]['name'] == 'left_hand'):
            mongo_collection = mongo_db.left_hand
            mydict = {
                "picid": info.data[postnum]['id'],
                "index": info.data[postnum]['index'],
                "x": float(round(info.data[postnum]['x'], 1)),
                "y": float(round(info.data[postnum]['y'], 1)),
                # "Angle": angle1c
            }
            mongo_collection.insert_one(mydict)
            print('insert id:', info.data[postnum]['id'])

        elif (info.data[postnum]['name'] == 'left_hand'):
            mongo_collection = mongo_db.Lefthand_location
            mydict = {
                "picid": info.data[postnum]['id'],
                "index": info.data[postnum]['index'],
                "x": float(round(info.data[postnum]['x'], 1)),
                "y": float(round(info.data[postnum]['y'], 1)),
                # "Angle": angle1c
            }
            mongo_collection.insert_one(mydict)
            print('insert id:', info.data[postnum]['id'])

    response.content = {"data": res_data}
    response.status_code = 200
    # start_time = time.time()
    return response

@router.post("/api/mouthposition-post", tags=["info"])
async def insertInfo(info: InfoList):
    mongo_db = client.YOLO
    mongo_collection = mongo_db.mouse_position
    if len(info.data) != -1:
        print("post数据",info.data)
        t=time.asctime()
        # for datanum in range(len(info.data)):
        #     print(info.data[datanum])\

    for postnum in range(len(info.data)):
            mydict = {
                "picid": info.data[postnum]['id'],
                "inserttime":t,
                "x": float(round(info.data[postnum]['x'],1)),
                "y": float(round(info.data[postnum]['y'],1)),
                "z": float(round(info.data[postnum]['z'],1)),
                "euler_angle": info.data[postnum]['euler_angle'],
            }
            mongo_collection.insert_one(mydict)
            print('insert mongo collection:', mongo_collection,'message:',mydict)
    return "mouse"

@router.post("/api/mouse_road", tags=["info"])
async def insertInfo(info: InfoList):
    mongo_db = client.YOLO
    mongo_collection = mongo_db.road_mouse
    if len(info.data) != -1:
        print("post数据",info.data)
        t=time.asctime()
        # for datanum in range(len(info.data)):
        #     print(info.data[datanum])\

    for postnum in range(len(info.data)):
            mydict = {
                "picid": info.data[postnum]['id'],
                "inserttime":t,
                "x": float(round(((info.data[postnum]['x']-314) / 19.721),1)),
                "y": float(round(((info.data[postnum]['y']-291) / 13.235),1)),
            }
            mongo_collection.insert_one(mydict)
            print('insert mongo:', mydict)

    return "mouse"

