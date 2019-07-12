import pytest
import paramiko
import time


node_ip = '172.16.231.17'
ssh_port = 22
ssh_name = 'root'
ssh_password = "admin123"

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
        pass
    client.close()
    return info_list

@pytest.fixture(scope="module")
def resource_a_setup(request):
    print("\nresource_a_setup()")
    def resource_a_teardown():
        print("\nresource_a_teardown()")
    request.addfinalizer(resource_a_teardown)

def test_1_node_performance(resource_a_setup):
    print("test_1_node_performance()")
    # input_stream = 'rtmp://192.168.32.100:1935/live/node_test'
    # for stream_index in range(8):
    #     out_stream = input_stream + '_' +  node_ip.split('.')[-1] + '_' + str(stream_index)
    #     transcode_cmd = "nohup ffmpeg -c:v v205h264 -i {} -c:v v205h264 -b:v 2000k -c:a copy -analyzeduration 50000000 -r 30 -outw 1920 -outh 1080 -max_muxing_queue_size 512 -f flv {} >/dev/null 2>/dev/null &".format(input_stream, out_stream)
    #     cc = exec_cmdline(node_ip ,transcode_cmd)
    # print("info: node {} running task finish".format(node_ip))    
    # check_num = exec_cmdline(node_ip ,'ps aux | grep ffmpeg | grep -v grep | wc -l')
    # assert check_num == 8

def test_2_that_do_not():
    print("test_2_that_do_not()")

def test_3_that_do(resource_a_setup):
    print("test_3_that_do()")




    