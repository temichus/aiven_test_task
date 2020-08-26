import asyncio
from argparse import ArgumentParser
from functools import partial
from consumer.pg_db_adapter import DbWebsiteMetricsWriter
from consumer.kafka_metrics_consumer import MetricsConsumer
from common.config_parser import Config
from common.setup_logger import setup_logger

async def consume(db_writer, data):
    print("consumed: ", data)
    await db_writer.log_signal_data(**data)


def pars_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--consumer_config", action="store", help="consumer config file path", default="consumer_config.yaml")
    parser.add_argument(
        "--kafka_config", action="store", help="kafka config filr path", default="kafka_config.yaml")
    return parser.parse_args()


async def main(loop):
    args = pars_args()
    config_obj = Config([args.consumer_config, args.kafka_config])
    db_writer = DbWebsiteMetricsWriter(config_obj)
    consumer = MetricsConsumer(config_obj, loop, partial(consume, db_writer))
    async with db_writer:
        async with consumer:
            await consumer.consume()


if __name__ == '__main__':
    setup_logger('consumer.log')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
    except KeyboardInterrupt:
        print('interrupted!')
