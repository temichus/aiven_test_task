import logging
import pytest
import kafka
from common.config_parser import Config
from producer.kafka_metrics_porducer import MetricsProducer

logger = logging.getLogger(__name__)


async def return_async_value():
    pass


@pytest.fixture(scope="function")
def config():
    conf = Config([])
    conf.config["kafka_config"] = {}
    return conf


# ------------POSITIVE-------------
@pytest.mark.asyncio
async def test_successful_message_send(mocker, event_loop, config):
    mocker.patch('common.kafka_ssl_context_helper.create_ssl_context')
    config.config["kafka_config"] = {"bootstrap_servers": 'test', "topic": 'test',
                                     "ssl_context": {"cafile": 0, "certfile": 0, "keyfile": 0}}
    producer = MetricsProducer(config, event_loop)

    mock_start = mocker.Mock(return_value=return_async_value())
    producer.producer.start = mock_start
    mock_stop = mocker.Mock(return_value=return_async_value())
    producer.producer.stop = mock_stop
    mock_send = mocker.Mock(return_value=return_async_value())
    producer.producer.send_and_wait = mock_send
    async with producer:
        await producer.send("test_data")

    for mock in [mock_start, mock_stop, mock_send]:
        mock.assert_called_once()

    assert ('test', b'"test_data"') == mock_send.call_args_list[0][0]


# ------------NEGATIVE-------------
@pytest.mark.asyncio
async def test_not_started_producer(event_loop, config):
    config.config["kafka_config"] = {"bootstrap_servers": 'test', "topic": 'test'}
    producer = MetricsProducer(config, event_loop)
    with pytest.raises(AssertionError, match="producer is not started"):
        await producer.send(["test_data"])


@pytest.mark.asyncio
async def test_kafka_unavailable(event_loop, config):
    config.config["kafka_config"] = {"bootstrap_servers": 'not_exist', "topic": 'test'}
    producer = MetricsProducer(config, event_loop)
    with pytest.raises(kafka.errors.KafkaConnectionError, match=r".*Unable to bootstrap from.*"):
        await producer.__aenter__()
