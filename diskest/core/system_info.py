"""
System information collection module for Diskest
"""

import platform
import psutil
import distro
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SystemInfo:
    """Collects various system information."""

    def collect(self) -> Dict[str, Any]:
        """
        Collect system information.

        Returns:
            Dict[str, Any]: Dictionary containing collected system information.
        """
        return {
            "os": self._get_os_info(),
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "network": self._get_network_info(),
        }

    def _get_os_info(self) -> Dict[str, str]:
        """Collect operating system information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "distro": distro.name(pretty=True),
            "architecture": platform.machine(),
        }

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Collect CPU information."""
        cpu_freq = psutil.cpu_freq()
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": cpu_freq.max if cpu_freq else None,
            "current_frequency": cpu_freq.current if cpu_freq else None,
            "usage_percent": psutil.cpu_percent(interval=1),
        }

    def _get_memory_info(self) -> Dict[str, Any]:
        """Collect memory information."""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent,
        }

    def _get_disk_info(self) -> Dict[str, Dict[str, Any]]:
        """Collect disk information."""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            except PermissionError:
                logger.warning(f"Permission denied when accessing {partition.device}")
        return disk_info

    def _get_network_info(self) -> Dict[str, Dict[str, Any]]:
        """Collect network information."""
        network_info = {}
        for interface, addrs in psutil.net_if_addrs().items():
            network_info[interface] = {
                "addresses": [
                    {"family": addr.family.name, "address": addr.address}
                    for addr in addrs
                ]
            }
        return network_info
