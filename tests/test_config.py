import os
import tempfile
from diskest.utils.config import load_config, deep_merge, get_config_path, save_config


def test_load_config(sample_config):
    """Test loading configuration."""
    config = load_config()
    assert all(key in config for key in ["global", "fio", "sysbench"])


def test_deep_merge():
    """Test deep merging of dictionaries."""
    dict1 = {"a": 1, "b": {"c": 2}}
    dict2 = {"b": {"d": 3}, "e": 4}
    result = deep_merge(dict1, dict2)
    assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}


def test_get_config_path():
    """Test retrieving the configuration file path."""
    path = get_config_path()
    assert str(path).endswith(".diskest/config.yaml")


def test_save_config():
    """Test saving and loading a configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        test_config = {"test": {"key": "value"}}
        save_config(test_config, config_path)
        loaded_config = load_config(config_path)
        assert "test" in loaded_config
        assert loaded_config["test"]["key"] == "value"
        assert "global" in loaded_config
        assert "fio" in loaded_config
        assert "sysbench" in loaded_config
