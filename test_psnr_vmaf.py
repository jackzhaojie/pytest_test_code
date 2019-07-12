import os
import re
from scp import SCPClient
import csv
import paramiko
import getopt
import sys
import time
import math
import numpy as np
import json

psnr_open = 'true'
transcode_open  = 'true'

# default server infomation
ssh_flag = 0
ssh_server = '172.16.249.4'
ssh_port = '22'
ssh_name = 'root'
ssh_password = 'admin123'
node_test_folder = '/D0/test/'

file_local_folder = ''
vcodec_local_folder = ''

def version():
    print('vq_test_script ver 1.0.0 05/12/2018 15:33')

version()

def usage():
    print("Usage: all_ffmpeg_ubuntu.py [OPTION]...\n")
    print("    -f   input video format")
    print("    -s   ssh server ip")
    print("    -t   ssh server port")
    print("    -u   ssh server name")
    print("    -p   ssh server password")
    print("    -e   ssh server test folder")
    print("    -r   file local folder")
    print("    -l   vcodec local folder")
    print("    -o   transcode disable and able")
    
    
    
    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:f:s:t:u:p:e:r:l:o')
except getopt.GetoptError:
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt == '-h':
        usage()
        sys.exit(2)
    elif opt == '-f':
        source_format = str(arg)
    elif opt == '-s':
        ssh_flag = 1
        ssh_server = str(arg)
    elif opt == '-t':
        ssh_port = str(arg)
    elif opt == '-u':
        ssh_name = str(arg)
    elif opt == '-p':
        ssh_password = str(arg)
    elif opt == '-e':
        node_test_folder = str(arg)
    elif opt == '-r':
        file_local_folder = str(arg)
    elif opt == '-l':
        vcodec_local_folder = str(arg)
    elif opt == '-o':
        transcode_open = str(arg)
    else:
        usage()
        sys.exit(2)


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
    print('\n******* Connecting to remote server... \n')
    scp = SCPClient(client.get_transport())
    scp.put(source, node_test_folder)
    print('All source streams are transfered!')
    client.close()


# -------------------------------------------------------------------------------
# download files
# -------------------------------------------------------------------------------

def download(transcode_file):
    client = get_connect()
    scp = SCPClient(client.get_transport())
    temp_cwd = os.getcwd()
    print(node_test_folder)
    print(transcode_file)
    get_file = node_test_folder + transcode_file
    print(get_file)
    scp.get(get_file, str(temp_cwd))
    client.close()

def get_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_server, port=ssh_port, username=ssh_name, password=ssh_password)
    return client

def make_testdir():
    client = get_connect()
    stdin, stdout, stderr = client.exec_command(str('mkdir {}'.format(node_test_folder)))
    print(str('mkdir {}'.format(node_test_folder)))
    print('\n******* make the test...\n')
    for line in stdout:
        print(line.strip('\n'))
    client.close()

def clean_node():
    client = get_connect()
    stdin, stdout, stderr = client.exec_command(str('cd {}; pwd;rm *'.format(node_test_folder) ))
    print(str('cd {}; pwd;rm *'.format(node_test_folder)))
    print('\n******* Clean the node...\n')
    for line in stdout:
        print(line.strip('\n'))
    client.close()

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
            upload(source_video_path)
            client = get_connect()
            stdin, stdout, stderr = client.exec_command(str('sync'))
            client.close()
        elif source_format != 'yuv' and video_url == '':
            upload(source_yuv)
            client = get_connect()
            stdin, stdout, stderr = client.exec_command(str('sync'))
            client.close()
    if source_format == 'yuv' and video_url != '':
        # cmdline change source.yuv to the link
        cmdline = cmdline.replace(source_yuv, video_url)
    elif source_format != 'yuv' and video_url != '':
        # cmdline change source.yuv to the link
        cmdline = cmdline.replace(source_yuv, video_url)

    time.sleep(2)
    client = get_connect()    
    print('\nThe command to be executed is: \n' + cmdline)
    stdin, stdout, stderr = client.exec_command(str('cd {}; pwd;'.format(node_test_folder) + ''.join(cmdline)))
    print('\n******* Start Encoding...\n')
    for line in stdout:
        print(line.strip('\n'))
    print('\n*******Now downloading transcoded video  to local. \n')
    download(output_264)    
    client.close()

    # print("*******************\n")

