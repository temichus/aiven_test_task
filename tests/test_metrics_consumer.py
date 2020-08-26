import logging
import pytest
import kafka
from types import SimpleNamespace
from common.config_parser import Config
from consumer.kafka_metrics_consumer import MetricsConsumer

logger = logging.getLogger(__name__)


async def return_async_value():
    pass


def consumer_stub(mocker, num_calls=2):
    stub = mocker.stub(name='kafka_consumer_stub')
    stub.side_effect = [return_async_value() for i in range(num_calls)]
    return stub


@pytest.fixture(scope="function")
def config():
    conf = Config([])
    conf.config["kafka_config"] = {}
    return conf


# ------------POSITIVE-------------
@pytest.mark.asyncio
async def test_successful_message_received(mocker, event_loop, config):
    mocker.patch('common.kafka_ssl_context_helper.create_ssl_context')
    kafka_consumer_stub = consumer_stub(mocker, 1)
    config.config["kafka_config"] = {"bootstrap_servers": 'test', "topic": 'test',
                                     "ssl_context": {"cafile": 0, "certfile": 0, "keyfile": 0}}
    consumer = MetricsConsumer(config, event_loop, kafka_consumer_stub)

    mock_start = mocker.Mock(return_value=return_async_value())
    consumer.kafka_consumer.start = mock_start
    mock_stop = mocker.Mock(return_value=return_async_value())
    consumer.kafka_consumer.stop = mock_stop

    async def receive_message():
        return SimpleNamespace(value=b'"test_message"')

    mock_receive = mocker.Mock(return_value=receive_message())
    consumer.kafka_consumer.getone = mock_receive

    async with consumer:
        with pytest.raises(RuntimeError, match="cannot reuse already awaited coroutine"):
            await consumer.consume()

    for mock in [mock_start, mock_stop, kafka_consumer_stub]:
        mock.assert_called_once()

    assert len(mock_receive.call_args_list) == 2

    assert "test_message" == kafka_consumer_stub.call_args_list[0][0][0]


# ------------NEGATIVE-------------
@pytest.mark.asyncio
async def test_not_started_consumer(event_loop, config):
    config.config["kafka_config"] = {"bootstrap_servers": 'test', "topic": 'test'}
    consumer = MetricsConsumer(config, event_loop, return_async_value)
    with pytest.raises(AssertionError, match="consumer is not started"):
        await consumer.consume()


@pytest.mark.asyncio
async def test_kafka_unavailable(event_loop, config):
    config.config["kafka_config"] = {"bootstrap_servers": 'test', "topic": 'test'}
    consumer = MetricsConsumer(config, event_loop, return_async_value)
    with pytest.raises(kafka.errors.KafkaConnectionError, match=r".*Unable to bootstrap from.*"):
        await consumer.__aenter__()
