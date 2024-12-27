# -*- coding:utf-8_*-
"""
@version:
arthor:wyq
@time:2024/07/05
@file:file2pdf.py
@function:
@modify:
"""

# from docx2pdf import convert
#
# # 单个文件转换
# convert("吉林省建筑信息模型设计应用标准.docx", "output.pdf")
#
# # 也可以转换整个目录
# # convert("path/to/directory")


import os
import subprocess
from utilies.utilies import filename_fix


class file2PDF:
    def __init__(self, path):
        self.path = path

    # 这段是直接doc转docx
    def doc_to_docx(self):
        # 使用LibreOffice的soffice命令进行转换
        docx_path = filename_fix(self.path) + "docx"
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "docx",
                self.path,
                "--outdir",
                os.path.dirname(docx_path),
            ]
        )

    # docx转pdf
    def docx_to_pdf(self):
        path = filename_fix(self.path) + ".docx"
        print(path)
        print(os.path.dirname(path))
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                os.path.dirname(path),
                path,
            ],
        )

    def pptx_to_pdf(self):
        cmd = [
            "soffice",  # LibreOffice命令行工具
            "--headless",  # 无界面模式
            "--convert-to",
            "pdf",  # 指定输出格式为PDF
            self.path,  # 输入的PPT文件
            "--outdir",
            ".",  # 输出目录，这里是当前目录
        ]
        # 运行soffice命令
        try:
            subprocess.run(cmd, check=True)
            print(f"PPT转换为PDF成功")
        except subprocess.CalledProcessError as e:
            print(f"PPT转换为PDF失败：{e}")
