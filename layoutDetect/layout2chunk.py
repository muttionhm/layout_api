# -*- coding:utf-8_*-
"""
@version:
arthor:wyq
@time:2024/07/05
@file:layout2chunk.py
@function:
@modify:
"""

import os

# import cv2
# import numpy as np
# import torch

from config import FILES_DIR_PATH, IMAGE_TEMP_PATH
from layoutDetect.document import Document


class LayOut:
    def __init__(self, analysis_list):
        self.analysis_list = analysis_list  
        self.chunk_root_path = os.path.join(FILES_DIR_PATH, "chunks")
        self.image_root_path = IMAGE_TEMP_PATH
        # self.model = YOLO("yolov8-doc.yaml", task="detect")

    # 处理列表
    def docs_2_chunk_json(self):
        results = {}
        result_cls = {}
        for pdfname in self.analysis_list:
            doc = Document(pdfname)
            doc_json,tes = doc.chunk_data()  # 处理每个文件
            results[doc.name] = doc_json
            result_cls.update(tes)

        """
        results = {
            name:{
                id_1:{
                    "type": "title",
                    "context": "标题的内容",
                    "x_y": [1, 1, 2, 2],
                    "page": 1,
                },...,
                id_n: {
                    "type": "context",
                    "context": "标题的内容",
                    "x_y": [4, 4, 5, 5],
                    "page": 10,
                }
            }
        }
        """
        return result_cls

def docs_2_chunk_js(pdf_path):
        doc = Document(pdf_path)
        doc.chunk_data()
        # doc_json,tes = doc.chunk_data()  # 处理每个文件
        # results[doc.name] = doc_json



if __name__ == "__main__":
    analysis_list = ["2403.19735v1", "2403.14403"]
    A = LayOut(analysis_list)
    docs_chunk = A.docs_2_chunk_json()

    # 以下用于保存中间结果
    for data, chunks in docs_chunk.items():
        with open(data, "w", encoding="utf-8") as f:
            f.write(chunks)
