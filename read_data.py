import csv 
import os
import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt
import time

def read_csv(csv_name):
    with open(csv_name, 'r') as csv_file:
        reader = [i.strip('\n') for i in csv_file.readlines()]
    return reader

def video_path(csv_get):
    source_video_list = []
    for root,dirs,files in os.walk(os.getcwd()):
        for name in files:
            if name == csv_get:
                csv_path = os.path.join(root, name)
                source_video_list.append(csv_path)
    return source_video_list

def dict_get(dict1, objkey, default):
    tmp = dict1
    for k,v in tmp.items():
        if k == objkey:
            return v
        else:
            if type(v) is dict:
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
            if type(v) is list:
                ret = dict_get(v[0], objkey, default)
                if ret is not default:
                    return ret
    return default

bitrate_csv = video_path("bitrate.csv")
bitrate_data = [c for i in bitrate_csv for c in read_csv(i)]
psnr_data = read_csv('all_y_psnr.csv')

info = []
for psnr in psnr_data:
    psnr_info_list = psnr.split(',')
    psnr_match_info = psnr_info_list[1]
    for bitrate in bitrate_data:
        bitrate_info_list = bitrate.split(',')
        bitrate_match_info = '/'.join(bitrate_info_list[0].split('/')[-3:])
        bitrate_value = bitrate_match_info.split('/')[-1].split('_')[-1].split('.')[0]
        if psnr_match_info == bitrate_match_info:
            psnr_info_list.append(bitrate_info_list[1])
            psnr_info_list.append(bitrate_value)
            info.append(psnr_info_list)
# print(info)

for i in info:
    print(i)
list1 = []
list2 = []
none_list = []
for index, value in enumerate(info) :
    if value[0] not in none_list:        
        none_list.append(value[0])
        list1 = []
        list2.append({value[0]:list1})
    dict_change_info = {
            "codec_info" : value[1].split('/')[1],
            "y_value_info" : value[2],
            "x_bitrate_info":value[3],
            "target_bitrate_info": value[4]
        }
    list1.append(dict_change_info)
for i in list2:
    for key,value in i.items():
        extra_add = []
        for k in value:
            codec_value = dict_get(k, 'codec_info', None)
            k.pop("codec_info")
            extra_add.append({codec_value:k})
        i[key] = extra_add
for i in list2:
    list3 = []
    list4 = []
    none_list = []
    for keys, values in i.items() :
        for index, value in enumerate(values) :
            for key, valu in value.items():
                if key not in none_list:        
                    none_list.append(key)
                    list3 = []
                    list4.append({key : list3 })
                dict_change_info = valu
                list3.append(dict_change_info)
    for keys, values in i.items() :
        i[keys] = list4

# print(list2)


work_name = 'tmp.xlsx'
if os.path.exists(work_name):
    os.remove(work_name)
workbook = xlsxwriter.Workbook(work_name)
worksheet = workbook.add_worksheet()
for write_index, write_info in enumerate(list2[:5]) :
    # 视频字典分割    
    print(write_index)
    headings = ['Video', ' ' ]
    for key, value in write_info.items():
        video = key
        write_row1 = [video.split('.')[0], 'Target Bitrate',]
        write_row2 = []
        # print(value)
        write_len = len(value)
        # print(value)
        # print("write_len {}".format(write_len))
        target_bitrate_info_flag = 1
        for index, value in enumerate(value):
            for key2,value2 in value.items():
                vcodec = key2
                bitrate_num = len(value2)
                vcodec_flag = 1
                bitrate_flag = 1
                for cc in value2:
                    x_bitrate_info = cc["x_bitrate_info"]
                    y_value_info = cc["y_value_info"]
                    target_bitrate_info = cc["target_bitrate_info"]
                    if vcodec_flag == 1:
                        headings.append(vcodec)
                        headings.append(" ")
                        write_row1.append('real bitrate')
                        write_row1.append('PSNR')
                        vcodec_flag = 0
                    write_row2.append(target_bitrate_info)
                    write_row2.append(x_bitrate_info)
                    write_row2.append(y_value_info)                        
            xx = [write_row2[i:i + 3] for i in range(0, len(write_row2), 3 )]
            ccc = [ xx[i::bitrate_num] for i in range(bitrate_num)]
    pp = []
    for i in ccc:
        cc = []
        for num in range(write_len):
            cc = cc + i[num]
        cc = [cc[i] for i in range(0,len(cc) ) if str(cc[i]).endswith('k') == False or i == 0]
        pp.append(cc)

    locate_path = 1 + write_index * (7 + bitrate_num) 
    worksheet.write_row('A{}'.format(str(locate_path)), headings)       
    worksheet.write_row('A{}'.format(str(locate_path + 1)), write_row1)
    sorted_pp = sorted(pp, key=lambda my_sort: my_sort[0])
    for i, value in enumerate(sorted_pp) :
        info2 = [' '] + value
        index = locate_path + 2 + int(i)
        worksheet.write_row('A{}'.format(str(index)), info2)
    cc = [i for i in headings if i != ' ']
    info = []
    plt.figure() # 初始化图层对象
    for index, c in enumerate(cc) :
        if c != 'Video':
            print(index)
            x_num = [i[index*2 -1] for i in sorted_pp]
            y_num = [i[index*2] for i in sorted_pp]
            x_num = list(map(lambda x : float(x) ,x_num))
            y_num = list(map(lambda x : float(x) ,y_num))
            plt.plot(x_num, y_num,label='{} Line'.format(c))
    # x_index = [i for i in range(0,5001,500)]
    # y_index = [i for i in range(20,51,5)]
    # print(xx)
    # exit(-1)
    # x_group_labels = list(x_index)
    # y_group_labels = list(y_index)
    # a = np.arange(len(x_index))
    # b = np.arange(len(y_index))
    # plt.xticks(a, x_group_labels)
    # plt.yticks(b, y_group_labels)

    png_name = "tmp{}.png".format(write_index)
    plt.xlabel('bitrate/kbps')
    plt.ylabel('psnr')
    plt.title(video.split('.')[0])
    plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0)
    plt.savefig(png_name,dpi=200,bbox_inches='tight')
    pic_path = chr(ord('A') + 2 + write_len*2)
    worksheet.insert_image('{}{}'.format(pic_path ,locate_path) , png_name, {'x_scale': 0.5, 'y_scale': 0.5})
    time.sleep(1)
workbook.close()
c = [i for i in os.listdir(os.getcwd()) if i.endswith('.png')]
for i in c:
    os.remove(i)