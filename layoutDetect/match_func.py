# -*- coding:utf-8_*-
'''
@version:
arthor:wyq
@time:2024/07/10
@file:match_func.py
@function:
@modify:
'''
import math


# 计算矩形框的坐标中心
def center_of_rectangle(target_xy):
    return (target_xy[0] + target_xy[2]) / 2, (target_xy[1] + target_xy[3]) / 2


# 计算两坐标的距离
def distance_between_points(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# 找到target在列表中最近的框
def nearest_rec_index(target_xy, rectangles):
    target_center = center_of_rectangle(target_xy)
    min_distance = float('inf')
    nearest_index = -1
    index = 0
    for rect in rectangles:
        rect_center = center_of_rectangle(rect)
        distance = distance_between_points(target_center, rect_center)
        if distance < min_distance:
            min_distance = distance
            nearest_index = index
        index += 1
    return nearest_index


# 找到最匹配的figure/box && caption。输入图表list和与之匹配的caption list
def match_ft_caption(ft_list, caption_list):
    ft_caption = {}  # {图片的坐标：解说的坐标}
    for caption in caption_list:
        index = nearest_rec_index(caption, ft_list)  # 最近的框号
        ft_xy_caption = ft_list.pop(index)  # 取出该框的四点坐标
        ft_caption[str(ft_xy_caption)] = caption
    return ft_caption, ft_list


# 把图片，table和它们的caption对应起来。
def ft_caption_read(dict_list, ft_list, caption_list):
    ft_caption, ft_list = match_ft_caption(ft_list, caption_list)
    for chunk in dict_list:
        if chunk['type'] == "figures" or chunk['type'] == "tables":
            if str(chunk['x_y']) in ft_caption.keys():
                caption_xy = ft_caption[str(chunk['x_y'])]
                for chunk_tmp in dict_list:
                    if chunk_tmp['x_y'] == caption_xy:
                        chunk["context"] = chunk_tmp["context"]
                        break
                    
    result_list = []
    for chunk in dict_list:
        if chunk['type'] == "figure_caption" or chunk['type'] == "table_caption":
            pass
        else:
            result_list.append(chunk)
    return result_list, ft_list


if __name__ == "__main__":
    result = [
        {
            "type": "title",
            "context": "标题的内容",
            "x_y": [1, 1, 2, 2],
            "path": "该切块的存放地址",
            "page": 1
        },
        {
            "type": "text",
            "context": "文本块的内容",
            "x_y": [22, 21, 52, 42],
            "path": "该切块的存放地址",
            "page": 1
        },
        {
            "type": "figure",
            "x_y": [23, 22, 35, 87],
            "path": "该图片的存放地址",
            "page": 1
        },
        {
            "type": "table",
            "x_y": [33, 51, 89, 76],
            "path": "该表格的存放地址",
            "page": 1
        },
        {
            "type": "table",
            "x_y": [133, 151, 189, 176],
            "path": "该表格的存放地址",
            "page": 1
        },
        {
            "type": "figure_caption",
            "context": "图解的内容",
            "x_y": [28, 22, 40, 87],
            "path": "该图片的存放地址",
            "page": 1
        },
        {
            "type": "table_caption",
            "context": "表格说明的内容",
            "x_y": [33, 60, 89, 99],
            "path": "该表格的存放地址",
            "page": 1
        }
    ]
    caption_list = [
        [28, 22, 40, 87],
        [33, 60, 89, 99]
    ]
    table_list = [[23, 22, 35, 87], [33, 51, 89, 76],[133, 151, 189, 176]]
    dict_list, ft_list = ft_caption_read(result, table_list, caption_list)
    print(dict_list)