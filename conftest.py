import pytest

def pytest_addoption(parser):
    parser.addoption("--outres", action="store", default="type1",help="output video res")
    parser.addoption("--source", action="store", default="type1",help="source video name")
    parser.addoption("--ip", action="store", default="type1",help="node ip to test")
    parser.addoption("--runflag", action="store", default="type1",help="choose ffmpeg or stream_mixer")

@pytest.fixture
def outres(request):
    return request.config.getoption("--outres")

@pytest.fixture
def source(request):
    return request.config.getoption("--source")

@pytest.fixture
def ip(request):
    return request.config.getoption("--ip")

@pytest.fixture
def runflag(request):
    return request.config.getoption("--runflag")
