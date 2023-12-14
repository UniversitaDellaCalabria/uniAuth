import uuid 

from copy import deepcopy
from django.conf import settings

from . tools import iat_now, exp_from_now, create_jws


def issue_security_jwts(audiences :list, subject :str, **kwargs) -> dict:
    jwk = settings.PRIVATE_SIGNATURE_JWKS["keys"][0]
    payloads = {}
    data =  {
        "iss": getattr(settings, "BASE", "https://example.org"),
        "jti": str(uuid.uuid4()),
        "iat": iat_now(),
        "exp": exp_from_now(
            minutes = getattr(settings, "DEFAULT_EXP", 3)
        ),
        "sub": subject
    }
    data.update(kwargs)
    
    for aud in audiences:
        _d = deepcopy(data)
        _d["aud"] = aud
        payloads[aud] = create_jws(payload = _d, jwk_dict = jwk)
    
    return payloads
