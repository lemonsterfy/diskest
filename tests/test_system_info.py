import pytest
from diskest.core.system_info import SystemInfo
from collections import namedtuple


@pytest.fixture
def system_info():
    return SystemInfo()


@pytest.fixture
def mock_disk_usage():
    disk_usage = namedtuple("sdiskusage", ["total", "used", "free", "percent"])
    return disk_usage(
        total=100000000000, used=50000000000, free=50000000000, percent=50.0
    )


def test_get_os_info(system_info, mock_debian_system):
    os_info = system_info._get_os_info()
    assert os_info["system"] == "Linux"
    assert os_info["release"] == "6.1.0-18-amd64"
    assert os_info["distro"] == "Debian GNU/Linux 12 (bookworm)"


def test_get_cpu_info(system_info, mock_cpu_info):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "psutil.cpu_count",
            lambda logical=True: (
                mock_cpu_info.total if logical else mock_cpu_info.physical
            ),
        )
        mp.setattr("psutil.cpu_freq", lambda: mock_cpu_info)

        cpu_info = system_info._get_cpu_info()
        assert cpu_info["physical_cores"] == 4
        assert cpu_info["total_cores"] == 8
        assert cpu_info["max_frequency"] == 3.5
        assert cpu_info["current_frequency"] == 2.8


def test_get_memory_info(system_info, mock_memory_info):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("psutil.virtual_memory", lambda: mock_memory_info)

        memory_info = system_info._get_memory_info()
        assert memory_info["total"] == 16000000000
        assert memory_info["available"] == 8000000000
        assert memory_info["used"] == 8000000000
        assert memory_info["percent"] == 50.0


def test_get_disk_info(system_info, mock_disk_usage):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "psutil.disk_partitions",
            lambda all=False: [
                type(
                    "obj",
                    (object,),
                    {"device": "/dev/sda1", "mountpoint": "/", "fstype": "ext4"},
                )
            ],
        )
        mp.setattr("psutil.disk_usage", lambda path: mock_disk_usage)

        disk_info = system_info._get_disk_info()
        assert "/dev/sda1" in disk_info
        assert disk_info["/dev/sda1"]["total"] == 100000000000
        assert disk_info["/dev/sda1"]["used"] == 50000000000
        assert disk_info["/dev/sda1"]["free"] == 50000000000
        assert disk_info["/dev/sda1"]["percent"] == 50.0
