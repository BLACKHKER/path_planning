import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from numpy import shape

from route.utils import parse_xml_file


def is_obstacle(pixel):
    # 假设黑色为 (0, 0, 0)，白色为 (255, 255, 255)
    black_count = sum(1 for value in pixel if value < 200)
    white_count = sum(1 for value in pixel if value > 200)
    return black_count > 0


def create_grids(image_path, grid_size, xml_dict, protection_rad=5):
    image = Image.open(image_path).convert('RGB')
    ratio = float(xml_dict['map_info']['ratio'])
    origin_x = int(xml_dict['map_info']['origin']['x'])
    origin_y = int(xml_dict['map_info']['origin']['y'])
    x_v = int(xml_dict['map_info']['origin']['x_v'])
    y_v = int(xml_dict['map_info']['origin']['y_v'])

    img_array = np.array(image)

    for obj in xml_dict['static_objects']['object']:
        x1 = int(obj['top_left']['x'])
        y1 = int(obj['top_left']['y'])
        x2 = int(obj['bottom_right']['x'])
        y2 = int(obj['bottom_right']['y'])
        x1_px = int(origin_x + x1 * x_v / 100 * ratio)
        y1_px = int(origin_y + y1 * y_v / 100 * ratio)
        x2_px = int(origin_x + x2 * x_v / 100 * ratio)
        y2_px = int(origin_y + y2 * y_v / 100 * ratio)
        cv2.rectangle(img_array, (x1_px - protection_rad, y1_px - protection_rad), (x2_px + protection_rad, y2_px + protection_rad), (0, 0, 0), -1)

    image = Image.fromarray(img_array)

    width, height = image.size
    grid_width = width // grid_size
    grid_height = height // grid_size
    grids = []
    grids_img = np.zeros([grid_height, grid_width], dtype=np.uint8)
    grids_map = [[0] * grid_width for _ in range(grid_height)]
    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            box = (max(0, x - grid_size), max(0, y - grid_size), x + grid_size, y + grid_size)
            region = image.crop(box)
            pixels = list(region.getdata())
            is_obs = is_obstacle([sum(p) / 3 for p in pixels])  # 计算每个网格的颜色并判断是否为障碍物
            grids.append({'position': (x, y), 'is_obstacle': is_obs})
            if is_obs:
                grids_img[y // grid_size, x // grid_size] = 255
                grids_map[y // grid_size][x // grid_size] = 1  # True表示障碍物，False表示空地

    # cv2.imshow('grids_map', cv2.resize(grids_img, [grids_img.shape[1], grids_img.shape[0]]))
    # cv2.waitKey(0)

    return grids_map


def array_to_image(array):
    # 将True转换为255（白色），将False转换为0（黑色）
    image_data = [[[255, 255, 255] if element else [0, 0, 0] for element in row] for row in array]
    return np.array(image_data, dtype=np.uint8)


if __name__ == '__main__':
    # 使用示例
    image_path = "map.png"  # 你需要替换为你的图片路径
    xml_file_path = "map.xml"
    xml_dict = parse_xml_file(xml_file_path)
    grid_size = int(xml_dict['map_info']['grid_size'])
    grids = create_grids(image_path, grid_size, xml_dict)

    for grid in grids:
        print(grid)
