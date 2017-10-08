import aiohttp_jinja2
from aiohttp import web

from chat.user.models import User


class SignUp(web.View):
    """Provide sign up new user"""

    @aiohttp_jinja2.template('sing_up.html')
    async def get(self):
        """render template with sign up form"""
        return {}

    async def post(self):
        """create new user"""
        data = await self.request.post()
        user = User(**data)
        if await user.is_valid(check_email=True):
            await user.save()
        else:
            return web.json_response(data=user.errors, status=400)
        return web.json_response(data={}, status=201)
