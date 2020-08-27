import re
import aiohttp
import asyncio
import logging
import time
import datetime
from common.helpers.config_helpers import get_config_attr

logger = logging.getLogger(__name__)

"""Setup TraceConfig Callbacks to get request time and response time in asynchronous request"""


##################################################################################################
async def on_request_start(
        session, trace_config_ctx, params):
    trace_config_ctx.start = asyncio.get_event_loop().time()
    trace_config_ctx.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')


async def on_request_end(session, trace_config_ctx, params):
    elapsed = round(asyncio.get_event_loop().time() - trace_config_ctx.start, 2)
    trace_config_ctx.trace_request_ctx.set_result((elapsed, trace_config_ctx.timestamp))


trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)


##################################################################################################


class WebsitesChecker:
    """
    Websites Checker
    """

    def __init__(self, config, loop, producer):
        """
        :param config: Config obj
        :param loop: event loop
        :param producer: Coroutine callback produce website check result
        """
        self.delay = config.get_config_attr("delay_between_checks")
        self.websites_to_check = config.get_config_attr("websites_to_check")
        self.loop = loop
        self.producer = producer

    async def _get_url(self, url):
        """
        do HTTP GET for url 
        :param url: str
        :return: (dict) website check result
        """
        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with aiohttp.ClientSession(trace_configs=[trace_config], timeout=timeout) as session:
                response_time_future = asyncio.Future(loop=self.loop)
                async with session.get(url, trace_request_ctx=response_time_future) as response:
                    response_time, timestamp = await response_time_future
                    data = {"url": url,
                            "response_time": response_time,
                            "timestamp": timestamp,
                            "status_code": response.status,
                            "content": await response.text()}
        except aiohttp.client_exceptions.ClientConnectorError as e:
            logger.error(e)
            data = {"url": url,
                    "response_time": None,
                    "timestamp": datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    "status_code": None,
                    "content": None}
        return data

    async def _check_website(self, website_conf):
        """
        Check website for availability and content
        :param website_conf: dict
        :return: 
        """
        data = await self._get_url(website_conf["url"])
        self._check_content(website_conf, data)
        await self.producer(data)

    @staticmethod
    def _check_content(website_conf, data):
        """
        checking the returned page contents for a regexp pattern
        :param website_conf: dict
        :param data: dict
        :return:
        """
        regex = get_config_attr(website_conf, "regex")
        data["regex"] = regex
        if regex:
            data["regex_found"] = bool(re.search(regex, data["content"]))
        else:
            data["regex_found"] = None
        del data["content"]

    async def run(self):
        """
        Run website checker once
        :return: (list) created tasks for checking
        """
        tasks = []
        for website_conf in self.websites_to_check:
            tasks.append(asyncio.ensure_future(self._check_website(website_conf), loop=self.loop))
        return tasks

    async def run_forever(self):
        """
        Run website checker in infinity loop
        """
        while True:
            await self.run()
            await asyncio.sleep(self.delay)
