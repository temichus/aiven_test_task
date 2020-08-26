import pytest
import logging
import os

logger = logging.getLogger(__name__)

def pytest_configure(config):
    log_file = config.getini("log_file")
    dir_name = os.path.dirname(log_file)
    os.makedirs(dir_name, exist_ok=True)



