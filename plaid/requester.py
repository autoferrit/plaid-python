import json

from functools import partial

import requests

from plaid.errors import PlaidError
from plaid.version import __version__

ALLOWED_METHODS = {'post'}
DEFAULT_TIMEOUT = 600  # 10 minutes


def _requests_http_request(url, method, data, timeout=DEFAULT_TIMEOUT):
    normalized_method = method.lower()
    if normalized_method in ALLOWED_METHODS:
        return getattr(requests, normalized_method)(
            url,
            json=data,
            headers={
                'User-Agent': 'Plaid Python v{}'.format(__version__),
            },
            timeout=timeout, )
    else:
        raise Exception('Invalid request method {}'.format(method))


async def _requests_http_request_async(url,
                                       method=None,
                                       data=None,
                                       timeout=DEFAULT_TIMEOUT):
    import aiohttp
    headers = {'content-type': 'application/json'}
    async with aiohttp.ClientSession(read_timeout=timeout) as session:
        async with session.post(
                url, data=json.dumps(data), headers=headers) as resp:
            body = await resp.json()
            if body.get('error_type'):
                raise PlaidError.from_response(body)
            else:
                return body


def http_request(url, method=None, data=None, timeout=DEFAULT_TIMEOUT):
    response = _requests_http_request(url, method, data or {}, timeout)
    response_body = json.loads(response.text)
    if response_body.get('error_type'):
        raise PlaidError.from_response(response_body)
    else:
        return response_body


def http_request_async(url, method=None, data=None, timeout=DEFAULT_TIMEOUT):
    response = _requests_http_request_async(url, method, data, timeout)
    return response


# helpers to simplify partial function application
post_request = partial(http_request, method='POST')
post_request_async = partial(http_request_async, method='POST')
