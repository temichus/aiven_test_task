import json
import logging
from aiokafka import AIOKafkaProducer
from common.kafka_ssl_context_helper import get_ssl_context

logger = logging.getLogger(__name__)


class MetricsProducer:
    """
    Kafka producer wrapper
    """

    def __init__(self, config, loop):
        """
        :param config: Config obj
        :param loop: event loop
        """
        config = config.get_config_attr("kafka_config")
        self.bootstrap_servers = config["bootstrap_servers"]
        self.topic = config["topic"]
        self.loop = loop
        self.is_started = False

        add_ops = {}
        if "ssl_context" in config:
            ssl_context = get_ssl_context(**config["ssl_context"])
            add_ops = {"security_protocol": "SSL", "ssl_context": ssl_context}

        self.producer = AIOKafkaProducer(
            loop=self.loop, bootstrap_servers=self.bootstrap_servers, **add_ops)

    async def __aenter__(self):
        """
        Connect Producer to Kafka service
        """
        await self.producer.start()
        self.is_started = True

    async def __aexit__(self, exc_type, exc, tb):
        """
        Disconnect Producer form Kafka service
        """
        await self.producer.stop()
        self.is_started = False

    async def send(self, data):
        """
        Send json message
        """
        assert self.is_started, "producer is not started"
        logger.info(f"Send {data} to kafka topic {self.topic}")
        await self.producer.send_and_wait(self.topic, json.dumps(data).encode("utf-8"))
