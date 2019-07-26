# install pytest 4.0.2
# uninstall pytest 4.6.2
import pytest
import re
import paramiko
import time

optx = -1
cmdline = ""

# info = {
#     "-preset":'medium,fast,veryfast', \
#     "-rc-lookahead": '40,20', \
#     "-bf": '0,3', \
#     "-b:v": '2000k' \
#     }

# 自己单元测试得出结果 不同option递归 外部输入source outres

node_ip = '172.16.231.18'
ssh_port = 22
ssh_name = 'root'
ssh_password = "admin123"

info = {
    "-preset":'medium', \
    "-rc-lookahead": '40', \
    "-bf": '3', \
    "-b:v": '2000k' \
    }

def option_mark(options):
    dict_mark = options.split(' ')
    dict_mark_info = {}
    for index, value in enumerate(dict_mark):
        if value.startswith('-'):
            dict_mark_info[value] = dict_mark[index+1]
    return dict_mark_info

def get_connect(ssh_server):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_server, port=ssh_port, username=ssh_name, password=ssh_password)
    return client

def exec_cmdline(ssh_server ,cmdline):
    client = get_connect(ssh_server)    
    print('\nThe command to be executed is: \n' + cmdline)
    stdin, stdout, stderr = client.exec_command(str('{}'.format(cmdline)))
    # print('\n******* exec cmdline...\n')
    info_list = [line.strip('\n') for line in stdout]
    for line in stdout:
        pass
    client.close()
    return info_list
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

def option_cmdline():
    global optx
    optx += 1 
    global cmdline
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
        jas = option_cmdline()
        if jas == 1:
            cmdline_list.append(cmdline.lstrip(' '))
        cmdline = cmdline[0:len(cmdline)-tmp_len-2-len(key_data)]    
        tmp_idx += 1
    tmp_len = len(options) - 1
    optx -= 1
    return 0

options = []
AL = {}
for option ,value in info.items():
    if value.find(' '):
        value = value.replace(' ','')
    AL[option] = value
    op_value = value + ',NULL'
    op_value = op_value.split(',')
    if option != 'frames':
        options.append({option:op_value})
options.append({'END':'NULL'})
# print(options)

cmdline_list = []
leng = len(options) - 1
option_cmdline()
# print(cmdline_list)

print("**************")

stuple_list = []
for index, value in enumerate(cmdline_list):
    write_index = index + 1
    write_stuple = (write_index, value)
    stuple_list.append(write_stuple)

@pytest.mark.parametrize("index, value", stuple_list)
def test_transcode(index, value, source, outres):
    basic_cmd = "cd /tmp/;ffmpeg -y -c:v v205h264 -i /tmp/{}  -c:v v205h264 -an -preset veryfast -bf 3  -vsync 0 -rc-lookahead 40 -b:v 8000k -r 30 -g 90 -ratetol 1 -s {} /tmp/output1.mp4".format(source, outres)
    value_dicts = option_mark(value)
    basic_cmd_list = [i for i in basic_cmd.split(' ') if i != ' ']
    for dict_key, dict_value in value_dicts.items():
        for list_index, list_value in enumerate(basic_cmd_list):
            if dict_key == '-bf' and dict_value == '0' and dict_key == list_value: 
                basic_cmd_list[list_index+1] = str(dict_value) + ' -b-adapt 0'
            elif dict_key == list_value: 
                basic_cmd_list[list_index+1] = dict_value
    transcode_cmd = ' '.join(basic_cmd_list)
    print(transcode_cmd)
    for task_num in range(1,10):
        cmd_use = transcode_cmd[0:transcode_cmd.rindex(' ')] + ' /tmp/out{}.mp4 2>&1 | tee thread{}.log &'.format(str(task_num), str(task_num))
        transcode = exec_cmdline(node_ip, cmd_use)
        time.sleep(3)
        check_num = exec_cmdline(node_ip, 'ps aux | grep ffmpeg | grep -v grep | wc -l')
        check_num = check_num[0]
        print("task_num: {}".format(task_num))
        print("check_num: {}".format(check_num))
        if task_num != int(check_num):
            print("waring: task_num != check_num")
            print("task_num: {}".format(task_num))
            print("check_num: {}".format(check_num))
            err_info = exec_cmdline(node_ip ,"tail -n 4 /tmp/thread{}.log".format(str(task_num)))
            print("error message:")
            for i in err_info:
                print(i)
            break
        # exit(-1)
    print("**********")
    # task_clear = exec_cmdline(node_ip, 'killall -9 ffmpeg')

    task_clear = exec_cmdline(node_ip, 'killall -15 ffmpeg')
    # while True:
    time.sleep(5)
    task_clear = exec_cmdline(node_ip, 'ps aux | grep ffmpeg | grep -v grep | wc -l')
    if int(task_clear[0]) > 0:
        task_clear = exec_cmdline(node_ip, 'killall -2 ffmpeg')
        time.sleep(5)
        task_clear = exec_cmdline(node_ip, 'ps aux | grep ffmpeg | grep -v grep | wc -l')
        if int(task_clear[0]) > 0:
            task_clear = exec_cmdline(node_ip, 'killall -9 ffmpeg')
            print("warning: task killall -9")
    time.sleep(10)
