import base64
import json
import re
from typing import Union

JWT_REGEXP = r'^[\w\-]+\.[\w\-]+\.[\w\-]+'


def unpad_jwt_element(jwt: str, position: int) -> dict:
    if isinstance(jwt, bytes):
        jwt = jwt.decode()
    b = jwt.split(".")[position]
    padded = f"{b}{'=' * divmod(len(b), 4)[1]}"
    data = json.loads(base64.urlsafe_b64decode(padded))
    return data


def unpad_jwt_header(jwt: str) -> dict:
    return unpad_jwt_element(jwt, position=0)


def unpad_jwt_payload(jwt: str) -> dict:
    return unpad_jwt_element(jwt, position=1)


def get_jwk_from_jwt(jwt: Union[str, dict], provider_jwks: dict) -> dict:
    """
        docs here
    """
    if isinstance(jwt, str):
        head = unpad_jwt_header(jwt)
    elif isinstance(jwt, dict):
        head = jwt

    kid = head["kid"]
    if isinstance(provider_jwks, dict) and provider_jwks.get('keys'):
        provider_jwks = provider_jwks['keys']
    for jwk in provider_jwks:
        if jwk["kid"] == kid:
            return jwk
    return {}


def is_jwt_format(jwt: str) -> bool:
    res = re.match(JWT_REGEXP, jwt)
    return bool(res)
