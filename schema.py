from pydantic import BaseModel, field_validator, ValidationError
from errors import generate_error
from aiohttp.web import HTTPBadRequest


class CreateAnnounSchema(BaseModel):
    title: str
    description: str


class UpdateAnnounSchema(BaseModel):
    title: str | None = None
    description: str | None = None


class BaseUserSchema(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if password is not None and len(password) < 8:
            raise ValueError("password less than 8 characters")
        return password


class CreateUserSchema(BaseUserSchema):
    pass


class UpdateUserSchema(BaseUserSchema):
    email: str | None = None
    password: str | None = None


def validate_json(schema_cls: type, json_data: dict) -> dict:
    try:
        check_validate = schema_cls(**json_data)
        return check_validate.dict(exclude_unset=True)
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            error.pop("ctx", None)
        raise generate_error(HTTPBadRequest, errors)
