import asyncio
from argparse import ArgumentParser
from common.config_parser import Config
from producer.website_checker import WebsiteChecker
from producer.kafka_metrics_porducer import MetricsProducer
from common.setup_logger import setup_logger



def pars_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--producer_config", action="store", help="producer config file path", default="producer_config.yaml")
    parser.add_argument(
        "--kafka_config", action="store", help="kafka config filr path", default="kafka_config.yaml")
    return parser.parse_args()


async def main(loop):
    args = pars_args()
    config_obj = Config([args.producer_config, args.kafka_config])
    producer = MetricsProducer(config_obj, loop)
    checker = WebsiteChecker(config_obj, loop, producer.send)
    async with producer:
        await checker.run_forever()


if __name__ == '__main__':
    setup_logger('producer.log')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
    except KeyboardInterrupt:
        print('interrupted!')
