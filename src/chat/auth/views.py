import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session

from chat.auth.validators import UserSingUpValidator, UserSingInValidator
from chat.user.Exceptions import UserDoesNotExists
from chat.user.models import User
from chat.user.utils import get_hash


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
            await user.is_valid()
            await user.save()
        else:
            return web.json_response(data=user_data.errors, status=400)
        return web.json_response(data={}, status=201)


class SignInView(web.View):
    """Provide login user to site"""

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        """render template with sign in form"""
        session = await get_session(self.request)
        context = {}
        if session.get('user_id'):
            return web.HTTPFound('/')
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
                session['user_id'] = user._id
                return web.json_response(data={}, status=200)
        else:
            return web.json_response(data=user_data.errors, status=400)

