import pytest

def pytest_addoption(parser):
    parser.addoption("--outres", action="store", default="type1",help="my option: type1 or type2")
    parser.addoption("--source", action="store", default="type1",help="my option: type1 or type2")

@pytest.fixture
def outres(request):
    return request.config.getoption("--outres")

@pytest.fixture
def source(request):
    return request.config.getoption("--source")

