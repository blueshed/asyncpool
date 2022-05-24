""" performance test """
import asyncio
from functools import partial
from .test_async import do_tasks
from .test_process import do_process
from .test_thread import do_threads


def test_a(data, benchmark):
    """ test our async task """

    def run():
        return asyncio.run(do_tasks(data))

    result = benchmark(run)
    assert result == [b'Hello, romeo', b'Hello, julliet', b'Hello, mercucio']


def test_t(data, benchmark):
    """ test our thread task """
    result = benchmark(partial(do_threads, data))
    assert result == [b'Hello, romeo', b'Hello, julliet', b'Hello, mercucio']


def test_p(data, benchmark):
    """ test our process task """
    result = benchmark(partial(do_process, data))
    assert result == [b'Hello, romeo', b'Hello, julliet', b'Hello, mercucio']
