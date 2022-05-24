# Should there be an AsyncPoolProcessor?

Python Multiprocessing provides two high level classes that enable us to take advantage of a pool of workers to perform concurrent tasks: ThreadPoolExecutor and ProcessPoolExecutor. I would suggest that a third is missing from the library: AsyncPoolProcessor.

The interface of an Executor is simple. It affords `submit` and `map` methods that takes a function and its arguments as its arguments and return one or many `futures`. A `future` allows for a `result` to be acquired as it becomes available or to throw an `exception` should the called function fail.

So how would an AsyncPoolProcessor look?

```python
class AsyncPoolExecutor(Executor):
    ...
    def submit(self, fn, *args, **kwargs):
        """ part of the executor api """
        if self.running is False:
            raise NotRunningException()
        loop = asyncio.get_running_loop()
        result = loop.create_future()
        self.queue.put_nowait((result, fn, args, kwargs))
        return result

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        """ part of the executor api """
        if self.running is False:
            raise NotRunningException()
        results = []
        args = zip(*iterables)
        for line in args:
            results.append(self.submit(fn, *line))
        return results
```

I am an architect and this is an implementation, certainly neither exhaustive nor correct. But it is testable and can demonstrate the feature that I am suggesting. `Map` is just an iterative call to `Submit`. But we have a `queue` of work and a specified number of `tasks` to perform the work and we return [concurrent.futures.Future](https://docs.python.org/3/library/concurrent.futures.html#future-objects) instance(s). It is that set number of concurrent tasks that this pool provides. Should you be using an external api with limits this could help. Should you be calling a database with a set number of processes, this could help. Iterating the results should provide individual results, but that is more correct and complete that needed to demonstrate my point.

You might notice that the implementations of the Thread and Process Executors implement the Context Manager interface allowing us to write the following:

```python
with ThreadPoolExecutor() as pool:
    responses = pool.map(request, urls)
```

Let us add that to our class as an Async Context Manager:

```python
class AsyncPoolExecutor(Executor):
    ...
    async def __aenter__(self):
        """ This makes us an async contextmanager """
        self.start()
        return self

    async def __aexit__(self, *args):
        """ This is called when the with is up """
        await self.shutdown()
```

Here you can see a difference, our `shutdown` must be `async`. So I have disabled the pylint warning, that my `shutdown` differs from the Executors `shutdown`.

So now we come to the benefit of using this technique - performance. The pytest I provide prepares our Thread and Process pools outside of the performance test, thus avoiding the creation and cleanup overheads. That is not true of the async test. The target of the tests is a [tornado](https://www.tornadoweb.org/en/stable/index.html) server - it merely returns the salutation including the request:

```python
class MainHandler(tornado.web.RequestHandler):  # pylint: disable=W0223
    """ simple welcome """

    def get(self, name):
        """ handle get request """
        self.write(f'Hello, {name}')
```

So, running our server on port 8080, we use a fixture for our data:

```python
@fixture
def data():
    """ our request objects """
    return ['romeo', 'julliet', 'mercucio']
```

And test our ThreadPoolExecutor:

```python
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
```

The ProcessPoolExecutor test is identical but for the construction of the pool. Our async test is near identical too, but that we create the pool within the test using the Context Manager interface, as we have no global event loop:

```python
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
```

So, what about the results. These we gather by benchmarking the functions tested:

```python
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
```

And the results:

```bash
Name (time in ms)         Min                Max               Mean            StdDev
test_a                 9.0464 (1.0)      38.7552 (2.58)     10.4006 (1.0)      3.0807 (3.64)
test_p                10.6764 (1.18)     15.0337 (1.0)      11.9298 (1.15)     0.8462 (1.0)
test_t                13.1372 (1.45)     44.6249 (2.97)     16.7564 (1.61)     5.2769 (6.24)
```

As I said, I am not correct or exhaustive, but I am intrigued. I have used [tornado's](https://www.tornadoweb.org/en/stable/httpclient.html) HTTPClient and AsyncHTTPClient against a tornado server. I assume, but do not know, that that helps expose the efficiency of the library pools. I assume that the high max is the instantiation of the first event loop and threads. This is an IO operation and the very reason that `asyncio` was introduced to the standard library. It performs well.

Thanks for reading. If you'd have any thoughts or would like improve on this, please feel free to comment or be in touch. The source to this madness is available here.

To install:

```
make setup
```

The activate the virtual environment:
```
source venv/bin/activate
```

To run the server:
```
server run
```

To run the tests:
```
server test
```
