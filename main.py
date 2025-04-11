import jwt
from errors import generate_error
from aiohttp import web
from config import SECRET_KEY_TOKEN
from aiohttp.web import middleware
from dependencies import Session
from auth import hash_password, check_password, create_jwt
from functions.functions_main import (
    add_user,
    add_announ,
    get_announ_by_id,
    get_user_by_email,
)
from schema import (
    validate_json,
    CreateUserSchema,
    CreateAnnounSchema,
    UpdateAnnounSchema,
)
from models import User, Announcement
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiohttp.web import HTTPUnauthorized, HTTPForbidden


@middleware
async def session_middleware(request: web.Request, handler):

    async with Session() as session:
        request.session = session
        response = await handler(request)

        return response


async def jwt_middleware(app, handler):
    async def middleware_handler(request):
        token = request.headers.get("Authorization")
        if token:
            parts = token.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                try:
                    payload = jwt.decode(
                        parts[1], SECRET_KEY_TOKEN, algorithms=["HS256"]
                    )
                    request["email_user"] = payload["user_id"]
                    return await handler(request)
                except jwt.ExpiredSignatureError:
                    return generate_error(
                        HTTPUnauthorized, "Token has expired"
                    )
                except jwt.InvalidTokenError:
                    return generate_error(HTTPUnauthorized, "Invalid token")
            else:
                return generate_error(
                    HTTPUnauthorized,
                    "Authorization header must be Bearer <token>"
                )
        return await handler(request)

    return middleware_handler


app = web.Application(middlewares=[session_middleware, jwt_middleware])


class RegisterView(web.View):

    async def post(self):
        json_data = await self.request.json()
        validate_data = validate_json(CreateUserSchema, json_data)
        user = await get_user_by_email(
            email=validate_data["email"], session=self.request.session
        )
        if user and check_password(validate_data["password"], user.password):
            token = create_jwt(user_email=user.email)
            return web.json_response({"token": token})

        return web.json_response({"error": "Invalid credentials"})


class BaseView(web.View):

    @property
    def session(self) -> async_sessionmaker:
        return self.request.session

    @property
    def user_id(self) -> int:
        return int(self.request.match_info.get("user_id"))

    @property
    def announ_id(self) -> int:
        return int(self.request.match_info.get("announ_id"))

    @property
    async def get_json_data(self) -> dict:
        return await self.request.json()

    @property
    def get_session_email_user(self) -> str:
        return self.request.get("email_user")


class UserView(BaseView):

    async def get(self):
        pass

    async def post(self):
        json_data = self.get_json_data
        validate_data = validate_json(CreateUserSchema, json_data)
        email = validate_data.get("email")
        password = hash_password(validate_data.get("password"))
        user = User(email=email, password=password)
        await add_user(user, self.session)
        return web.json_response(user.json_user)

    async def patch(self):
        pass

    async def delete(self):
        pass


class AnnounView(BaseView):

    async def get(self):
        user = await get_user_by_email(
            self.get_session_email_user,
            self.session
        )
        announ = await get_announ_by_id(self.announ_id, self.session)
        if user.id == announ.user_id:
            return web.json_response(announ.json_announ)
        else:
            raise generate_error(HTTPForbidden, "No access")

    async def post(self):
        user_email = self.get_session_email_user
        if user_email is None:
            raise generate_error(HTTPUnauthorized, "Permision denied")

        user = await get_user_by_email(user_email, self.session)
        json_data = await self.get_json_data
        validate_data = validate_json(CreateAnnounSchema, json_data)
        title = validate_data.get("title")
        description = validate_data.get("description")
        announ = Announcement(
            title=title,
            description=description,
            user_id=user.id
        )
        await add_announ(announ, self.session)
        return web.json_response(announ.json_announ)

    async def patch(self):
        user = await get_user_by_email(
            self.get_session_email_user,
            self.session
        )
        announ = await get_announ_by_id(self.announ_id, self.session)
        if user.id == announ.user_id:
            json_data = await self.get_json_data
            validate_data = validate_json(UpdateAnnounSchema, json_data)
            if validate_data.get("title"):
                announ.title = validate_data["title"]
            if validate_data.get("description"):
                announ.description = validate_data["description"]
            await add_announ(announ, self.session)
            return web.json_response(announ.json_announ)
        else:
            raise generate_error(HTTPForbidden, "No access")

    async def delete(self):
        user = await get_user_by_email(
            self.get_session_email_user,
            self.session
        )
        announ = await get_announ_by_id(self.announ_id, self.session)
        if user.id == announ.user_id:
            await self.session.delete(announ)
            await self.session.commit()
            return web.json_response(
                {"status": f"Announcement id: {self.announ_id} delete"}
            )
        else:
            raise generate_error(HTTPForbidden, "No access")


app.add_routes(
    [
        web.post("/api/v1/announcements", AnnounView),
        web.get("/api/v1/announcements/{announ_id:[0-9]+}", AnnounView),
        web.patch("/api/v1/announcements/{announ_id:[0-9]+}", AnnounView),
        web.delete("/api/v1/announcements/{announ_id:[0-9]+}", AnnounView),
        web.post("/api/v1/registration", RegisterView),
        web.post("/api/v1/users", UserView),
    ]
)
if __name__ == "__main__":
    web.run_app(app)
