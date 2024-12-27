# -*- coding:utf-8_*-
'''
@version:
arthor:wyq
@time:2024/07/04
@file:test.py
@function:
@modify:
'''
import os

from flask import Flask

app = Flask(__name__)

files_already_ls = set()
to_analysis = []


def rec_image(input):
    resize_ratio = min((640 / input.shape[0]), (640 / input.shape[1]))
    image = cv2.resize(input, (0, 0), fx=resize_ratio, fy=resize_ratio, interpolation=cv2.INTER_LINEAR)
    # OCR-检测-识别
    ocr_sys = det_rec_functions(image, det_file, rec_file, keys_file)
    # 得到检测框
    dt_boxes = ocr_sys.get_boxes()
    # 识别 results: 单纯的识别结果，results_info: 识别结果+置信度
    results, results_info, img_draw = ocr_sys.recognition_img(dt_boxes)
    results = [i[0] for i in results]
    final_results = ''.join(results)
    return final_results


def cal_like(figure,figure_caption,x_max):
    '''

    :param figure: caption的坐标
    :param figure_caption: 某个figure的坐标
    :param x_max:
    :return:
    '''
    figure_center_x = figure[2]-figure[0]
    figure_caption_x = figure_caption[2]-figure_caption[0]
    if abs(figure_center_x-figure_caption_x)>1/3*x_max:         # 图和说明的中心点差距比1/3的整个图都大……
        return x_max
    else:
        s_1 = abs(figure[1]-figure_caption[1])
        s_2 = abs(figure[1]-figure_caption[3])
        s_3 = abs(figure[3]-figure_caption[1])
        s_4 = abs(figure[3]-figure_caption[3])
        return min([s_1,s_2,s_3,s_4])

# 该方法返回一个词典，key为ocr后的figure，value为figure保存地址
def match_f_c(caption,figure_list,x_max):
    '''

    :param caption: caption的坐标
    :param figure_list: figure的全部坐标列表
    :param x_max:
    :return:
    '''
    result_list = []
    for i in figure_list:
        result_list.append(cal_like(caption,i,x_max))
    min_val,min_index = min(enumerate(result_list),key=lambda x: x[1])
    return figure_list[min_val]

def pdf_process2(input_pdf):
    res = {}
    images = convert_from_path(input_pdf, thread_count=12, dpi=200)
    pdf_name = input_pdf.split('/')[-1]
    res[pdf_name] = {}
    result_figure = {}
    print(f'start process {pdf_name}, the total is {len(images)}')
    for i in tqdm(range(len(images)),total = len(images)):
        # 对于每一张图片
        caption_figure_dist = {}
        image_name = f'images/{pdf_name}_{i}.png'
        # 保存图片
        images[i].save(image_name, 'PNG')
        # 使用cv2读取图片
        img_cv2 = cv2.imread(image_name)
        yolo_result = model(img_cv2)[0]
        x_max = yolo_result.orig_shape[0]
        res_boxes = yolo_result.boxes
        figures = []
        captions = []
        for i_box in res_boxes:
            if int(i_box.cls)==2:
                x1,y1,x2,y2 = map(int,i_box.xyxy[0])
                figures.append([x1,y1,x2,y2])
            if int(i_box.cls)==3:
                x1, y1, x2, y2 = map(int, i_box.xyxy[0])
                captions.append([ x1, y1, x2, y2])
        # figure存放位置为sources/pdf_name/figures/page_x1_y1_x2_y2
        if captions and figures:
            if not os.path.isdir(f'sources/{pdf_name}'):
                os.mkdir(f'sources/{pdf_name}')
            for i_caption in captions:
                caption_text = rec_image(img_cv2[i_caption[1]:i_caption[3],i_caption[0]:i_caption[2]])
                figure = match_f_c(i_caption,figures,x_max)
                save_path = f'sources/{pdf_name}/{i}_{figure[0]}_{figure[1]}_{figure[2]}_{figure[3]}.jpg'
                caption_figure_dist[caption_text]=save_path
                cropped_image = img_cv2[figure[1]:figure[3],figure[0]:figure[2]]
                cv2.imwrite(save_path, cropped_image)
        text = rec_image( img_cv2)
        result_figure.update(caption_figure_dist)
        res[pdf_name][str(i)]={}
        res[pdf_name][str(i)]['text']= text
        res[pdf_name][str(i)]['figure_cation'] =  caption_figure_dist
    return res,result_figure


def pdf_analysis(file_input):
    result = {}
    for i in file_input:
        if i.endswith(".pdf"):
            temp_result, caption_figure = pdf_process2(i)
            result.update(temp_result)
            tmp_data = []
            for cap, img_dir in caption_figure.items():
                tmp_data.append({"Text": cap, "page_id": img_dir})
            img_esp.insert_data_es_by_file(tmp_data)

    #            caption_figure_t.update(caption_figure)

    if result:
        data_re, id_dict = load_file_data(result)
        ori_data.extend(data_re)
        r_api.set_ori_id(id_dict)
        #            ori_id_file.update(id_dict)
        try:
            data_to_es(es_name, data_re)
        except:
            pass
        dr.add_raw_data(data_re)



