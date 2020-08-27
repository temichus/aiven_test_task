from argparse import ArgumentParser

"""Add arguments for main scripts dynamically"""


def add_producer_config(parser):
    parser.add_argument(
        "--producer_config", action="store", help="producer config file path (DEFAULT producer_config.yaml)",
        default="producer_config.yaml")


def add_consumer_config(parser):
    parser.add_argument(
        "--consumer_config", action="store", help="consumer config file path (DEFAULT consumer_config.yaml)",
        default="consumer_config.yaml")


def add_kafka_config(parser):
    parser.add_argument(
        "--kafka_config", action="store", help="kafka config filr path (DEFAULT kafka_config.yaml)",
        default="kafka_config.yaml")


def pars_logging_args(parser):
    parser.add_argument(
        "--log_file", action="store", help="log file path (DEFAULT log.txt)", default="log.txt")
    parser.add_argument(
        "--log_level", action="store", help="Log level (DEFAULT INFO)", default="INFO")


ARGUMENTS = {
    "producer": add_producer_config,
    "consumer": add_consumer_config,
    "kafka": add_kafka_config,
    "logging": pars_logging_args,

}


def get_parser(*args):
    parser = ArgumentParser()
    for arg in args:
        ARGUMENTS[arg](parser)
    return parser.parse_args()
