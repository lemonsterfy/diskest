import pytest
from collections import namedtuple
from diskest.core.hardware_detection import HardwareDetector


@pytest.fixture
def hardware_detector():
    return HardwareDetector()


@pytest.fixture
def mock_disk_usage():
    sdiskusage = namedtuple("sdiskusage", ["total", "used", "free", "percent"])
    return sdiskusage(
        total=100000000000, used=50000000000, free=50000000000, percent=50.0
    )


def test_detect_storage_devices(hardware_detector, mock_disk_usage):
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
        mp.setattr(
            "diskest.core.hardware_detection.HardwareDetector._is_ssd",
            lambda self, device: True,
        )
        mp.setattr(
            "diskest.core.hardware_detection.HardwareDetector._get_device_model",
            lambda self, device: "Test Model",
        )
        mp.setattr(
            "diskest.core.hardware_detection.HardwareDetector._get_device_serial",
            lambda self, device: "Test Serial",
        )

        devices = hardware_detector._detect_storage_devices()
        assert "/dev/sda1" in devices
        device_info = devices["/dev/sda1"]
        assert device_info["mountpoint"] == "/"
        assert device_info["fstype"] == "ext4"
        assert device_info["total"] == 100000000000
        assert device_info["used"] == 50000000000
        assert device_info["free"] == 50000000000
        assert device_info["percent"] == 50.0
        assert device_info["is_ssd"]
        assert device_info["model"] == "Test Model"
        assert device_info["serial"] == "Test Serial"


def test_detect_raid(hardware_detector, mock_hardware_detector):
    raid_info = hardware_detector._detect_raid()
    assert not raid_info["detected"]
    assert raid_info["type"] is None
