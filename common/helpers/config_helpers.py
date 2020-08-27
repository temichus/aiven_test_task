import copy
import logging

logger = logging.getLogger(__name__)


def get_config_attr(config, *args, default=None, do_copy=True):
    """
    Looks for args in config. Returns default if no key or index found
    It can help to avoid try, except construction
    default value is returned if no such key of index is found
    Example, try to get value of config['misc']['tags']:
    config_attr(MAIN_CONFIG, [], 'misc', 'tags')
    If there is no 'misc' or 'tags' keys empty array is returned
    """
    if do_copy:
        resulting_value = copy.deepcopy(config)
    else:
        resulting_value = config
    for arg in args:
        try:
            resulting_value = resulting_value[arg]
        except (KeyError, IndexError) as e:
            logger.info(f'key error {e} ')
            return default
    return resulting_value
