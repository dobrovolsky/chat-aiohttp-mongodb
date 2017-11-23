import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from auth.validators import UserSingUpValidator, UserSingInValidator
from common.view_mixins import LoginRequiredMixin
from user.Exceptions import UserDoesNotExists
from user.models import User

from user.utils import get_hash


class SignUpView(web.View):
    """Provide sign up new user"""

    @aiohttp_jinja2.template('sing_up.html')
    async def get(self):
        """render template with sign up form"""
        return {}

    async def post(self):
        """create new user"""
        data = await self.request.post()
        user_data = UserSingUpValidator(**data)
        if await user_data.is_valid():
            user = User(**user_data.get_data())
            user.is_valid()
            await user.save()
        else:
            return web.json_response(data=user_data.errors, status=400)
        return web.json_response(data={}, status=201)


class SignInView(web.View):
    """Provide login user to site"""

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        """render template with sign in form"""
        context = {
            'request': self.request
        }
        if self.request.user:
            return web.HTTPFound('/chat-list')
        return context

    async def post(self):
        """login user to site"""
        data = await self.request.post()
        session = await get_session(self.request)
        user_data = UserSingInValidator(**data)
        if user_data.is_valid():
            try:
                user = await User.get_user(email=data['email'], password=get_hash(data['password']))
            except UserDoesNotExists:
                return web.json_response(data={'error': 'user with this credential does not exist'}, status=400)
            else:
                session['user_id'] = str(user.id)
                return web.json_response(data={}, status=200)
        else:
            return web.json_response(data=user_data.errors, status=400)


class IndexView(LoginRequiredMixin, web.View):
    async def get(self):
        return web.HTTPFound(self.request.app.router['chat_list'].url_for())


class SignOut(LoginRequiredMixin, web.View):
    async def get(self):
        session = await get_session(self.request)
        session.invalidate()
        return web.HTTPFound(self.get_login_url())
