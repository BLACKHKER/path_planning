import heapq

import numpy as np
from matplotlib import pyplot as plt


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def astar_search(map, start, end):
    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])

    open_list = []
    closed_list = []

    heapq.heappush(open_list, start_node)

    while len(open_list) > 0:
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        if current_node.x == end_node.x and current_node.y == end_node.y:
            path = []
            current = current_node
            while current is not None:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        neighbors = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.x + new_position[0], current_node.y + new_position[1])

            if node_position[0] > (len(map) - 1) or node_position[0] < 0 or node_position[1] > (len(map[0]) - 1) or node_position[1] < 0:
                continue

            if map[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(node_position[0], node_position[1])
            new_node.g = current_node.g + 1
            new_node.h = ((new_node.x - end_node.x) ** 2) + ((new_node.y - end_node.y) ** 2)
            new_node.f = new_node.g + new_node.h
            new_node.parent = current_node
            neighbors.append(new_node)

        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            if neighbor not in open_list:
                heapq.heappush(open_list, neighbor)
            else:
                if neighbor.g > current_node.g + 1:
                    neighbor.g = current_node.g + 1
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current_node

def ResultPlt(start,end,map,path):
    fig,ax = plt.subplots(figsize=(20, 20))
    ax.imshow(map, cmap=plt.cm.binary)
    # ax.imshow(S,cmap=plt.cm.summer)#色彩风格
    # 获取到当前坐标轴信息
    ax = plt.gca()
    path_y = [path_node[0] for path_node in path]
    path_x = [path_node[1] for path_node in path]
    plt.plot(path_x, path_y, 'r-', linewidth=3)
    # 画出起点位置 blue 画出终点位置 red
    plt.scatter(start[1], start[0], s=200, c='b', marker='o')
    plt.scatter(end[1], end[0], s=200, c='r', marker='o')
    # plt.grid()# 开启栅格
    # plt.grid(color='k', linestyle='-', linewidth=0.1)
    plt.show()

def main():
    map = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    start = (0, 0)
    end = (4, 4)

    path = astar_search(map, start, end)
    print(path)
    ResultPlt(start,end,map,path)
if __name__ == '__main__':
    main()
