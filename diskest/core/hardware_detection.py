"""
Hardware detection module for Diskest
"""

import os
import logging
import psutil
import subprocess
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class HardwareDetector:
    """Detects storage devices and RAID configurations."""

    def detect(self) -> Dict[str, Any]:
        """
        Perform hardware detection.

        Returns:
            Dict[str, Any]: Detected hardware information.
        """
        return {
            "storage_devices": self._detect_storage_devices(),
            "raid": self._detect_raid(),
            "cpu_info": self._get_cpu_info(),
            "memory_info": self._get_memory_info(),
        }

    def _detect_storage_devices(self) -> Dict[str, Dict[str, Any]]:
        """Detect and collect information about storage devices."""
        devices = {}
        for partition in psutil.disk_partitions(all=True):
            if partition.device not in devices:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    device_name = partition.device.split("/")[-1]
                    devices[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": getattr(partition, 'fstype', 'unknown'),
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                        "is_ssd": self._is_ssd(device_name),
                        "model": self._get_device_model(device_name),
                        "serial": self._get_device_serial(device_name),
                    }
                except PermissionError:
                    logger.warning(
                        f"Permission denied when accessing {partition.device}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error detecting storage device {partition.device}: {str(e)}"
                    )
        return devices

    def _is_ssd(self, device: str) -> bool:
        """
        Check if a device is an SSD.

        Args:
            device (str): The device name (e.g., 'sda', 'nvme0n1')

        Returns:
            bool: True if the device is likely an SSD, False otherwise
        """
        # Strip '/dev/' prefix if present
        device = device.split("/")[-1]

        # Check if it's a block device
        if not os.path.exists(f"/sys/block/{device}"):
            logger.debug(f"{device} is not a block device, skipping SSD check")
            return False

        # Method 1: Check rotational flag in sysfs
        rotational_path = f"/sys/block/{device}/queue/rotational"
        if os.path.exists(rotational_path):
            try:
                with open(rotational_path, "r") as f:
                    return f.read().strip() == "0"
            except IOError:
                logger.warning(f"Unable to read rotational status for {device}")

        # Method 2: Use lsblk command
        try:
            output = (
                subprocess.check_output(["lsblk", "-ndo", "ROTA", f"/dev/{device}"])
                .decode()
                .strip()
            )
            if output == "0":
                return True
        except subprocess.CalledProcessError:
            logger.warning(f"Unable to determine if {device} is an SSD using lsblk")

        # Method 3: Check for NVMe devices
        if device.startswith("nvme"):
            return True

        # Method 4: Check device model for SSD indicators
        model = self._get_device_model(device)
        if model and ("ssd" in model.lower() or "solid state" in model.lower()):
            return True

        logger.debug(f"Could not definitively determine if {device} is an SSD")
        return False

    def _get_device_model(self, device: str) -> str:
        """Get the model of the device."""
        model_path = f"/sys/block/{device}/device/model"
        if os.path.exists(model_path):
            try:
                with open(model_path, "r") as f:
                    return f.read().strip()
            except IOError:
                logger.warning(f"Unable to read model information for {device}")
        return ""

    def _get_device_serial(self, device: str) -> str:
        """Get the serial number of the device."""
        serial_path = f"/sys/block/{device}/device/serial"
        if os.path.exists(serial_path):
            try:
                with open(serial_path, "r") as f:
                    return f.read().strip()
            except IOError:
                logger.warning(f"Unable to read serial information for {device}")
        return ""

    def _detect_raid(self) -> Dict[str, Any]:
        """Detect RAID configuration."""
        raid_info = {"detected": False, "type": None, "details": None}

        # Check for software RAID
        if os.path.exists("/proc/mdstat"):
            try:
                with open("/proc/mdstat", "r") as f:
                    mdstat_content = f.read()
                if "active raid" in mdstat_content.lower():
                    raid_info["detected"] = True
                    raid_info["type"] = "software"
                    raid_info["details"] = self._parse_mdstat(mdstat_content)
            except Exception as e:
                logger.error(f"Error reading /proc/mdstat: {str(e)}")

        # Check for hardware RAID
        if not raid_info["detected"]:
            try:
                lspci_output = subprocess.check_output(
                    ["lspci"], universal_newlines=True
                )
                if "RAID" in lspci_output:
                    raid_info["detected"] = True
                    raid_info["type"] = "hardware"
                    raid_info["details"] = "Hardware RAID detected via lspci"
            except subprocess.CalledProcessError:
                logger.warning("Failed to execute lspci command")

        return raid_info

    def _parse_mdstat(self, mdstat_content: str) -> List[Dict[str, Any]]:
        """Parse the content of /proc/mdstat to extract RAID information."""
        raid_arrays = []
        for line in mdstat_content.splitlines():
            if line.startswith("md"):
                parts = line.split()
                raid_arrays.append(
                    {
                        "device": parts[0],
                        "status": parts[2],
                        "type": parts[3],
                        "devices": parts[4:],
                    }
                )
        return raid_arrays

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        cpu_info = {}
        try:
            cpu_info["physical_cores"] = psutil.cpu_count(logical=False)
            cpu_info["total_cores"] = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info["max_frequency"] = cpu_freq.max
                cpu_info["min_frequency"] = cpu_freq.min
                cpu_info["current_frequency"] = cpu_freq.current
        except Exception as e:
            logger.error(f"Error getting CPU information: {str(e)}")
        return cpu_info

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        memory_info = {}
        try:
            vm = psutil.virtual_memory()
            memory_info["total"] = vm.total
            memory_info["available"] = vm.available
            memory_info["used"] = vm.used
            memory_info["percent"] = vm.percent
        except Exception as e:
            logger.error(f"Error getting memory information: {str(e)}")
        return memory_info
