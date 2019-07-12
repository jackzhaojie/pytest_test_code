import os
from scp import SCPClient
import paramiko
import getopt
import sys
import time
import subprocess
import pytest

# exec transcode stream
node_ip = "172.16.231.31"
ssh_port = '22'
ssh_name = 'root'
ssh_password = 'admin123'

def check_rtmp(rtmp):
    cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} | grep video > /dev/null '.format(rtmp)
    # cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} | grep video | wc -l'.format(rtmp)
    # cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} '.format(rtmp)
    retcode = subprocess.call(cmdline, shell=True, timeout=15)
    return retcode

def run(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def get_connect(ssh_server):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_server, port=ssh_port, username=ssh_name, password=ssh_password)
    return client

def exec_cmdline(ssh_server ,cmdline):
    client = get_connect(ssh_server)    
    # print('\nThe command to be executed is: \n' + cmdline)
    stdin, stdout, stderr = client.exec_command(str('{}'.format(cmdline)))
    # print('\n******* exec cmdline...\n')
    info_list = [line.strip('\n') for line in stdout]
    for line in stdout:
        # print(line.strip('\n'))    
        pass
    client.close()
    return info_list


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

# exec push stream
rtmp_input_stream = 'rtmp://172.16.132.234:1935/live/rtmp_live'
rtsp_input_stream = 'rtmp://172.16.132.234:1935/live/rtsp_live'
ffmpeg_get = run("ps aux | grep ffmpeg | wc -l")
if int(ffmpeg_get) > 2:
    pass
else:
    test_videos = [i for i in os.listdir(os.getcwd()) if i.endswith('mp4')]
    for push_stream_mp4 in test_videos:
        if push_stream_mp4 == '':
            rtmp_input_stream = rtmp_input_stream + '_1080'
            rtsp_input_stream = rtsp_input_stream + '_1080'
        elif push_stream_mp4 == '':
            rtmp_input_stream = rtsp_input_stream + '_720'
            rtsp_input_stream = rtsp_input_stream + '_720'
        push_rtmp_stream_cmd = "nohup ffmpeg -threads 2 -re -fflags +genpts -stream_loop -1 -i {} -c copy -f flv {} >/dev/null 2>/dev/null &".format(push_stream_mp4 ,rtmp_input_stream)
        push_rtsp_stream_cmd = "nohup ffmpeg -threads 2 -re -fflags +genpts -stream_loop -1 -i {} -c copy -f rtsp {} >/dev/null 2>/dev/null &".format(push_stream_mp4 ,rtsp_input_stream)
        run_cmd = run(push_rtmp_stream_cmd)
        run_cmd = run(push_rtsp_stream_cmd)
        time.sleep(2)


info_conf = {            
            "-o":"rtmp://172.16.132.234:1935/live/rtmp_live_1080_test,rtmp://172.16.132.234:1935/live/rtmp_live_720_test,rtmp://172.16.132.234:1935/live/rtsp_live_1080_test,rtmp://172.16.132.234:1935/live/rtsp_live_720_test",
            "-preset":"medium, veryfast",
            }

source_videos = ['rtmp://172.16.132.234:1935/live/rtmp_live_1080', 'rtsp://172.16.132.234:1935/live/rtsp_live_1080','rtmp://172.16.132.234:1935/live/rtmp_live_720', 'rtsp://172.16.132.234:1935/live/rtsp_live_720']
mixstream_stuple_list = []
cc = dict_recursive(info_conf)
for source_video in source_videos:    
    if source_video == 'rtmp://172.16.132.234:1935/live/rtmp_live_1080' or source_video == 'rtsp://172.16.132.234:1935/live/rtsp_live_1080':
        [mixstream_stuple_list.append((8,index[1],source_video,'1280x720',"3000k")) if index[1].find('720') != -1 and index[1].find('veryfast') != -1 \
        else mixstream_stuple_list.append((8,index[1],source_video,'1920x1080',"3000k")) if index[1].find('720') == -1 and index[1].find('veryfast')!= -1 \
        else mixstream_stuple_list.append((6,index[1],source_video,'1280x720',"3000k"))  if index[1].find('720') != -1 and index[1].find('medium')!= -1 \
        else mixstream_stuple_list.append((3,index[1],source_video,'1920x1080',"3000k")) if index[1].find('720') == -1 and index[1].find('medium')!= -1 else None for index in cc]
    elif source_video == 'rtmp://172.16.132.234:1935/live/rtmp_live_720' or source_video == 'rtsp://172.16.132.234:1935/live/rtsp_live_720':
        [mixstream_stuple_list.append((4,index[1],source_video,'1280x720',"3000k")) if index[1].find('720') != -1 and index[1].find("veryfast")!= -1 \
        else mixstream_stuple_list.append((3,index[1],source_video,'1280x720',"4000k")) if index[1].find('720') != -1 and index[1].find("medium")!= -1 else None for index in cc ]

for i in mixstream_stuple_list:
    print(i)
print(len(mixstream_stuple_list))

def option_mark(options):
    dict_mark = options.split(' ')
    dict_mark_info = {}
    for index, value in enumerate(dict_mark):
        if value.startswith('-'):
            dict_mark_info[value] = dict_mark[index+1]
    return dict_mark_info


