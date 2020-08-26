import sys
import logging

def setup_logger(log_file):
    log_format = '%(asctime)s - [%(process)d|%(thread)d] - %(levelname)s - %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)

    logging.root.handlers = [stream_handler,file_handler]
    logging.root.setLevel("INFO")