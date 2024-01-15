# python 3.10
import random
import time

import pymongo
import numpy as np
from matplotlib import pyplot as plt
from pymongo import MongoClient
from Astar import astar_search, ResultPlt

# MongoDB数据库配置
client = pymongo.MongoClient(host='127.0.0.1', port=27019)
mongo_db = client.DevelopMode_React
YOLO_collection = mongo_db.obstacles_test

# 栅格地图配置
grid_width = 116  # 网格宽度
grid_height = 54  # 网格高度
map_width = 1160  # 地图宽度
map_height = 540  # 地图高度

# 其他设置
obstacle_label=['trash', 'projector', 'cup'] # 障碍物label
robot_radius = 2  # 避障半径

# 读取YOLO检测结果
detections = YOLO_collection.find()
obstacle_coords = []
for detection in detections:
    if detection['id'] == 5:
        if detection['Name'] in obstacle_label:
            print(detection)
             # 解析YOLO检测结果
            [xmin,ymin,xmax,ymax] = [detection['Xmin'],detection['Ymin'],detection['Xmax'],detection['Ymax']]
        # 将检测结果映射到栅格地图上
            x1 = int(xmin * grid_width / map_width)
            y1 = int(ymin * grid_height / map_height)
            x2 = int(xmax * grid_width / map_width)
            y2 = int(ymax * grid_height / map_height)
            obstacle_coords.append((x1, y1, x2, y2))
        # 自动模式起点
        if detection['Name'] == 'mecanum':
            start = (int((detection['Ymin'] + detection['Ymax']) / 2 * grid_width / map_width),
                     int((detection['Xmin'] + detection['Xmax']) / 2 * grid_height / map_height))
# 生成栅格地图
print(obstacle_coords)
grid_map = np.zeros((grid_height,grid_width))
for coords in obstacle_coords:
    x1, y1, x2, y2 = coords
    grid_map[y1:y2,x1:x2] = 1

# 碰撞保护功能
obstacle_map = np.zeros_like(grid_map)
for y in range(grid_height):
    for x in range(grid_width):
        if grid_map[y, x] == 1:
            for i in range(-robot_radius, robot_radius+1):
                for j in range(-robot_radius, robot_radius+1):
                    if 0 <= x+i < grid_width and 0 <= y+j < grid_height:
                        obstacle_map[y+j, x+i] = -1
grid_map[obstacle_map == -1] = 0.2
# 障碍物本身和碰撞保护范围作出区分
for coords in obstacle_coords:
    x1, y1, x2, y2 = coords
    grid_map[y1:y2,x1:x2] = 1

# 桌子外围设为障碍物吗，防止掉落
grid_map[0,0:116] = 1
grid_map[53,0:116] = 1
grid_map[0:53,0] = 1
grid_map[0:53,115] = 1


if __name__ == '__main__':

    # 起点终点设置
    start = (20,10)
    end = (28, 60)

    path = astar_search(grid_map, start, end)
    for path_node in path:
        grid_map[path_node[0],path_node[1]] = 0.1
    # 可视化栅格地图
    ResultPlt(start,end,grid_map,path)


    ############### React可视化测试2.2数据 ################

    db = client['YOLO']
    collection = db['rt_location_test']
    collection_path = db['rt_road_plan_test']
    for node in path:
        print(node)
        rt_location = {
            "id": 1,
            "x": node[0],
            "y": node[1],
            "objID": 1,
            "x_obj": end[0],
            "y_obj": end[1],
            "Integral_Angle": 90.0,
        }
        collection.insert_one(rt_location)

        path_mongo=[]
        for path_node in path:
            grid_map[path_node[0], path_node[1]] = 0
        path_temp = astar_search(grid_map, node, end)
        for path_node in path_temp:
            grid_map[path_node[0], path_node[1]] = 0.1
        # 可视化栅格地图
        #ResultPlt(node, end, grid_map, path_temp)
        print('start', node, 'path_temp', path_temp)
        path_node_count = 0
        for path_node in path_temp:
            path_node_mongo = {
                "objID": 1,
                "point": path_node_count,
                "x": path_node[0],
                "y": path_node[1],
            }
            path_mongo.append(path_node_mongo)
            path_node_count += 1
            #print('path_node_mongo',path_node_mongo)

        print('path_mongo',path_mongo)
        path_mongo_insert = {'data':path_mongo}
        collection_path.insert_one(path_mongo_insert)
        time.sleep(random.uniform(1,5))



    #print(path[1])