def deal_txt(txt):
    get_option = open(txt,'r')
    s = get_option.readlines()
    dic = {}
    for i in s:
        string = i.rstrip('\n').split('=', 1)
        dic[string[0]] = string[1]
    return dic

def get_lines(filepath):
    with open(filepath) as file_object:
        lines=file_object.readlines()
        return lines

def get_psnr(mse):
    log10 = math.log10
    return round(10.0*log10(float(255*255)/float(mse)), 2)

def change(option):
    source = option + ' {}'
    return source

def match(option, string):
    s = re.findall(option, string)
    if s is not None:
        if vcodec == 'v205h264':
            source = source_yuv
        elif vcodec == 'libx264' or vcodec == 'h264_qsv':
            source = source_yuv_path
        
        if s[0] == '-r': new = string.replace(change(s[0]), change(s[0]).format(video_fps))
        elif s[0] == '-video_size': new = string.replace(change(s[0]), change(s[0]).format(video_res))
        elif s[0] == '-i': new =string.replace(change(s[0]), change(s[0]).format(source))
        elif s[0] == '-c:v': new =string.replace(change(s[0]), change(s[0]).format(vcodec))
        elif s[0] == '-b:v': new =string.replace(change(s[0]), change(s[0]).format(bitrate))
        # elif s[0] == '-bf': new =string.replace(change(s[0]), change(s[0]).format(bf))
        elif s[0] == '-s': new =string.replace(change(s[0]), change(s[0]).format(video_res))
        elif s[0] == '-g': new =string.replace(change(s[0]), change(s[0]).format(video_gop))
        elif s[0] == '-outw': new =string.replace(change(s[0]), change(s[0]).format(video_width))
        elif s[0] == '-outh': new =string.replace(change(s[0]), change(s[0]).format(video_height))
        elif s[0] == '0': new =string.replace(change(s[0]), change(s[0]).format(output_264))
        else:
            print('no option value {} and exit'.format(s))
            exit(-1)
        return new

cmdlines = deal_txt("cmdline.txt")

if ssh_flag == 1:
    make_testdir()
listdir1 = os.listdir(os.getcwd())

if file_local_folder == '':
    test_folder = listdir1
else:
    test_folder = [file_local_folder]

source_video_list = []
for root,dirs,files in os.walk(os.getcwd()):
    for name in files:
        video_name = os.path.join(root, name)
        if video_name.endswith(source_format):
            source_video_list.append(video_name)

