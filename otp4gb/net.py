"""
``otp4gb.net`` -- Network utilities
--------------------------------------------
"""

import urllib.request


def api_call(url):
    request = urllib.request.Request(url, headers={
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(request) as r:
        body = r.read().decode(r.info().get_param('charset') or 'utf-8')
    return body
