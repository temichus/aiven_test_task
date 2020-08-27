"""
This is script to start websites_checker/messages producer in independent process
"""

import asyncio
import logging
from common.config_parser import Config
from producer.website_checker import WebsitesChecker
from producer.kafka_metrics_porducer import MetricsProducer
from common.setup_logger import setup_logger
from common.arguments_parsing import get_parser

logger = logging.getLogger(__name__)

async def main(loop, args):
    """
      main method
      :param loop: event loop
      """
    config_obj = Config([args.producer_config, args.kafka_config])
    producer = MetricsProducer(config_obj, loop)
    checker = WebsitesChecker(config_obj, loop, producer.send)
    async with producer:
        await checker.run_forever()


if __name__ == '__main__':
    args = get_parser("producer", "kafka", "logging")
    setup_logger(args.log_file, args.log_level)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop,args))
    except KeyboardInterrupt:
        logger.info('interrupted!')
