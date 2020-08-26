from consumer_main import main as consumer_main
from producer_main import main as producer_main
from common.setup_logger import setup_logger
import asyncio

async def main(loop):
    await asyncio.gather(
        consumer_main(loop),
        producer_main(loop),
    )


if __name__ == '__main__':
    setup_logger('common.log')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
    except KeyboardInterrupt:
        print('interrupted!')