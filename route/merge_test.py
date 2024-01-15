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


if __name__ == '__main__':
    # 测试
    points = [(85, 147), (86, 146), (87, 145), (88, 144), (89, 143), (90, 142), (91, 141), (92, 140), (93, 139)]
    result = merge_points(points)
    print(result)
