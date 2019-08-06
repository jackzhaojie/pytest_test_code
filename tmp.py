import os
import subprocess
import psutil
import time


class TimeoutError(Exception): 
    pass 
   
def command(cmd, timeout=15): 
    """执行命令cmd，返回命令输出的内容。
    如果超时将会抛出TimeoutError异常。
    cmd - 要执行的命令
    timeout - 最长等待时间，单位：秒
    """ 
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True) 
    t_beginning = time.time() 
    seconds_passed = 0 
    while True: 
        if p.poll() is not None: 
            break 
        seconds_passed = time.time() - t_beginning 
        if timeout and seconds_passed > timeout: 
            p.terminate() 
            raise TimeoutError(cmd, timeout) 
        time.sleep(0.1) 
    return p.stdout.read() 

out_stream = 'rtmp://172.16.15.31:1935/live/1111'
cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} | grep video | wc -l'.format(out_stream)

try:
    check_code_status = command(cmdline)
    if check_code_status != '':
        print("exix")
except Exception as err:
    print(err)
    print("no exix")