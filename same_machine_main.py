"""
This is script to start everything in one process
"""
import asyncio
import logging
from consumer_main import main as consumer_main
from producer_main import main as producer_main
from common.setup_logger import setup_logger
from common.arguments_parsing import get_parser

logger = logging.getLogger(__name__)


async def main(loop, args):
    """
      main method
      :param loop: event loop
      """
    await asyncio.gather(
        consumer_main(loop, args),
        producer_main(loop, args),
    )


if __name__ == '__main__':
    args = get_parser("producer", "consumer", "kafka", "logging")
    setup_logger(args.log_file, args.log_level)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop, args))
    except KeyboardInterrupt:
        logger.info('interrupted!')
