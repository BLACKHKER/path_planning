import xml.etree.ElementTree as ET

import cv2


def xml_to_dict(element):
    result = {}
    for child in element:
        if child:
            child_dict = xml_to_dict(child)
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict
        else:
            result[child.tag] = child.text
    return result


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_dict(root)


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


def save_figure(grid_map, real_path, filename='result.png'):
    img = cv2.imread('/root/web/my_backend_s/route/map.png')
    for i in range(len(grid_map)):
        for j in range(len(grid_map[0])):
            y_start = i * grid_size
            x_start = j * grid_size
            if grid_map[i][j] == 0:
                color = (0, 255, 0)
            elif grid_map[i][j] == 1:
                color = (0, 0, 255)
            elif grid_map[i][j] == 2:
                color = (0, 255, 255)
            cv2.rectangle(img, (x_start, y_start), (x_start + grid_size, y_start + grid_size), color, -1)

    if real_path is not None:
        for item in real_path:
            cv2.circle(img, real2pixel(item), int(grid_size / 2), (255, 0, 0), -1)

    cv2.imwrite("/root/web/my_backend_s/route/" + filename, img)
    return img
