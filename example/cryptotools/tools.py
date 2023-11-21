from django.utils import timezone
from django.utils.timezone import make_aware

from secrets import token_hex

import datetime
import binascii
import json
import cryptojwt
import logging
import re

from cryptojwt.jwe.jwe import factory
from cryptojwt.jwe.jwe_ec import JWE_EC
from cryptojwt.jwe.jwe_rsa import JWE_RSA
from cryptojwt.jwk.ec import new_ec_key
from cryptojwt.jwk.jwk import key_from_jwk_dict
from cryptojwt.jws.jws import JWS
from django.conf import settings

from . jwt import unpad_jwt_header

from typing import Union

DEFAULT_EC_CRV = getattr(settings, "DEFAULT_EC_CRV", "P-256")
DEFAULT_HASH_FUNC = getattr(settings, "DEFAULT_HASH_FUNC", "P256")
DEFAULT_JWE_ALG = getattr(settings, "DEFAULT_JWE_ALG", "RSA-OAEP")
DEFAULT_JWE_ENC = getattr(settings, "DEFAULT_JWE_ENC", "A256CBC-HS512")
ENCRYPTION_ENC_SUPPORTED = getattr(
    settings, 
    "ENCRYPTION_ENC_SUPPORTED", [
        "A128CBC-HS256",
        "A192CBC-HS384",
        "A256CBC-HS512",
        "A128GCM",
        "A192GCM",
        "A256GCM",
    ]
)
SIGNING_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "SIGNING_ALG_VALUES_SUPPORTED",
    ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
)
ENCRYPTION_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "ENCRYPTION_ALG_VALUES_SUPPORTED",
    [
        "RSA-OAEP",
        "RSA-OAEP-256",
        "ECDH-ES",
        "ECDH-ES+A128KW",
        "ECDH-ES+A192KW",
        "ECDH-ES+A256KW",
    ],
)

logger = logging.getLogger(__name__)


def iat_now() -> int:
    return int(datetime.datetime.now().timestamp())


def exp_from_now(minutes: int = 33) -> int:
    _now = timezone.localtime()
    return int((_now + datetime.timedelta(minutes=minutes)).timestamp())


def secparams_check(payload :dict, aud : Union [str, list], allowed_clients :list) -> bool:
    if not all(
        (
            payload.get('iss', None),
            payload.get('iat', None) < iat_now(),
            payload.get('exp', None) > iat_now(),            
            payload.get('aud', None) in (aud, re.sub("^https?://", "", aud))
        )
    ):
        return False
    

    if isinstance(allowed_clients, str):
        allowed_clients = [allowed_clients]
    
    
    for i in allowed_clients:
        if i == payload['iss']:
            return True
    
    return False


def datetime_from_timestamp(value) -> datetime.datetime:
    return make_aware(datetime.datetime.fromtimestamp(value))


def create_jwk(key = None, hash_func=None, crv = None) -> tuple:
    key = key or new_ec_key(crv = crv or DEFAULT_EC_CRV)
    key.add_kid()
    return key.serialize(private = True), key.serialize()


def key_from_jwk(jwk_dict: dict) -> tuple:
    key = key_from_jwk_dict(jwk_dict)
    return key.serialize(private = True), key.serialize()


def create_jws(payload: dict, jwk_dict: dict, alg: str = "ES256", protected:dict = {}, **kwargs) -> str:
    _key = key_from_jwk_dict(jwk_dict)
    _signer = JWS(payload, alg=alg, **kwargs)

    jwt = _signer.sign_compact([_key], protected=protected, **kwargs)
    return jwt


def verify_jws(jws: str, pub_jwk: dict, **kwargs) -> str:
    _key = key_from_jwk_dict(pub_jwk)

    _head = unpad_jwt_header(jws)
    if _head.get("kid") != pub_jwk["kid"]:  # pragma: no cover
        raise Exception(
            f"kid error: {_head.get('kid')} != {pub_jwk['kid']}"
        )

    _alg = _head["alg"]
    if _alg not in SIGNING_ALG_VALUES_SUPPORTED or not _alg:  # pragma: no cover
        raise UnsupportedAlgorithm(f"{_alg} has beed disabled for security reason")

    verifier = JWS(alg=_head["alg"], **kwargs)
    msg = verifier.verify_compact(jws, [_key])
    return msg


def create_jwe(plain_dict: Union[dict, str, int, None], jwk_dict: dict, **kwargs) -> str:
    logger.debug(f"Encrypting dict as JWE: " f"{plain_dict}")
    _key = key_from_jwk_dict(jwk_dict)

    if isinstance(_key, cryptojwt.jwk.rsa.RSAKey):
        JWE_CLASS = JWE_RSA
    elif isinstance(_key, cryptojwt.jwk.ec.ECKey):
        JWE_CLASS = JWE_EC

    if isinstance(plain_dict, dict):
        _payload = json.dumps(plain_dict).encode()
    elif not plain_dict:
        logger.warning(f"create_jwe with null payload!")
        _payload = ""
    elif isinstance(plain_dict, (str, int)):
        _payload = plain_dict
    else:
        logger.error(f"create_jwe with unsupported payload type!")
        _payload = ""

    _keyobj = JWE_CLASS(
        _payload,
        alg=DEFAULT_JWE_ALG,
        enc=DEFAULT_JWE_ENC,
        kid=_key.kid,
        **kwargs
    )

    jwe = _keyobj.encrypt(_key.public_key())
    logger.debug(f"Encrypted dict as JWE: {jwe}")
    return jwe


def decrypt_jwe(jwe: str, jwk_dict: dict) -> dict:
    # get header
    try:
        jwe_header = unpad_jwt_header(jwe)
    except (binascii.Error, Exception) as e:  # pragma: no cover
        logger.error(f"Failed to extract JWT header: {e}")
        raise Exception("The JWT is not valid")

    _alg = jwe_header.get("alg", DEFAULT_JWE_ALG)
    _enc = jwe_header.get("enc", DEFAULT_JWE_ENC)
    # jwe_header.get("kid")

    if _alg not in ENCRYPTION_ALG_VALUES_SUPPORTED:  # pragma: no cover
        raise UnsupportedAlgorithm(f"{_alg} has beed disabled for security reason")

    _decryptor = factory(jwe, alg=_alg, enc=_enc)
    _dkey = key_from_jwk_dict(jwk_dict)
    msg = _decryptor.decrypt(jwe, [_dkey])
    return msg
