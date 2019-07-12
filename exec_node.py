import telnetlib
import time


def telnetip(tn, flag ,str_word):
    data = tn.read_until(flag.encode())
    print(data)
    print(data.decode(errors='ignore'))
    tn.write(str_word.encode() + b"\n")
    return data

ips = '172.16.204.7'
cmds_list = [   "mkdir /a",
                "mount -o nolock 172.16.132.7:/export/test_video /a",
                "cp /a/customer_aliyun/axstream-1.1.1-201907041823-md5-2a22c18f9973fce2d\
                9abb9d07a386dcd_multiOutputsScale_1.\
                pkg /D0/APP",
                "cd /D0/APP",
                "pkg-probe.sh axstream axstream-1.1.1-201907041823-md5-2a22c18f9973fce2d\
                9abb9d07a386dcd_multiOutputsScale_1.\
                pkg",
                "extend_rootfs_create_link.sh"
            ]
    
username = 'root'
password = 'root'
try:
    tn = telnetlib.Telnet(ips, port=23, timeout=50)
    telnetip(tn, "login:", username)
    telnetip(tn, "Password:", password)
    time.sleep(3)


    # for i in cmds_list:
    #     telnetip(tn, "#", i)
    #     time.sleep(1)
    # telnetip(tn, "#", "sh /D0/APP/zhaojie.sh")
    telnetip(tn, "#", "ssh zhaojie@172.16.132.234")
    # telnetip(tn, "#", "scp aupera-video@172.16.132.7:/home/aupera-video/work/xilinx/a\
    # pp/alicloud_tracker_pro/test6/yolo_al\
    # i416 /tmp")
    # telnetip(tn, "password", "xuejin000")
    # telnetip(tn, "#", "scp aupera-video@172.16.132.7:/home/aupera-video/work/xilinx/a\
    # pp/libaupvpacc/libaupvpacc.so  /us\
    # r/lib")

    for i in range(2):
        # if telnetip(tn, "connecting?", "y"):
        #     telnetip(tn, "password", "xue(yes/no)?jin000")
        # else:
        telnetip(tn, "(y/n)", "y")
        telnetip(tn, "password", "123456")

    # if telnetip(tn, "(yes/no)?", "y"):
    # telnetip(tn, "password", "xuejin000")
    telnetip(tn, "#", "exit")
    time.sleep(0.5)
    tn.close()
    time.sleep(0.5)
except Exception as err:
    print(err)