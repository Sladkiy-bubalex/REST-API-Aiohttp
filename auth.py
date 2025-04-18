import jwt
import datetime
from config import SECRET_KEY_TOKEN
from bcrypt import hashpw, gensalt, checkpw


def hash_password(password: str):
    byte_password = password.encode()
    hashed_password = hashpw(byte_password, gensalt())
    password = hashed_password.decode()
    return password


def check_password(password: str, hashed_password: str):
    byte_pw = password.encode()
    byte_hashed_pw = hashed_password.encode()
    return checkpw(byte_pw, byte_hashed_pw)


def create_jwt(user_email):
    payload = {
        "user_id": user_email,
        "exp": datetime.datetime.now() + datetime.timedelta(days=30),
    }
    return jwt.encode(payload, SECRET_KEY_TOKEN, algorithm="HS256")
