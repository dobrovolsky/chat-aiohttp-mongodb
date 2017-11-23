import asyncio

from aiohttp import web, hdrs


class LoginRequiredMixin:
    login_url_name = 'signin'

    @asyncio.coroutine
    def __iter__(self):
        if self.request._method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request._method.lower(), None)
        if method is None:
            self._raise_allowed_methods()
        if not self.request.user:
            return web.HTTPFound(self.get_login_url())
        resp = yield from method()
        return resp

    def get_login_url(self):
        return self.request.app.router[self.login_url_name].url_for()