# @pytest.mark.parametrize("index, value", "source", "outres", "bitrate", mixstream_stuple_list)
def test_mixstream(index, value, source, outres, bitrate):
    basic_cmd = "ffmpeg -y -c:v v205h264 -i {}  -c:v v205h264 -an -preset veryfast -bf 3  -rc-lookahead 40 -b:v {} -r 30 -g 90 -ratetol 1 -s {} -f flv rtmp://172.16.132.234:1935/live/test".format(source, bitrate,outres)
    value_dicts = option_mark(value)
    basic_cmd_list = [i for i in basic_cmd.split(' ') if i != ' ']
    # print(value_dicts)
    # print(basic_cmd_list)
    for dict_key, dict_value in value_dicts.items():
        for list_index, list_value in enumerate(basic_cmd_list):
            # if dict_key == '-o' and dict_key == list_value: 
            if dict_key == '-o': 
                basic_cmd_list[-1] = dict_value
            elif dict_key == list_value: 
                basic_cmd_list[list_index+1] = dict_value
    transcode_cmd = ' '.join(basic_cmd_list)
    print(transcode_cmd)
    print('')
    for task_num in range(1,index + 1):
        cmd_use = transcode_cmd + '_{} 2>&1 | tee thread{}.log &'.format(str(task_num), str(task_num))
        transcode = exec_cmdline(node_ip, cmd_use)
        time.sleep(1)
    
    output_streams = [transcode_cmd[basic_cmd.rindex(' '):] + '_{}'.format(i)  for i in range(1, index+1)] 
    while True:
        pass
        time.sleep(300) # 5min and ffprobe
        for out_stream in output_streams:
            try:
                check_code_status = check_rtmp(out_stream)
                if check_code_status == 0:
                    print("stream existx ")
                
            except Exception as error:
                print("info: stream {} timeout".format(out_stream))
                
            # print(error)
            # failed = failed + 1

        # ffprobe stream for 30min







for i in mixstream_stuple_list:
    # print(i)
    test_mixstream(i[0],i[1],i[2],i[3],i[4])
    # exit(-1)






# for i in cc:
#     print(i)
exit(-1)



print("wait 20s")
time.sleep(20)

stream_index = 8
out_stream = rtmp_input_stream + '_' +  node_ip.split('.')[-1] + '_' + str(stream_index)
transcode_cmd = "nohup ffmpeg -c:v v205h264 -i {} -c:v v205h264 -b:v 2000k -c:a copy -analyzeduration 50000000 -r 30 -outw 1920 -outh 1080 -max_muxing_queue_size 512 -f flv {} >/dev/null 2>/dev/null &".format(input_stream, out_stream)
# transcode_cmd = "cd /tmp/;nohup ffmpeg -c:v v205h264 -i {} -c:v v205h264 -b:v 7000k -c:a copy -analyzeduration 50000000 -r 30 -outw 1920 -outh 1080 -max_muxing_queue_size 512 -f flv {}  &".format(input_stream, out_stream)
# transcode_cmd = "nohup stream_mixer -i {} -c:v v205h264 -b:v 2000k -c:a copy  -r 30 -outw 1920 -outh 1080  -o {} -port 5188{} -in_plugin mp -out_plugin mp >/dev/null 2>/dev/null &".format(input_stream, out_stream, str(stream_index))
cc = exec_cmdline(node_ip ,transcode_cmd)
print("info: node {} running task finish".format(node_ip))    
    # cc = exec_cmdline(node_ip ,'ifconfig')
print("************\n")
# print("finish")



print("begin check")
# loop_stream = []
while True:
    for node_ip in ip_list:
        failed = 0
        reset_task = 0
        for stream_index in range(8):
            out_stream = input_stream + '_' +  node_ip.split('.')[-1] + '_' + str(stream_index)
            try:
                check_code_status =  check_rtmp(out_stream)
                # print(check_code_status)
                if check_code_status == 1:
                    # no video
                    ps_cmd = "ps aux | grep {} | grep -v grep | awk '{{print $1}}'".format(out_stream)
                    stream_pid = exec_cmdline(node_ip ,ps_cmd)
                    kill_cmd = 'kill -9 {}'.format(stream_pid[0])
                    kill  = exec_cmdline(node_ip ,kill_cmd)
                    transcode_cmd = "nohup ffmpeg -c:v v205h264 -i {} -c:v v205h264 -b:v 2000k -c:a copy -analyzeduration 50000000 -r 30 -outw 1920 -outh 1080 -max_muxing_queue_size 512 -f flv {} >/dev/null 2>/dev/null &".format(input_stream, out_stream)
                    # transcode_cmd = "nohup stream_mixer -i {} -c:v v205h264 -b:v 2000k -c:a copy  -r 30 -outw 1920 -outh 1080  -o {} -port 5188{} -in_plugin mp -out_plugin mp >/dev/null 2>/dev/null &".format(input_stream, out_stream, str(stream_index))
                    cc = exec_cmdline(node_ip ,transcode_cmd)
                    reset_task = reset_task + 1
                    print("info: resend task {}".format(out_stream))
                else:
                    pass
            except Exception as error:
                print("info: stream {} timeout".format(out_stream))
                # print(error)
                failed = failed + 1
            
                # loop_stream.append(out_stream)
            
        if failed > 4 and failed < 8:
            print("warning task_num {}".format(failed))
        elif failed == 8:
            print("error node {}".format(node_ip))
            break
        if reset_task == 0:
            print("info: node {} pass".format(node_ip))
        elif reset_task > 0:
            print("info: node {} reset task {}".format(node_ip, str(reset_task)))