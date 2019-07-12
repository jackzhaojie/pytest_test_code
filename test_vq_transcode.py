import os
import re
from scp import SCPClient
import csv
import paramiko
import sys
import time
import json
import platform
from test_vq_psnr import psnr_get
from test_vq_vmaf import vmaf_get

# default server infomation
ssh_server = '172.16.231.31'
ssh_port = '22'
ssh_name = 'root'
ssh_password = 'admin123'
node_test_folder = '/D0/test/'
node_use_cmd = 'ffmpeg -y -r 30 -video_size 1920x1080 -i source_test.yuv -c:v v205h264 -an -preset veryfast -bf 3 -vsync 0 -rc-lookahead 40 -b:v 8000k  -g 90  out_test.264'

optx = -1
cmdline = ""
source_format = 'yuv'
# other_option = 'v205h264;-ratetol_1_-thread_4 libx264;-x264-params_bframes=3_-g_30'
other_option = ''


mount_ip = "172.16.15.31"
mount_folder = "/mnt/raid1/data/video"

psnr_open = 0
vmaf_open = 1

# -------------------------------------------------------------------------------
# running command locally
# -------------------------------------------------------------------------------

def run(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

# -------------------------------------------------------------------------------
# upload files
# -------------------------------------------------------------------------------

def upload(source):
    client = get_connect()
    print('\n******* Upload source video  to remote server... \n')
    scp = SCPClient(client.get_transport())
    scp.put(source, node_test_folder)
    print('All source streams are transfered!')
    client.close()

# -------------------------------------------------------------------------------
# download files
# -------------------------------------------------------------------------------

def download(transcode_file):
    client = get_connect()
    print('\n******* Download transcoded video to local... \n')
    scp = SCPClient(client.get_transport())
    temp_cwd = dir_name
    # get_file = node_test_folder + transcode_file
    get_file = transcode_file
    scp.get(get_file, str(temp_cwd))
    client.close()

def get_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_server, port=ssh_port, username=ssh_name, password=ssh_password)
    return client

def exec_cmdline(node_cmd):
    client = get_connect()
    stdin, stdout, stderr = client.exec_command('cd {};{}'.format(node_test_folder, node_cmd))
    print('\nThe command to be executed is: \n' + node_cmd)
    for line in stdout:
        print(line.strip('\n'))
    client.close()

def init_mount():
    client = get_connect()
    stdin, stdout, stderr = client.exec_command("mount -o remount, rw /")
    stdin, stdout, stderr = client.exec_command("mkdir /D1;mount -t nfs -o nolock {}:{} /D1".format(mount_ip, mount_folder))
    stdin, stdout, stderr = client.exec_command("mkdir {}".format(node_test_folder))
    print('\n init mount \n')
    for line in stdout:
        print(line.strip('\n'))
    client.close()

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
    option_cmdlines(optx, leng, options, cmdline, cmdline_list)
    return cmdline_list

def option_cmdlines(optx, leng, options, cmdline, cmdline_list):
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
        jas = option_cmdlines(optx, leng, options, cmdline, cmdline_list)
        if jas == 1:
            cmdline_list.append(cmdline.lstrip(' '))
        cmdline = cmdline[0:len(cmdline)-tmp_len-2-len(key_data)]    
        tmp_idx += 1
    tmp_len = len(options) - 1
    optx -= 1
    return 0

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

def v205_transcode(cmdline, upload_flag):
    if upload_flag == 1:
        if source_format == 'yuv' and video_url == '':
            upload(source_video)
            client = get_connect()
            stdin, stdout, stderr = client.exec_command(str('sync'))
            client.close()
        elif source_format != 'yuv' and video_url == '':
            upload(source_yuv_path)
            client = get_connect()
            stdin, stdout, stderr = client.exec_command(str('sync'))
            client.close()
    if source_format == 'yuv' and video_url != '':
        # cmdline change source.yuv to the link
        cmdline = cmdline.replace('source_test.yuv', video_url)
    elif source_format != 'yuv' and video_url != '':
        # cmdline change source.yuv to the link
        cmdline = cmdline.replace('source_test.yuv', video_url)
    cmdline = cmdline.replace('test.yuv', video_url)

    time.sleep(2)
    client = get_connect()    
    print('\nThe command to be executed is: \n' + cmdline)
    stdin, stdout, stderr = client.exec_command(str('cd {}; pwd;{}'.format(node_test_folder,cmdline)))
    print('\n******* Start Encoding...\n')
    for line in stdout:
        print(line.strip('\n'))
    download(node_out_video)    
    client.close()

