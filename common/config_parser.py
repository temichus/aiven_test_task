import yaml
import logging
from common.helpers.config_helpers import get_config_attr

logger = logging.getLogger(__name__)

class Config():
    def __init__(self, configs_path):
        self.config = dict()
        if type(configs_path) is not list:
            configs_path = [configs_path]
        for config in configs_path:
            with open(config, 'r') as f:
                self.config.update(yaml.full_load(f))

    def get_config_attr(self, *args, default=None, do_copy=True):
        return get_config_attr(self.config, *args, default=default, do_copy=do_copy)

