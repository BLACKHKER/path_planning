import time

import cv2

from route import PathPlanner
from route.convertimage import create_grids, array_to_image
from route.utils import parse_xml_file, save_figure

# xml_file_path = "D:/PycharmWorkspace/my_backend_s/route/map.xml"
xml_file_path = "/root/web/my_backend_s/route/map.xml"
xml_dict = parse_xml_file(xml_file_path)

grid_size = int(xml_dict['map_info']['grid_size'])


def real2pixel(real_pos):
    """
    :param real_pos:世界实际坐标，单位cm
    :return:
    """
    ratio = float(xml_dict['map_info']['ratio'])
    origin_x = int(xml_dict['map_info']['origin']['x'])
    origin_y = int(xml_dict['map_info']['origin']['y'])
    x_v = int(xml_dict['map_info']['origin']['x_v'])
    y_v = int(xml_dict['map_info']['origin']['y_v'])
    pixel_x = int(origin_x + real_pos[0] * x_v / 100 * ratio)
    pixel_y = int(origin_y + real_pos[1] * y_v / 100 * ratio)
    return pixel_x, pixel_y


def pixel2grid(pixel_pos):
    grid_x = pixel_pos[0] // grid_size
    grid_y = pixel_pos[1] // grid_size
    return grid_x, grid_y


def grid2pixel(grid_pos):
    pixel_x = (grid_pos[0] + 0.5) * grid_size
    pixel_y = (grid_pos[1] + 0.5) * grid_size
    return int(pixel_x), int(pixel_y)


def pixel2real(pixel_pos):
    ratio = float(xml_dict['map_info']['ratio'])
    origin_x = int(xml_dict['map_info']['origin']['x'])
    origin_y = int(xml_dict['map_info']['origin']['y'])
    x_v = int(xml_dict['map_info']['origin']['x_v'])
    y_v = int(xml_dict['map_info']['origin']['y_v'])
    real_x = int((pixel_pos[0] - origin_x) * x_v * 100 / ratio)
    real_y = int((pixel_pos[1] - origin_y) * y_v * 100 / ratio)
    return real_x, real_y


def merge_points(points):
    merged_points = [points[0]]  # 初始化合并后的点列表并添加第一个点
    prev_slope = None  # 初始化前一个斜率
    for i in range(1, len(points) - 1):  # 修改遍历范围以排除最后一个点
        x1, y1 = points[i - 1]  # 获取前一个点的坐标
        x2, y2 = points[i]  # 获取当前点的坐标
        x3, y3 = points[i + 1]  # 获取下一个点的坐标
        slope1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')  # 计算当前点与前一个点之间的斜率
        slope2 = (y3 - y2) / (x3 - x2) if x3 - x2 != 0 else float('inf')  # 计算当前点与下一个点之间的斜率
        if slope1 != slope2:  # 如果两个斜率不相同
            merged_points.append(points[i])  # 将当前点添加到合并后的点列表中
    merged_points.append(points[-1])  # 添加最后一个点
    return merged_points


def find_path(grids_map, start_real, end_real, save=False):
    start_px = real2pixel(start_real)
    end_px = real2pixel(end_real)

    start_grid = pixel2grid(start_px)
    end_grid = pixel2grid(end_px)

    print(start_grid, end_grid)
    # grids_map = create_grids('map.png', grid_size)
    # print(grids_map)

    grids_img = array_to_image(grids_map)

    grid_path, search_map = PathPlanner.find_path(grids_map, start_grid, end_grid)

    print('grid_path', grid_path)

    if grid_path is None:
        cv2.circle(grids_img, start_grid, 2, (0, 255, 0), -1)
        cv2.circle(grids_img, end_grid, 2, (0, 0, 255), -1)
        cv2.imwrite("/root/web/my_backend_s/route/" + 'grids.png', grids_img)
        real_path = [start_real, end_real]
        if save:
            save_figure(grids_map, real_path)
        return None

    for point in grid_path:
        cv2.circle(grids_img, point, 1, (255, 0, 0), -1)

    cv2.circle(grids_img, start_grid, 2, (0, 255, 0), -1)
    cv2.circle(grids_img, end_grid, 2, (0, 0, 255), -1)
    # cv2.imshow('image', grids_img)
    # cv2.waitKey(0)
    cv2.imwrite("/root/web/my_backend_s/route/" + 'grids.png', grids_img)

    merge_dict = merge_points(grid_path)

    real_path = []
    for grid_point in merge_dict[1:-1]:
        pixel_pos = grid2pixel(grid_point)
        real_pos = pixel2real(pixel_pos)
        real_path.append(real_pos)
    real_path.append(end_real)

    path_dict = []
    for item in real_path:
        path_dict.append({'x': item[0], 'y': item[1]})
    if save:
        save_figure(search_map, real_path)

    return path_dict


if __name__ == '__main__':
    start_real = (0, 0)
    end_real = (200, 200)

    grids_map = create_grids("/root/web/my_backend_s/route/" + 'map.png', grid_size)

    path = find_path(grids_map, start_real, end_real, save=True)
    print(path)
