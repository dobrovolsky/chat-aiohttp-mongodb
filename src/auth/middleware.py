from aiohttp_session import get_session


async def user_data(app, handler):
    from user.models import User
    async def middleware(request):
        session = await get_session(request)
        user_id = session.get('user_id')
        if user_id:
            request.user = await User.get_user(uuid=user_id)
        else:
            request.user = None
        response = await handler(request)
        return response
    return middleware