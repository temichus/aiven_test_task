import logging
import asyncpg
import asyncio
import os
import ssl

logger = logging.getLogger(__name__)

GET_SIGNALS_TYPES_QUERY = \
    "SELECT monitor.signal_type.id, monitor.signal_type.url_id, monitor.website_url.url, monitor.signal_type.regex " \
    "FROM monitor.signal_type INNER JOIN monitor.website_url ON monitor.signal_type.url_id = monitor.website_url.id;"
GET_URLS = "SELECT id, url FROM monitor.website_url;"
ADD_URL = "INSERT INTO monitor.website_url(url)VALUES ('{}');"
ADD_SIGNAL = "INSERT INTO monitor.signal_type(url_id, regex) VALUES ({}, {});"
LOG_SIGNSL_DATA = \
    "INSERT INTO monitor.signal_data(signal_id, status, response_time, time_code, regex_found) " \
    "VALUES ({}, {}, {}, '{}', {});"


def str_to_sql(str_val):
    if str_val is not None:
        return "'{}'".format(str_val)
    else:
        return "NULL"


def bool_to_sql(bool_val):
    if bool_val is not None:
        return "'{}'".format(int(bool_val))
    else:
        return "NULL"


def numeric_to_sql(val):
    if val is not None:
        return "{}".format(val)
    else:
        return "NULL"


class DbWebsiteMetricsWriter:
    def __init__(self, config):
        conf = config.get_config_attr("sql_credentials")
        self.wipe_db = getattr(config, "wipe_db", False)
        for key, value in conf.items():
            self.__setattr__(key, value)
        self.conn = None
        self.signals_types = None
        self.add_signal_type_lock = asyncio.Lock()

    async def __aenter__(self):
        ssl_context = None
        if hasattr(self, "ca_file"):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ssl_context.load_verify_locations(self.ca_file)
        self.conn = await asyncpg.create_pool(dsn=self.dsn, ssl=ssl_context)
        if self.wipe_db:
            await self.recreate_db()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

    async def _fetch_signals_types(self):
        self.signals_types = await self.conn.fetch(GET_SIGNALS_TYPES_QUERY)

    async def _add_signal(self, url, regex):

        async def get_url_id():
            urls = await self.conn.fetch(GET_URLS)
            for row in urls:
                if row['url'] == url:
                    return row["id"]
            await self.conn.execute(ADD_URL.format(url))
            return await get_url_id()

        url_id = await get_url_id()
        print(ADD_SIGNAL.format(url_id, str_to_sql(regex)))
        await self.conn.execute(ADD_SIGNAL.format(url_id, str_to_sql(regex)))

    async def get_signal_id(self, url, regex):
        if not self.signals_types:
            await self._fetch_signals_types()

        async def get_signal():
            def search_id():
                ids = [row['id'] for row in self.signals_types if row['url'] == url and row['regex'] == regex]
                if ids:
                    return ids[0]
                return None

            signal_id = search_id()
            if signal_id:
                return signal_id
            else:
                async with self.add_signal_type_lock:
                    signal_id = search_id()
                    if signal_id:
                        return signal_id
                    await self._add_signal(url, regex)
                    await self._fetch_signals_types()
                    return await get_signal()

        return await get_signal()

    async def log_signal_data(self, url, response_time, timestamp, status_code, regex, regex_found):
        signal_id = await self.get_signal_id(url, regex)
        query = LOG_SIGNSL_DATA.format(signal_id, numeric_to_sql(status_code), numeric_to_sql(response_time), timestamp,
                                     bool_to_sql(regex_found))
        logger.info(query)
        await self.conn.execute(query)

    async def recreate_db(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_scripts", "drop_tables.sql"), "r") as f:
            await self.conn.execute(f.read())
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_scripts", "create_tables.sql"),
                  "r") as f:
            await self.conn.execute(f.read())
