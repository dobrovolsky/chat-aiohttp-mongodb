import aiohttp_jinja2
from aiohttp import web

from chat.user.models import User
from chat.user.validators import UserSingUpValidator


class SignUp(web.View):
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
