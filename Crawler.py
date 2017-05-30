from datetime import timedelta

from tornado import httpclient, gen, ioloop, queues

from setting import proxy


class AsySpider(object):
    def __init__(self, urls, concurrency):
        self.urls = urls
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()
        self._items = set()
        self.proxy = proxy

    def handle_page(self, html, url):
        """
        overwrite here to do operation on page
        """
        pass

    @gen.coroutine
    def get_page(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
                'Host': 'www.quora.com',
            }
            response = yield httpclient.AsyncHTTPClient().fetch(url, headers=headers, **self.proxy)
        except Exception as e:
            print('Exception: %s %s' % (e, url))
            raise gen.Return('')
        raise gen.Return(response.body)

    @gen.coroutine
    def _run(self):

        @gen.coroutine
        def fetch_url():
            current_url = yield self._q.get()
            try:
                if current_url in self._fetching:
                    return
                self._fetching.add(current_url)
                html = yield self.get_page(current_url)
                self._fetched.add(current_url)
                if html:
                    self.handle_page(html, current_url)
                for i in range(self.concurrency):
                    if self.urls:
                        yield self._q.put(self.urls.pop())
            finally:
                self._q.task_done()

        self._q.put(self.urls.pop())

        # Start workers, then wait for the work queue to be empty.
        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()

        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300000))  # set a timeout
        assert self._fetching == self._fetched

    def run(self):

        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)