for i in test_folder:
    upload_flag = 1
    if os.path.isdir(i):
        os.chdir(i)
        for video_path,cmd in cmdlines.items():
            folder = video_path
            if os.path.exists(folder):
                pass
            else:
                os.mkdir(folder)
        options = deal_txt("option.txt")
        # video_fps = options['fps']
        # video_res = options['res']
        # video_width = video_res.split('x')[0]
        # video_height = video_res.split('x')[1]
        # video_frames = options['frames']
        video_bitrates = options['bitrate'].split(',')

        source_video = [i for i in os.listdir(os.getcwd()) if i.endswith(source_format)][0]
        frames_cmdline = 'ffprobe -v error -count_frames -select_streams v:0  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {}'.format(source_video)
        video_frames = run(frames_cmdline)
        info_cmdline = 'ffprobe -v quiet -print_format json -show_format -select_streams v:0 -show_streams -i {}'.format(source_video)
        video_info_str = run(info_cmdline)
        video_info_json = json.loads(video_info_str)
        video_fps = round( eval( dict_get(video_info_json, 'r_frame_rate', None)))
        video_width = round( eval( str(dict_get(video_info_json, 'width', None))))
        video_height = round( eval( str(dict_get(video_info_json, 'height', None))))
        video_res = str(video_width) + 'x' + str(video_height)


        if 'url' not in options.keys():
            video_url = ''
        else:
            video_url = options['url']

        if int(video_fps) < 60:
            video_gop = 3*int(video_fps)
        else:
            video_gop = 2*int(video_fps)

        if transcode_open == 'true':
            path = os.getcwd()
            source_video = [i for i in os.listdir(os.getcwd()) if i.endswith(source_format)][0]
            source_index = source_video.split('.')[0]
            source_yuv = source_index + '.yuv'
            if source_format != 'yuv':
                if os.path.exists(source_yuv) :
                    pass
                else:
                    yuv_cmdline = 'ffmpeg -y -i {}  -c:v rawvideo -vsync 0 {}'.format(source_video, source_yuv)
                    print(yuv_cmdline)
                    run(yuv_cmdline)
            else:
                pass

            listdir2 = os.listdir(os.getcwd())
            for j in listdir2:
                if os.path.isdir(j):
                    os.chdir(j)
                    print(os.getcwd())
                    for video_path,cmd in cmdlines.items():
                        for bitrate in video_bitrates:
                            vcodec = video_path.split('_')[0]
                            if vcodec == 'qsvh264':
                                vcodec = 'h264_qsv'
                            source_yuv_path = '../' + source_yuv
                            source_video_path = path + '/' + source_video
                            output_264 = source_index + '_' + bitrate + '.264'
                            if vcodec == 'v205h264' and j == video_path:
                                # cmdline = cmd.format(video_fps, video_res, source_yuv, vcodec, bitrate, video_width, video_height ,video_gop, output_264)
                                info_tmp = cmd.split('{}')
                                options = []
                                cmdline = cmd
                                for i in info_tmp:
                                    if i != '0' and i != '':
                                        option = i.split(' ')[-2]
                                        cmdline = match(option, cmdline)
                                print(cmdline)
                                # exit(-1)
                                # v205_transcode(cmdline, upload_flag)
                                upload_flag = 0
                            elif vcodec == 'libx264'and j == video_path:
                                info_tmp = cmd.split('{}')
                                options = []
                                cmdline = cmd
                                for i in info_tmp:
                                    if i != '0' and i != '':
                                        option = i.split(' ')[-2]
                                        cmdline = match(option, cmdline)
                                print(cmdline)
                                # run(cmdline)
                            elif vcodec == 'h264_qsv'and j == video_path:
                                info_tmp = cmd.split('{}')
                                options = []
                                cmdline = cmd
                                for i in info_tmp:
                                    if i != '0' and i != '':
                                        option = i.split(' ')[-2]
                                        cmdline = match(option, cmdline)
                                print(cmdline)
                                # run(cmdline)
                            
                    if os.path.exists('bitrate.csv'):
                        os.remove('bitrate.csv')
                    video_names = [i for i in os.listdir(os.getcwd()) if i.endswith('.264')]
                    psnr_write = []
                    with open('bitrate.csv', 'a', newline="") as out:
                        for all_file in video_names:
                            size = os.path.getsize(all_file)
                            bitrate = round(8*float(video_fps)*float(size)/1000/float(video_frames),2)
                            csv_write = csv.writer(out,delimiter=',')
                            csv_write.writerow([all_file, bitrate])
                    os.chdir('../')
        if ssh_flag == 1:
            clean_node()
        os.chdir('../')

# all video transcode

# get all video path

# transcode_video_list = []
# for root,dirs,files in os.walk(os.getcwd()):
#     for name in files:
#         video_name = os.path.join(root, name)
#         if video_name not in source_video_list:
#             if video_name.endswith('.264') or video_name.endswith('.265'):
#                 transcode_video_list.append(video_name)

