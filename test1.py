# import pytest

# @pytest.fixture(scope='function')
# def setup_function(request):
#     def teardown_function():
#         print("teardown_function called.")
#     request.addfinalizer(teardown_function)  # 此内嵌函数做teardown工作
#     print("setup_function called")
    

# @pytest.fixture(scope='module')
# def setup_module(request):
#     def teardown_module():
#         print("teardown_module called.")
#     request.addfinalizer(teardown_module)
#     print("setup_module called.")

# @pytest.mark.website
# def test_1(setup_function):
#     print("test1 called.")

# def test_2(setup_module):
#     print("test2 called.")

# def test_3(setup_module):
#     print("test3 called.")
#     assert 2==1+1 # 通过assert断言确认测试结果是否符合预期


# import pytest


# # @pytest.mark.skipif(not pytest.config.getoption("--runslow"))
# # def test_func_slow_1():
# #     """当在命令行执行 --runslow 参数时才执行该测试"""
# #     print ('skip slow')

# def test_get(outres):
#     print('')
#     print(outres)

# def test_get_mp4(source):
#     print('')
#     print(source)

# import platform

# print(platform.system())


import subprocess
import os


def check_rtmp(rtmp):
    cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} | grep video > /dev/null '.format(rtmp)
    # cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} | grep video | wc -l'.format(rtmp)
    # cmdline = 'ffprobe -v quiet -print_format json -show_format -show_streams -i {} '.format(rtmp)
    retcode = subprocess.call(cmdline, shell=True, timeout=15)
    # 视频流exists = 0, no exists = timeout for this ffprobe
    # 文件  exists = 0. no exists = 1
    return retcode


a = check_rtmp("rtmp://172.16.15.31:1935/live/bbb-lived")
print(a)


# b = check_rtmp("004-bbb-1080p-h264_5000frames.264")
# print(b)