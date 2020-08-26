import pytest
import logging
import asyncio
from producer.website_checker import WebsiteChecker
from common.config_parser import Config

logger = logging.getLogger(__name__)


async def return_async_value():
    pass


def porduser_stub(mocker, num_calls=2):
    stub = mocker.stub(name='kafka_porduser_stub')
    stub.side_effect = [return_async_value() for i in range(num_calls)]
    return stub


async def run_checker_once(checker):
    tasks = await checker.run()
    while [task for task in tasks if task.done() is not True]:
        logger.info([task for task in tasks if task.done() is not True])
        await asyncio.sleep(1)


@pytest.fixture(scope="function")
def config():
    conf = Config([])
    conf.config["delay_between_checks"] = 1
    conf.config["websites_to_check"] = []
    return conf


# ------------POSITIVE-------------
config_dict = [
    {"url": "http://tut.by"},
    {"url": "http://onliner.by", "regex": "Google"},
    {"url": "http://dev.by", "regex": "Gogle"}
]

expected_regex_result = {
    "http://tut.by": None,
    "http://onliner.by": True,
    "http://dev.by": False
}


@pytest.mark.asyncio
async def test_website_available(mocker, event_loop, config):
    kafka_porduser_stub = porduser_stub(mocker, 3)
    config.config["websites_to_check"] = config_dict
    checker = WebsiteChecker(config, event_loop, kafka_porduser_stub)
    await run_checker_once(checker)

    assert kafka_porduser_stub.call_count == 3
    args_calls = [call[0][0] for call in kafka_porduser_stub.call_args_list]
    for call in args_calls:
        assert call["status_code"] == 200
        assert call["regex_found"] == expected_regex_result[call["url"]]


# ------------NEGATIVE-------------
@pytest.mark.asyncio
async def test_website_unavailable(mocker, event_loop, config):
    kafka_porduser_stub = porduser_stub(mocker, 1)
    config.config["websites_to_check"] = [{"url": "http://tut.byy"}, ]
    checker = WebsiteChecker(config, event_loop, kafka_porduser_stub)
    await run_checker_once(checker)

    kafka_porduser_stub.assert_called_once()
    expected_call = {'url': 'http://tut.byy', 'response_time': None, 'status_code': None, 'regex': None,
                     'regex_found': None}
    for key, value in expected_call.items():
        assert value == kafka_porduser_stub.call_args_list[0][0][0][key]