def option_mark(options):
    dict_mark = options.split(' ')
    dict_mark_info = {}
    for index, value in enumerate(dict_mark):
        if value.startswith('-') and dict_mark[index +1].find('-') == -1 :
            dict_mark_info[value] = dict_mark[index+1]
    return dict_mark_info

def deal_txt(txt):
    with open(txt,"r") as get_option:
        s = get_option.readlines()
        dic = {}
        for i in s:
            i = i.replace(' ','')
            string = i.rstrip('\n').split('=', 1)
            dic[string[0]] = string[1]
    return dic

def make_folder(get_info):
    option_dict = option_mark(get_info)
    vcodec = option_dict['-c:v']
    preset = option_dict['-preset']
    bframe = option_dict['-bf']
    lookahead = option_dict['-rc-lookahead']
    dir_tmp = vcodec+'_'+ preset + "_bf" + bframe + '_lookahead' + lookahead
    return option_dict, dir_tmp

def video_path(format):
    source_video_list = []
    formats = format.split(',')
    for root,dirs,files in os.walk(os.getcwd()):
        for name in files:
            for fmt in formats:
                video_name = os.path.join(root, name)
                if video_name.endswith(fmt):
                    source_video_list.append(video_name)
    return source_video_list

folder_conf = deal_txt("test.conf")

transfer_list = []
# match option
for folder in folder_conf:
    conf_info = json.loads(folder_conf[folder])
    cmd_list = dict_recursive(conf_info)
    for folder_option in cmd_list:
        basic_cmd = node_use_cmd
        value_dicts = option_mark(folder_option)  # value is folder_option
        basic_cmd_list = [i for i in basic_cmd.split(' ') if i != ' ']
        for dict_key, dict_value in value_dicts.items():
            for list_index, list_value in enumerate(basic_cmd_list):
                if dict_key == '-bf' and dict_value == '0' and dict_key == list_value: 
                    basic_cmd_list[list_index+1] = str(dict_value) + ' -b-adapt 0'
                elif dict_key == list_value: 
                    basic_cmd_list[list_index+1] = dict_value
        # print(basic_cmd_list)
        cmd = ' '.join(basic_cmd_list)
        transfer_list.append((folder, cmd))
# match value and option to set cmdline

source_videos = video_path(source_format)
test_set = []
for i in source_videos:
    for j in transfer_list:
        if platform.system() == 'Linux':
            test_folder = i.split('/')[-2]
        elif platform.system() == 'Windows':
            test_folder = i.split('\\')[-2]
        if test_folder == j[0]:
            test_set.append((test_folder, i, j[1]))

