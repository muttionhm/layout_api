from file2image.file2image import secfile2Image,to_images
from layoutDetect.layout2chunk import LayOut,docs_2_chunk_js



def layout(input_path):
    to_images(input_path)
    # 转换成pdf格式并存成图片
    docs_2_chunk_js(input_path)
