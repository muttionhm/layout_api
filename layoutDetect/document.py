# -*- coding:utf-8_*-
"""
@version:
arthor:wyq
@time:2024/07/08
@file:document.py
@function:
@modify:
"""
import json
import uuid
import os
import requests
import cv2
import numpy as np
import torch
from PIL import Image
from Large_model.about_layout import LayoutOrcModel
from config import OUTPUT_PATH
from layoutDetect.match_func import *
from utilies.utilies import filename_fix
from LLM_api import chat,chat_image,chat_image_data
import re
import time,io
stop_words = ["<\|user\|>", "<\|endoftext\|>", "<\|observation\|>", "<user>"]
stop_re = re.compile("(" + "|".join(stop_words) + ")$")

print("(" + "|".join(stop_words) + ")$")
from ultralytics import YOLO
# from config import LAYOUT_MODEL_PATH
# from Large_model.vlm_api import VLM_api
from config import layout_model_path

# class LayoutOrcModel:
layout_model = YOLO(model=layout_model_path)


def padding(img):
    # 原始图像的尺寸
    original_width, original_height = img.size
    if original_width > 640 or original_height > 640:
        new_size = max(original_width, original_height)
        target_width, target_height = new_size, new_size
        pad_left = (target_width - original_width) // 2
        pad_top = (target_height - original_height) // 2
        padded_img = Image.new("RGB", (target_width, target_height), "white")
        padded_img.paste(img, (pad_left, pad_top))
    else:
        # 目标尺寸
        target_width, target_height = 640, 640
        # 计算填充量
        pad_left = (target_width - original_width) // 2
        pad_top = (target_height - original_height) // 2
        pad_right = target_width - original_width - pad_left
        pad_bottom = target_height - original_height - pad_top

        # 使用'constant'填充模式，填充颜色为白色（或者你选择的其他颜色）
        padded_img = Image.new("RGB", (target_width, target_height), "white")
        padded_img.paste(img, (pad_left, pad_top))

    return padded_img


