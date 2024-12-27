# -*- coding:utf-8_*-
"""
@version:
arthor:wyq
@time:2024/07/05
@file:file2image.py
@function:
@modify:
该文件为本文件下主要执行，并可以得到相应的图片，保存在文档的文件夹内


"""
import os.path
from pdf2image import convert_from_path
from tqdm import tqdm
from api_redis import redis_api
from config import FILES_DIR_PATH, IMAGE_TEMP_PATH
from file2image.file2pdf import file2PDF
from utilies.utilies import filename_fix


# pdf转化为图片并保存
def pdf_2_image(input_pdf):
    path = input_pdf
    res = {}
    images = convert_from_path(path, thread_count=12, dpi=300)  # dpi表示每英寸长的像素点数，默认200
    # 去掉了后缀名
    pdf_name = filename_fix(path.split('/')[-1])
    res[pdf_name] = {}
    print(f"开始处理 {pdf_name}, 总页数{len(images)}张")
    for i in tqdm(range(len(images)), total=len(images)):
        image_path = f"{IMAGE_TEMP_PATH}/{pdf_name}/{i}.png"  #
        # 检查or建立文件夹
        os.makedirs(f"{IMAGE_TEMP_PATH}/{pdf_name}/", exist_ok=True)
        # 按页保存图片
        images[i].save(image_path, "PNG")


class file2Image:
    def __init__(self):
        self.r_api = redis_api()
        self.to_analysis = []

    # 检查是否已经解析过
    def check_is_updating(self):
        return self.r_api.check_is_updating()

    def set_updating(self):
        self.r_api.set_updating()

    def unset_updating(self):
        self.r_api.unset_updating()

    def check_already_redis(self, filename):
        return self.r_api.check_already(filename)

    # 更新redis中的已解析文件
    def set_already_redis(self, filename):
        self.r_api.set_already(filename)

    # 更新已解析文件的列表
    def updata_already(self):
        already_list = list(self.files_already_ls)
        with open("already_files.txt", "w", encoding="utf-8") as f:
            f.writelines("\n".join(already_list))

    # 单文件解析
    def pdfs_analysis(self, in_path):
        result = {}
        f2p = file2PDF(in_path)
        if in_path.endswith(".doc"):
            f2p.doc_to_docx()
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".docx"):
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".ppt"):
            f2p.pptx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".pdf"):
            pdf_2_image(in_path)
        else:
            print(f"{in_path.split('/')[-1]}是暂不支持的文件格式")

    # 主运行函数
    def run_file2image(self):
        self.to_analysis = []
        # 获取当前文件所在目录的父目录路径
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.dirname(parent_dir)
        # 拼接完整路径
        folder_path = os.path.join(current_dir, FILES_DIR_PATH)
        filename_list = os.listdir(folder_path)
        for filename in filename_list:
            if filename != ".DS_Store":
                if self.check_already_redis(filename):  # 对于已经解析过的文件
                    continue
                self.pdfs_analysis(folder_path + "/" + filename)
                self.to_analysis.append(filename)
                self.set_already_redis(filename)


# 初始化参数为上传文件的临时地址，然后直接根据文件路径解析并保存到向量数据库以及es
class secfile2Image:
    def __init__(self,doc_path_list):
        self.to_analysis = []
        self.doc_path_list = doc_path_list
        
    # 单文件解析
    def pdfs_analysis(self, in_path):
        f2p = file2PDF(in_path)
        if in_path.endswith(".doc"):
            f2p.doc_to_docx()
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".docx"):
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".ppt"):
            f2p.pptx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".pdf"):
            pdf_2_image(in_path)
        else:
            print(f"{in_path.split('/')[-1]}是暂不支持的文件格式")

    # 主运行函数
    def run_file2image(self):
        file_names = [i.split('/')[-1] for i in self.doc_path_list]
        ready_files = os.listdir('output/images')
        ready_files  = [i+'.pdf' for i in ready_files]
        for index,filename in enumerate(file_names):
                self.to_analysis.append(filename)
                if filename in ready_files:
                    continue
                self.pdfs_analysis(self.doc_path_list[index])



def to_images(file_path):
        f2p = file2PDF(file_path)
        if in_path.endswith(".doc"):
            f2p.doc_to_docx()
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".docx"):
            f2p.docx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".ppt"):
            f2p.pptx_to_pdf()
            pdf_2_image(in_path)
        elif in_path.endswith(".pdf"):
            pdf_2_image(in_path)
        else:
            print(f"{in_path.split('/')[-1]}是暂不支持的文件格式")         
 



if __name__ == "__main__":
    A = file2Image()
    A.run_file2image()
