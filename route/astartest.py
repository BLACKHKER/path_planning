import heapq
import math
import time


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


def heuristic(a, b):
    return math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y))


def astar_search(map, start, end):
    open_set = []
    closed_set = set()
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # 初始化起始节点和目标节点
    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])

    # 将起始节点加入到open集合中
    heapq.heappush(open_set, start_node)

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.x == end_node.x and current_node.y == end_node.y:
            path = []
            while current_node.parent:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]

        closed_set.add((current_node.x, current_node.y))

        for direction in directions:
            x = current_node.x + direction[0]
            y = current_node.y + direction[1]

            if x < 0 or x >= len(map) or y < 0 or y >= len(map[0]) or map[x][y] == 1 or (x, y) in closed_set:
                continue

            neighbor = Node(x, y)
            neighbor.g = current_node.g + 1
            neighbor.h = heuristic(neighbor, end_node)
            neighbor.f = neighbor.g + neighbor.h
            neighbor.parent = current_node

            if any(node for node in open_set if node.x == neighbor.x and node.y == neighbor.y and node.f < neighbor.f):
                continue

            heapq.heappush(open_set, neighbor)

    return None


if __name__ == '__main__':
    # 测试数据
    grid_map = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    start_point = (0, 0)
    end_point = (9, 0)

    t0 = time.time()
    path = astar_search(grid_map, start_point, end_point)
    print(path)
    t1 = time.time()
    print(t1 - t0)
