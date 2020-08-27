"""
This is script to start messages consumer/db writer in independent process
"""

import asyncio
import logging
from argparse import ArgumentParser
from functools import partial
from consumer.pg_db_adapter import DbWebsiteMetricsWriter
from consumer.kafka_metrics_consumer import MetricsConsumer
from common.config_parser import Config
from common.setup_logger import setup_logger
from common.arguments_parsing import get_parser

logger = logging.getLogger(__name__)


async def consume(db_writer, data):
    """
    Coroutine callback for received message in Kafka consumer wrapper
    """
    logger.info("consumed: {}".format(data))
    await db_writer.log_signal_data(**data)


async def main(loop, args):
    """
    main method
    :param loop: event loop
    """
    config_obj = Config([args.consumer_config, args.kafka_config])
    db_writer = DbWebsiteMetricsWriter(config_obj)
    consumer = MetricsConsumer(config_obj, loop, partial(consume, db_writer))
    async with db_writer:
        async with consumer:
            await consumer.consume()


if __name__ == '__main__':
    args = get_parser("consumer", "kafka", "logging")
    setup_logger(args.log_file, args.log_level)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop, args))
    except KeyboardInterrupt:
        logger.info('interrupted!')