class Document:
    def __init__(self, pdf_path):
        self.id = uuid.uuid4()
        self.name = filename_fix(pdf_path.split('/')[-1])
        self.pages_path = f"output/images/{self.name}"  # 存放保存页数的地址
        self.chunk_path = f"output/text/{self.name}"  # 存放text&title的地址
        self.caption_path = f"output/caption/{self.name}"  # 存放caption的地址
        self.figures_path = f"output/figures/{self.name}"  # 存放保存图的地址
        self.tables_path = f"output/tables/{self.name}"  # 存放保存表的地址
        self.model = LayoutOrcModel()

    # 保存各类块，chunk为该块的坐标
    def put_save_chunk(self, type, page_no, img_cv2, chunk):
        if type == 2:
            path = self.figures_path
        elif type == 4:
            path = self.tables_path
        elif type == 3 or type == 5:
            path = self.caption_path
        else:
            path = self.chunk_path
        if path:
            saveimage = img_cv2[chunk[1] : chunk[3], chunk[0] : chunk[2]]
            saveimage = Image.fromarray(cv2.cvtColor(saveimage, cv2.COLOR_BGR2RGB))
            chunk_name = (
                f"{self.name}_{page_no}_{chunk[0]}_{chunk[1]}_{chunk[2]}_{chunk[3]}"
            )
            if not os.path.exists(path):
                os.makedirs(path)
            saveimage.save(os.path.join(path, chunk_name + ".png"))
            path = os.path.join(path, chunk_name + ".png")
        return path

    # 对单个图表块进行描述
    def read_ft_chunk(self, ft_chunk, img_cv2):
        image = img_cv2[ft_chunk[1] : ft_chunk[3], ft_chunk[0] : ft_chunk[2]]
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # 必须把图像尺寸padding到正方形再ocr，细长条的框无法识别
        image = padding(image)
        img_byte_arr = io.BytesIO()
        # 将图像保存到BytesIO对象，而不是文件
        image.save(img_byte_arr, format='PNG')
        # 获取二进制图像数据
        buffer = img_byte_arr.getvalue()
        msgs = self.model.generate_prompts(ocr=True)
        response = chat_image_data(msgs,buffer)
        if response:
            return response
        else:
            return "清晰度过低，无法解析"

    # 对单个文字块进行识别
    def read_text_chunk(self, text_chunk, img_cv2):
        image = img_cv2[text_chunk[1] : text_chunk[3], text_chunk[0] : text_chunk[2]]
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # 必须把图像尺寸padding到正方形再ocr，细长条的框无法识别
        image = padding(image)
        img_byte_arr = io.BytesIO()
        # 将图像保存到BytesIO对象，而不是文件
        image.save(img_byte_arr, format='PNG')
        # 获取二进制图像数据
        buffer = img_byte_arr.getvalue()
        msgs = self.model.generate_prompts(ocr=True)
        result = chat_image_data(msgs,buffer)
        return result


    # 读每一页的块
    def page_chunk(self, img_cv2, page_no):
        img_cv2 = cv2.cvtColor(np.asarray(img_cv2), cv2.COLOR_RGB2BGR)
        # block_count = 0
        yolo_result = layout_model(img_cv2)[0]  # 切出的各类块
        res_boxes = yolo_result.boxes

        # figures = []
        # figure_captions = []
        # tables = []
        # table_captions = []

        # page_result_list = []

        # 区分切出的各类块，并保存
        for i_box in res_boxes:
            if 0 <= int(i_box.cls) <= 5:
                x1, y1, x2, y2 = map(int, i_box.xyxy[0])
                self.put_save_chunk(
                        int(i_box.cls), page_no, img_cv2, [x1, y1, x2, y2]
                    )
                # chunk_dict = {
                #     "center":[(x1+x2)/2, (y1+y2)/2],
                #     "x_y": [x1, y1, x2, y2],
                #     "path": self.put_save_chunk(
                #         int(i_box.cls), page_no, img_cv2, [x1, y1, x2, y2]
                #     ),
                #     "page": page_no,
                # }
        #         if int(i_box.cls) == 0:
        #             chunk_dict["type"] = "text"
        #             chunk_dict["context"] = self.read_text_chunk(
        #                 chunk_dict["x_y"], img_cv2
        #             )
        #         if int(i_box.cls) == 1:
        #             chunk_dict["type"] = "title"
        #             chunk_dict["context"] = self.read_text_chunk(
        #                 chunk_dict["x_y"], img_cv2
        #             )

        #         # 处理匹配问题
        #         if int(i_box.cls) == 2:
        #             chunk_dict["type"] = "figures"
        #             figures.append([x1, y1, x2, y2])
        #         if int(i_box.cls) == 3:
        #             chunk_dict["type"] = "figure_caption"
        #             figure_captions.append([x1, y1, x2, y2])
        #             chunk_dict["context"] = self.read_text_chunk(
        #                 chunk_dict["x_y"], img_cv2
        #             )
        #         if int(i_box.cls) == 4:
        #             chunk_dict["type"] = "tables"
        #             tables.append([x1, y1, x2, y2])
        #         if int(i_box.cls) == 5:
        #             chunk_dict["type"] = "table_caption"
        #             table_captions.append([x1, y1, x2, y2])
        #             chunk_dict["context"] = self.read_text_chunk(
        #                 chunk_dict["x_y"], img_cv2
        #             )
        #         page_result_list.append(chunk_dict)


        # # 对图片和图说的匹配与对应
        # if 1 <= len(figure_captions) <= len(figures):
        #     page_result_list, figures = ft_caption_read(
        #         page_result_list, figures, figure_captions
        #     )  # figures是为了维持pop后的一致性
            

        # # 如果图片还有没处理的,就识别图片的内容作为caption
        # if len(figures) >= 1:
        #     for figure in figures:
        #         for index in range(len(page_result_list)):
        #             if page_result_list[index]["x_y"] == figure:
        #                 page_result_list[index]["context"] = self.read_ft_chunk(
        #                     figure, img_cv2
        #                 )

        # # 对表格和表格说明的匹配与对应
        # if 1 <= len(table_captions) <= len(tables):
        #     page_result_list, tables = ft_caption_read(
        #         page_result_list, tables, table_captions
        #     )  # tables是为了维持pop后的一致性
        # # 如果表格还有没处理的
        # if len(tables) >= 1:
        #     for table in tables:
        #         for index in range(len(page_result_list)):
        #             if page_result_list[index]["x_y"] == table:
        #                 page_result_list[index]["context"] = self.read_ft_chunk(
        #                     table, img_cv2
        #                 )

        # return self.read_sort(page_result_list)

    # 处理单页内的切块和ocr
    def layout_ocr(self, img_cv2, page_no):
        self.page_chunk(img_cv2, page_no)
        torch.cuda.empty_cache()  # 释放内存
        return 

    # 处理单页内的阅读顺序问题(只设计了单栏）
    def read_sort(self, chunk_list):
        """
        read_list = [
            {
                "type": "title",
                "context": "标题的内容",
                "x_y": [x1, y1, x2, y2],
                "path": "该切块的存放地址",
                "page": 1
            },
            {
                "type": "title",
                "context": "标题的内容",
                "x_y": [x1, y1, x2, y2]
            },
            {
                "type": "title",
                "context": "标题的内容",
                "x_y": [x1, y1, x2, y2]
            },
            ...
        ]"""

        sorted_elements = sorted(
            chunk_list,
            key=lambda elem: (elem["center"][1]),
            reverse=False,
        )  # 升序处理，单栏考虑y就足够了
        return sorted_elements


    # 处理文件本身，返回带阅读顺序的部分,顺便返回第一页的文字内容用来做文本分类。
    def chunk_data(self):
        page_no = 0  # 页码
        # self.pages_path 是带有后缀名的
        image_list0 = os.listdir(self.pages_path)
        image_list = sorted(image_list0, key=lambda x: int(x.split('.')[0]))
        for index,image_name in enumerate(image_list):  # 逐页读取
            img_cv2 = cv2.imread(
                self.pages_path + "/" + image_name
            )  # 从路径读入PpmImageFile格式的图片数据
            self.layout_ocr(img_cv2, page_no)
            # page_box_list = self.layout_ocr(img_cv2, page_no)  # 从页内读数据 
            # cls_refo[self.name+'.pdf'][str(index)] = {}
            # cls_refo[self.name+'.pdf'][str(index)]['text'] = ''.join([i['context'] for i in page_box_list])
            # for chunk in page_box_list:
            #     chunk_id = str(self.id) + "_" + str(chunk_th)
            #     result[chunk_id] = chunk
            #     chunk_th += 1
            # page_no += 1

        """
            result = {
                docid_1: {
                    "type": "title",
                    "context": "标题的内容",
                    "x_y": [x1, y1, x2, y2],
                    "path": "该切块的存放地址",
                    "page": 1
                },
                docid_2: {
                    "type": "text",
                    "context": "文本块的内容",
                    "x_y": [x1, y1, x2, y2],
                    "path": "该切块的存放地址",
                    "page": 1
                },
                docid_3: {
                    "type": "figure",
                    "caption": "图解的内容",
                    "x_y": [x1, y1, x2, y2],
                    "path": "该图片的存放地址",
                    "page": 1
                },
                docid_4: {
                    "type": "table",
                    "caption": "表格说明的内容",
                    "x_y": [x1, y1, x2, y2],
                    "path": "该表格的存放地址",
                    "page": 1
                },
            }
            """
        # result_json = json.dumps(result, ensure_ascii=False, indent=4)
        # return result_json
        return 
