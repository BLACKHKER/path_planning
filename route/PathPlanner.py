import time

from astar import AStar
import sys
import math

from route.convertimage import create_grids
from route.utils import parse_xml_file


class PathPlanner(AStar):
    """sample use of the astar algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, maze):
        self.lines = maze
        self.width = len(self.lines[0])
        self.height = len(self.lines)

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        (x1, y1) = n1
        (x2, y2) = n2
        self.lines[y1][x1] = 2
        self.lines[y2][x2] = 2
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        # (x1, y1) = n1
        # (x2, y2) = n2
        # return math.hypot(x2 - x1, y2 - y1)
        return 1

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        x, y = node
        return [(nx, ny) for nx, ny in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y),
                                        (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)] if
                0 <= nx < self.width and 0 <= ny < self.height and self.lines[ny][nx] != 1]


def find_path(m, start, goal):
    if m[goal[1]][goal[0]] == 1:
        return None, m

    t1 = time.time()

    PP = PathPlanner(m)

    # let's solve it
    foundPath = PP.astar(start, goal)

    search_map = PP.lines

    if foundPath is None:
        return None, search_map

    t2 = time.time()
    print('find path:{}s'.format(t2 - t1))

    return list(foundPath), search_map


if __name__ == '__main__':
    xml_file_path = "map.xml"
    xml_dict = parse_xml_file(xml_file_path)
    grid_size = int(xml_dict['map_info']['grid_size'])
    map = create_grids(image_path='map.png', grid_size=grid_size)
    start = (85, 147)
    goal = (89, 126)
    print(find_path(map, start, goal))
