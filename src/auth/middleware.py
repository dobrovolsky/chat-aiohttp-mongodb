from aiohttp_session import get_session
from bson import ObjectId

from user.Exceptions import UserDoesNotExists


async def user_data(app, handler):
    from user.models import User
    async def middleware(request):
        session = await get_session(request)
        user_id = session.get('user_id')
        if user_id:
            try:
                request.user = await User.get_user(_id=ObjectId(user_id))
            except UserDoesNotExists:
                request.user = None
        else:
            request.user = None
        response = await handler(request)
        return response
    return middleware