# psnr_vmaf_data = []
# if os.path.exists('average_psnr_vmaf.csv'):
#     os.remove('average_psnr_vmaf.csv')


        
        if psnr_open == 'true':
            if vcodec_local_folder == '':
                change_folder = listdir2
            else:
                change_folder == [vcodec_local_folder]
            
            psnr_vmaf_data = []
            if os.path.exists('average_psnr_vmaf.csv'):
                os.remove('average_psnr_vmaf.csv')

            for path in change_folder:
                if os.path.isdir(path):
                    os.chdir(path)
                    measure_video = [i for i in os.listdir(os.getcwd()) if i.endswith('.264')]        
                    for video in measure_video:
                        psnr_data_tmp = []
                        out_yuv = video.split('.')[0] + '.yuv'

                        # get yuv and compare psnr

                        ffmpeg_yuv_cmd = 'ffmpeg -y -i {} -c:v rawvideo -vsync 0 {}'.format(video, out_yuv)
                        print(ffmpeg_yuv_cmd)
                        run(ffmpeg_yuv_cmd)
                        psnr_cmd = r'ffmpeg -s {} -i ../{} -s {} -i {} -lavfi psnr="stats_file=psnr.log" -f null /dev/null'.format(video_res,source_yuv, video_res,out_yuv) 
                        print(psnr_cmd)
                        run(psnr_cmd)                        
                        time.sleep(1)
                        os.remove(out_yuv)
                        psnr_log_csv_name = "psnr_" + source_yuv.split('.')[0] +'-'+ video.split('.')[0] + '.csv'
                        lines = get_lines('psnr.log')
                        # list1 = []
                        # for line in lines:
                        #     line = line.rstrip(' \n')
                        #     list1.append(line)
                        list1 = [line.rstrip(' \n') for line in lines]
                        total_mse = []

                        with open(psnr_log_csv_name,'a') as csvfile:
                            csv_writer=csv.writer(csvfile,dialect='excel')
                            index = list1[0]
                            lis = index.split(' ')
                            index2 = [i.split(':')[0] for i in lis]
                            csv_writer.writerow(index2)
                        for i in list1:
                            with open(psnr_log_csv_name,'a') as csvfile:
                                csv_writer=csv.writer(csvfile,dialect='excel')
                                data = i.split(' ')
                                data = [j.split(':')[1] for j in data]
                                y_mse_data = data[2]
                                total_mse.append(float(y_mse_data))
                                csv_writer.writerow(data)
                        average_mse = np.sum(total_mse) / len(total_mse)
                        y_psnr = get_psnr(average_mse)
                        video_path = path + '/' + video

                        # get yuv and compare vmaf
                        vmaf_env = '/home/zhaojie/zhaojie/vmaf_tool/vmaf-1.3.9'
                        vmaf_cmd = './run_vmaf yuv420p  {} {} ../{} {} --out-fmt json'.format(video_width, video_height , source_yuv, out_yuv)
                        print(vmaf_cmd)
                        vmaf_info = os.popen(vmaf_cmd).read()
                        # print(vmaf_info)
                        j = json.loads(vmaf_info)
                        VMAF_score = j['aggregate']['VMAF_score']
                        print('VMAF_score: {}'.format(VMAF_score))
                        vmaf_log_csv_name = "vmaf_" + source_yuv.split('.')[0] +'-'+ video.split('.')[0] + '.csv'
                        if os.path.exists(vmaf_log_csv_name):
                            os.remove(vmaf_log_csv_name)

                        with open(vmaf_log_csv_name, 'ab') as out_fps:
                            lists = j['frames']
                            csv_write2 = csv.writer(out_fps,delimiter=',')
                            csv_write2.writerow(['frameNum','VMAF_score'])
                            for i in lists:
                                frameNum = i['frameNum']
                                VMAF_score = i['VMAF_score']
                                fps_info = [frameNum, VMAF_score]
                                csv_write2 = csv.writer(out_fps,delimiter=',')
                                csv_write2.writerow(fps_info)
                        psnr_vmaf_data_tmp = [source_yuv, video_path, y_psnr, VMAF_score]
                        psnr_vmaf_data.append(psnr_data_tmp)
                    os.remove('psnr.log')
                    os.chdir('../')
            with open('average_psnr_vmaf.csv','a') as csvfile:
                csv_writer=csv.writer(csvfile,dialect='excel')
                csv_writer.writerow(["video1","video2","PSNR_YYUV", 'VMAF_score'])
                for i in psnr_vmaf_data:
                    csv_writer.writerow(i)
        os.chdir('../')
time.sleep(2)
# get html at the same time
# run('python web_html.py -f {}'.format(source_format))
