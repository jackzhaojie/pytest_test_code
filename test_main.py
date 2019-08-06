#pytest test1.py -vv --html=report.html --self-contained-html

import pytest
from test_tmp_performance import test_node_performance
from test_tmp_transcode import test_node_transcode
# import test_tmp
import paramiko

# performance class
xx = test_node_performance()
performance_stuple_list = []
presets = ['veryfast', 'fast', 'medium']
videos = ['004-bbb-1080p-h264_10000frames.mp4', '004-bbb-720p-h264_10000frames.mp4']
for video in videos:
  if video == '004-bbb-1080p-h264_10000frames.mp4':
    for preset in presets:
      if preset == 'veryfast':
        [performance_stuple_list.append((index,preset,video,'1920x1080',"3000k")) for index in range(1,9)]
      elif preset == 'medium':
        [performance_stuple_list.append((index,preset,video,'1920x1080',"3000k")) for index in range(1,5)]
      elif preset == 'fast':
        [performance_stuple_list.append((index,preset,video,'1920x1080',"3000k")) for index in range(1,5)]
  elif video == '004-bbb-720p-h264_10000frames.mp4':
    for preset in presets:
      if preset == 'veryfast':
        [performance_stuple_list.append((index,preset,video,'1280x720',"2000k")) for index in range(1,17)]
      elif preset == 'medium':
        [performance_stuple_list.append((index,preset,video,'1280x720',"2000k")) for index in range(1,9)]
      elif preset == 'fast':
        [performance_stuple_list.append((index,preset,video,'1280x720',"2000k")) for index in range(1,9)]
# performance_stuple_list = [(i,j) for j in s2 for i in s1 ]

# print(performance_stuple_list)
# for i in performance_stuple_list:
#     print(i)


# transcode class
bb = test_node_transcode()
info_conf = {
            "-preset":'medium, veryfast, fast',
            "-rc-lookahead": '40, 20', 
            "-bf": '0,3', 
            }

def dict_recursive(info_dic):
    optx = -1
    cmdline = ""
    info_default = info_dic
    options = []
    AL = {}
    for option ,value in info_default.items():
        if value.find(' '):
            value = value.replace(' ','')
        AL[option] = value
        op_value = value + ',NULL'
        op_value = op_value.split(',')
        options.append({option:op_value})
    options.append({'END':'NULL'})
    cmdline_list = []
    leng = len(options) - 1
    option_cmdline(optx, leng, options, cmdline, cmdline_list)
    # print(cmdline_list)
    stuple_list = []
    for index, value in enumerate(cmdline_list):
        write_index = index + 1
        write_stuple = (write_index, value)
        stuple_list.append(write_stuple)
    return stuple_list

def option_cmdline(optx, leng, options, cmdline, cmdline_list):
    # global optx
    optx += 1 
    # global cmdline
    tmp_idx = 0
    tmp_len = 0
    if optx == leng:
        optx -= 1
        return 1
    while [i[tmp_idx] for i in options[optx].values()][0] != 'NULL':
        tmp_len = len([i[tmp_idx] for i in options[optx].values()][0])
        value_data = [i[tmp_idx] for i in options[optx].values()][0]
        key_data = [i for i in options[optx].keys()][0]
        cmdline = cmdline + ' ' + key_data + ' ' + value_data
        jas = option_cmdline(optx, leng, options, cmdline, cmdline_list)
        if jas == 1:
            cmdline_list.append(cmdline.lstrip(' '))
        cmdline = cmdline[0:len(cmdline)-tmp_len-2-len(key_data)]    
        tmp_idx += 1
    tmp_len = len(options) - 1
    optx -= 1
    return 0

m = dict_recursive(info_conf)
transcode_stuple_list = []
videos = ["004-bbb-1080p-h264_10000frames.mp4","004-bbb-720p-h264_10000frames.mp4","004-bbb-540p-h264_10000frames.mp4","004-bbb-480p-h264_10000frames.mp4","004-bbb-360p-h264_10000frames.mp4", "004-bbb-1080p-h264_10000frames.mp4:720p"]
for video in videos:
    if video == '004-bbb-1080p-h264_10000frames.mp4':
        [transcode_stuple_list.append((index[0],index[1],video,'1920x1080',"3000k")) for index in m]
    elif video ==  "004-bbb-1080p-h264_10000frames.mp4:720p":
        video = video.split(':')[0]
        [transcode_stuple_list.append((index[0],index[1],video,'1280x720',"3000k")) for index in m]
    elif video == '004-bbb-720p-h264_10000frames.mp4':
        [transcode_stuple_list.append((index[0],index[1],video,'1280x720',"2000k")) for index in m]
    elif video == '004-bbb-540p-h264_10000frames.mp4':
        [transcode_stuple_list.append((index[0],index[1],video,'960x540',"1600k")) for index in m]
    elif video == '004-bbb-480p-h264_10000frames.mp4':
        [transcode_stuple_list.append((index[0],index[1],video,'640x480',"1100k")) for index in m]
    elif video == '004-bbb-360p-h264_10000frames.mp4':
        [transcode_stuple_list.append((index[0],index[1],video,'480x360',"800k")) for index in m]

# for i in transcode_stuple_list:
#     print(i)
# exit(-1)

# live class
# # test2

class TestClass(object):
    # def test_one(self):
    #     x = 'this'
    #     assert 'x' in x
    
    @pytest.mark.parametrize("index, preset, source_video, source_res, bitrate", performance_stuple_list)
    def test_node_get_performance(self, index, preset, source_video, source_res, bitrate):
        xx.test_performance(index, preset, source_video, source_res, bitrate)

    @pytest.mark.parametrize("index, value, source_video, source_res, bitrate", transcode_stuple_list)
    def test_node_get_transcode(self, index, value, source_video, source_res, bitrate):
        bb.test_transcode(index, value, source_video, source_res, bitrate)
