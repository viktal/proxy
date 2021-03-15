import brotli
from http_parser.http import HttpStream, ParserError

END_HEADERS = '\r\n\r\n'
END_ONE_HEADER = '\r\n'


def join_data(request: HttpStream, type_: str):
    assert type_ in ('Request', 'Response')
    # try:
    major, minor = request.version()
    # except ParserError:
    #     raise
    if type_ == 'Request':
        url = request.url()
        start_line = f'{request.method()} {url} HTTP/{major}.{minor}'
    else:
        start_line = f'HTTP/{major}.{minor} {request.status()}'

    body = request.body_string(binary=True)
    headers = request.headers()
    setcookies = headers['Set-Cookie'] if 'Set-Cookie' in headers else None
    if "Content-Encoding" in headers:
        assert headers["Content-Encoding"] == "br"
        body = brotli.decompress(body)

    for key in ['Transfer-Encoding', 'Content-Encoding', 'Content-Length', 'Set-Cookie']:
        if key in headers:
            del headers[key]

    headers['Content-Length'] = len(body)
    headers = [f'{key}: {value}' for key, value in headers.items()]
    if setcookies is not None:
        setcookies = setcookies.split(",")
        ind = 0
        while ind < len(setcookies):
            if setcookies[ind].lower()[:-4].endswith('expires'):
                headers.append(f"Set-Cookie: {setcookies[ind]}, {setcookies[ind + 1]}")
                ind += 2
            else:
                headers.append(f"Set-Cookie: {setcookies[ind]}")
                ind += 1
    headers = END_ONE_HEADER.join(headers)

    return (start_line + END_ONE_HEADER + headers + END_HEADERS).encode('ISO-8859-1') + body