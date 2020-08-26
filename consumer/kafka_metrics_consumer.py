import json
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from common.kafka_ssl_context_helper import get_ssl_context

logger = logging.getLogger(__name__)


class MetricsConsumer:
    def __init__(self, config, loop, consumer):
        config = config.get_config_attr("kafka_config")
        self.bootstrap_servers = config["bootstrap_servers"]
        self.topic = config["topic"]
        self.loop = loop
        self.consumer = consumer
        self.is_started = False

        add_ops = {}
        if "ssl_context" in config:
            ssl_context  = get_ssl_context(**config["ssl_context"])
            add_ops = {"security_protocol" : "SSL", "ssl_context" : ssl_context}

        self.kafka_consumer = AIOKafkaConsumer(
            self.topic, loop=self.loop, bootstrap_servers=self.bootstrap_servers, group_id=self.topic,
            **add_ops)

    async def __aenter__(self):
        await self.kafka_consumer.start()
        self.is_started = True

    async def __aexit__(self, exc_type, exc, tb):
        await self.kafka_consumer.stop()
        self.is_started = False

    async def consume(self):
        assert self.is_started, "consumer is not started"
        async for msg in self.kafka_consumer:
            logger.info(msg)
            asyncio.ensure_future(self.consumer(json.loads(msg.value.decode("utf-8"))))
