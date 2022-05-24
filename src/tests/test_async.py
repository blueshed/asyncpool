""" Test async pool """
import asyncio
from tornado.httpclient import AsyncHTTPClient
from server.pool import AsyncPoolExecutor


async def request(item):
    """ request resource """
    uri = f'http://localhost:8080/{item}'
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(uri)
    return response.body


async def do_tasks(data):
    """ can we make requests """
    async with AsyncPoolExecutor() as pool:
        futures = pool.map(request, data)
    result = [item.result() for item in futures]
    return result


def test_tasks(data):
    """ run test in asyncio """
    result = asyncio.run(do_tasks(data))
    assert result == [b'Hello, romeo', b'Hello, julliet', b'Hello, mercucio']
