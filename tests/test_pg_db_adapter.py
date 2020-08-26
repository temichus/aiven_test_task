import logging
import pytest
from types import SimpleNamespace
from common.config_parser import Config
from consumer.pg_db_adapter import DbWebsiteMetricsWriter
from asyncmock import AsyncMock

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def config():
    conf = Config([])
    conf.config["sql_credentials"] = {"ca_file" : "test" , "dsn" : "test"}
    return conf

#------------POSITIVE-------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_input,expected",
    [(["test", 1, "test", 200, "test", True],[{'url': "test",'id': "test", "regex" : "test"}]),
    (["test", None, "test", None, None, None],[{'url': "test",'id': "test", "regex" : None}])])
async def test_log_new_url_signal_data(mocker, config, test_input, expected):
    mocker.patch('consumer.pg_db_adapter.ssl')
    close_mock = AsyncMock()
    fetch_mock = AsyncMock(side_effect=[[], [], [{'url': "test",'id': "test"}], expected])
    execute_mock = AsyncMock()
    async def await_pool():
        return SimpleNamespace(close=close_mock, fetch=fetch_mock, execute=execute_mock)
    mocker.patch('asyncpg.create_pool' , return_value=await_pool())
    db_writer = DbWebsiteMetricsWriter(config)
    async with db_writer:
        await db_writer.log_signal_data(*test_input)


