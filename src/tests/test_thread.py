""" Test thread pool """
from concurrent.futures import ThreadPoolExecutor
from tornado.httpclient import HTTPClient

pool = ThreadPoolExecutor()


def request(item):
    """ request resource """
    uri = f'http://localhost:8080/{item}'
    http_client = HTTPClient()
    response = http_client.fetch(uri)
    return response.body


def do_threads(data):
    """ use a thread pool executor """
    futures = pool.map(request, data)
    result = list(futures)
    return result


def test_threads(data):
    """ test threads """

    assert do_threads(data) == [
        b'Hello, romeo',
        b'Hello, julliet',
        b'Hello, mercucio',
    ]
