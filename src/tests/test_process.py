""" Test thread pool """
from concurrent.futures import ProcessPoolExecutor
from tornado.httpclient import HTTPClient

pool = ProcessPoolExecutor()


def request(item):
    """ request resource """
    uri = f'http://localhost:8080/{item}'
    http_client = HTTPClient()
    response = http_client.fetch(uri)
    return response.body


def do_process(data):
    """ use a process pool executor """
    futures = pool.map(request, data)
    result = list(futures)
    return result


def test_process(data):
    """ test processes """
    assert do_process(data) == [
        b'Hello, romeo',
        b'Hello, julliet',
        b'Hello, mercucio',
    ]
