import os
import sys
import json
import csv
import re

souce_info = [
	         ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/superpop_lollipop_1920x1080_25.yuv', 1920 , 1080],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/superpop_lollipop_1920x1080_50.yuv', 1920 , 1080],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/superpop_lollipop_480_25.yuv', 854 , 480],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/superpop_lollipop_720_25.yuv', 1280 , 720],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/overwatch_1280x720_25.yuv', 1280 , 720],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/overwatch_1080_25.yuv', 1920 , 1080],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/overwatch_1080_50.yuv', 1920 , 1080],
             ['/home/vmaf/D1/tencent/20190403_TestSequence/6/new/overwatch_480_25.yuv', 854 , 480],
            ]

for i in souce_info:
    print(i)
if os.path.exists('vmaf.csv'):
    os.remove('vmaf.csv')
path4 = '/home/zhaojie/zhaojie/vmaf_tool/video/'
video_list = []
for root,dirs,files in os.walk(path4):
#    print(files)
    for name in files:
        video_name = os.path.join(root, name)
        if video_name.endswith('.264') or video_name.endswith('.265'):
            video_list.append(video_name)
print(video_list)
for i in video_list:
   print(i)
#exit(-1)
total_task = 0
for info in souce_info:
    for video in video_list:
        info_mess = info[0].split('/')[-1].split('.')[0]
        video_mess = video.split('/')[-1].split('.')[0]
        e = re.findall(info_mess, video_mess)
        if e != []:
            total_task = total_task + 1
task_num = 0
for info in souce_info:
    for video in video_list:
        info_mess = info[0].split('/')[-1].split('.')[0]
        video_mess = video.split('/')[-1].split('.')[0]
        e = re.findall(info_mess, video_mess)
        if e != []:
            task_num = task_num + 1
            print("total task {}".format(str(total_task)))
            print("running task {}".format(task_num))
            print("running video {}".format(video))
            video_yuv = video.split('.')[0] + '.yuv'
            cmd2 = 'ffmpeg -y -i {} -c:v rawvideo -vsync 0 {}'.format(video, video_yuv)
            print(cmd2)
            l = os.popen(cmd2).read()
            cmd = './run_vmaf yuv420p  {} {} {} {} --out-fmt json'.format(info[1], info[2],info[0], video_yuv)
            print(cmd)
            s = os.popen(cmd).read()
            print(s)
            j = json.loads(s)
            VMAF_score = j['aggregate']['VMAF_score']
            with open('vmaf.csv', 'ab') as out_total:
                csv_write1 = csv.writer(out_total,delimiter=',')
                write_name = video.split('/')[-2] + '/' + video.split('/')[-1]
                csv_write1.writerow([write_name, VMAF_score])
            vmaf_vname = video.split('.')[0] + '.csv'
            if os.path.exists(vmaf_vname):
                os.remove(vmaf_vname)
            with open(vmaf_vname, 'ab') as out_fps:
                lists = j['frames']
                for i in lists:
                    frameNum = i['frameNum']
                    VMAF_score = i['VMAF_score']
                    fps_info = [frameNum, VMAF_score]
                    csv_write2 = csv.writer(out_fps,delimiter=',')
                    csv_write2.writerow(fps_info)
            os.remove(video_yuv)