get_source_info = []
mount_flag = 1
for test_info in test_set:
    upload_flag = 1
    test_folder = test_info[0]
    source_video = test_info[1]
    cmdline_use = test_info[2]
    
    # exit(-1)
    info_dict, dir_tmp = make_folder(cmdline_use)
    dir_name = os.path.join(os.path.split(source_video)[0], dir_tmp)
    if os.path.exists(dir_name):
        pass
    else:
        os.mkdir(dir_name)

    video_res = info_dict['-video_size']
    video_fps = info_dict['-r']
    video_bitrate = info_dict['-b:v']
    video_vcodec = info_dict['-c:v']
    source_yuv = source_video.split('.')[0] + '.yuv'
    
    # if source_video.endswith('.yuv'):
    #     frames_cmdline = 'ffprobe -video_size {} -v error -count_frames -select_streams v:0  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {}'.format(video_res, source_video)
    # else: 
    #     frames_cmdline = 'ffprobe -v error -count_frames -select_streams v:0  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {}'.format(source_video)
    # print(frames_cmdline)
    # video_frames = run(frames_cmdline)
    # print(video_frames)
    video_frames = 5000

    

    source_yuv_path = 'ok' + source_yuv
    if source_format != 'yuv':
        if os.path.exists(source_yuv) :
            pass
        else:
            yuv_cmdline = 'ffmpeg -y -i {}  -c:v rawvideo -vsync 0 {}'.format(source_video, source_yuv)
            print(yuv_cmdline)
            run(yuv_cmdline)
        source_yuv_path = os.path.join(os.path.split(source_video)[0], source_yuv)
    # print(source_yuv_path)
    if video_vcodec == 'v205h264' or video_vcodec == 'libx264':
        out_video = os.path.split(source_video)[1].split('.')[0] + '_' + video_bitrate + '.264'
    elif video_vcodec == 'v205h265' or video_vcodec == 'libx265':
        out_video = os.path.split(source_video)[1].split('.')[0] + '_' + video_bitrate + '.265'
    out_video_path = os.path.join(dir_name, out_video)
    conf_info2 = json.loads(folder_conf[test_folder])
    if int(video_fps) < 60:
        video_gop = 3*int(video_fps)
    else:
        video_gop = 2*int(video_fps)
    if 'url' not in conf_info2.keys():
        video_url = ''
    else:
        video_url = conf_info2['url']
        if mount_flag == 1:
            init_mount()
            mount_flag = 0
    # if source_video in get_source_info[0]:
    get_source_info.append((source_video,video_res))
    option_list = [i for i in cmdline_use.split(' ') if i!= '' ]
    # print(option_list)
    if other_option == '':
        for index, value in enumerate(option_list):
            if value == '-g':
                option_list[index+1] = str(video_gop)
    else:
        vcodec_info = other_option.split(' ')
        for i in vcodec_info:
            match_vcodec = i.split(';')[0]
            match_option = ' '.join(i.split(';')[1].split('_'))
            if match_vcodec == video_vcodec:
                for index, value in enumerate(option_list):
                    if value == '-g':
                        option_list[index+1] = str(video_gop) + ' ' + match_option
    cmdline_use = ' '.join(option_list)

    if video_vcodec == 'v205h264' or  video_vcodec == 'v205h265':
        
        node_out_video = node_test_folder  + out_video
        cmdline_use = cmdline_use.replace('out_test.264', node_out_video)
        # print(cmdline_use)
        # v205_transcode(cmdline_use, upload_flag)
        upload_flag = 0
    elif video_vcodec == 'libx264' or  video_vcodec == 'libx265':
        cmdline_use = cmdline_use.replace('out_test.264', out_video_path)
        cmdline_use = cmdline_use.replace('source_test.yuv', source_yuv_path)
        print(cmdline_use)
        # run(cmdline_use)
    elif video_vcodec == 'h264_qsv':
        cmdline_use = cmdline_use.replace('out_test.264', out_video_path)
        cmdline_use = cmdline_use.replace('source_test.yuv', source_yuv_path)
        print(cmdline_use)
        # run(cmdline_use)
    
    bitrate_csv_name = os.path.join(os.path.split(out_video_path)[0],'bitrate.csv') 
    if os.path.exists(bitrate_csv_name):
        os.remove(bitrate_csv_name)
    video_names = [i for i in os.listdir(os.path.split(out_video_path)[0]) if i.endswith('.264') or i.endswith('.265')]
    with open(bitrate_csv_name, 'a', newline="") as out:
        for all_file in video_names:
            all_file = dir_name + '/' + all_file
            size = os.path.getsize(all_file)
            bitrate = round(8*float(video_fps)*float(size)/1000/float(video_frames),2)
            csv_write = csv.writer(out,delimiter=',')
            csv_write.writerow([all_file, bitrate])
# psnr open

video_name_path = video_path('264,265')
video_names_list = []
video_names = [video_names_list.append(i) for i in video_name_path if  i not in video_names_list]
source_names_list = []
source_names = [source_names_list.append(i) for i in get_source_info if  i not in source_names_list]

def get_psnr_vmaf_value(csv_name ,source_names_list, video_names_list, value_flag):
    if os.path.exists(csv_name):
        os.remove(csv_name)
    with open(csv_name,'a') as csv_psnr:
        csv_writer=csv.writer(csv_psnr,dialect='excel')
        csv_writer.writerow(["source_video", "out_video", value_flag])
        for source in source_names_list:
            for output in video_names_list:
                source_v = source[0]
                source_res = source[1]
                if source_v != output:
                    source_mess = os.path.split(source_v)[0]
                    output_mess = os.path.split(output)[0]
                    e = re.findall(source_mess, output_mess)
                    if e != []:
                        if value_flag == 'Y-PSNR':
                            get_value = psnr_get(source_res, source_v, output)
                        elif value_flag == 'VMAF':
                            get_value = vmaf_get(source_res, source_v, output)
                        source_write = os.path.split(source_v)[1]
                        output_write = '/'.join(output.split('/')[-3:]) 
                        csv_writer.writerow([source_write, output_write, get_value])
if psnr_open == 1:
    get_psnr_vmaf_value('all_y_psnr.csv', source_names_list, video_names_list, 'Y-PSNR')
if vmaf_open == 1:
    get_psnr_vmaf_value('all_vmaf.csv', source_names_list, video_names_list, 'VMAF')
