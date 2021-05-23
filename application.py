import re
from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup, NavigableString
from werkzeug.serving import WSGIRequestHandler
import mimetypes
import typing as t

def clean_headers(resp: Response) -> Response:
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    print(resp.content)
    response = Response(resp.content, resp.status_code, headers)
    return resp






class WebProxy(Flask):
    def __init__(self,
                 import_name: str,
                 site_name: t.Optional[str] = "en.wikipedia.org/",
                 phrase: t.Optional[str] = "WARP!",
                 regex: t.Optional[str] = None,
                 word_length: t.Optional[int] = None,
                 static_url_path: t.Optional[str] = None,
                 static_folder: t.Optional[str] = "static",
                 static_host: t.Optional[str] = None,
                 host_matching: bool = False,
                 subdomain_matching: bool = False,
                 template_folder: t.Optional[str] = "templates",
                 instance_path: t.Optional[str] = None,
                 instance_relative_config: bool = False,
                 root_path: t.Optional[str] = None,
                 ):
        super().__init__(
                import_name = import_name,
                static_url_path = static_url_path,
                static_folder = static_folder,
                static_host = static_host,
                host_matching = host_matching,
                subdomain_matching = subdomain_matching,
                template_folder = template_folder,
                instance_path = instance_path,
                instance_relative_config = instance_relative_config,
                root_path = root_path)
        self.site_name = site_name
        self.phrase = phrase
        self.regex_string = regex
        self.word_length = word_length
        self.regex = None

    def replace_words(self,
                      soup: BeautifulSoup,
                      phrase: t.Optional[str] = "WARP!",
                      wl: int = 5,
                      regex = None):
        if regex:
            self.regex_string = regex
        else:
            self.regex_string = fr"\b\w{{{wl}}}\b"
        self.regex = re.compile(self.regex_string)
        if soup.find('body'):
            page = soup.body.find_all(text = self.regex)
            for line in page:
                if not re.match(r"^(?!http+)[[a-zA-Z0-9'\"]+", line):
                    continue
                elif isinstance(line, NavigableString):
                    words = re.sub(self.regex, phrase, line)
                    line.replace_with(words)
            print(soup.text.count(phrase))
        return soup


app = WebProxy(__name__, static_folder = "static/")
mimetypes.add_type("text/javascript", ".js", False)
mimetypes.add_type("text/css", ".css", False)


@app.route('/')
def index():
    return 'root'


@app.route('/<path:path>', methods=['GET', 'POST', "DELETE"])
def proxy(path):
    # global SITE_NAME
    if request.method == 'GET':
        resp = requests.get(f'https://{app.site_name}{path}')
        # resp = requests.get(f'http://{app.site_name}{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        if 'php' not in path:    # exclude stuff that are not regular page request from soup
            soup = BeautifulSoup(resp.content)
            soup_append = BeautifulSoup('<link href="/static/css/Vector.css" rel="stylesheet" type="text/css"/> '
                                        '<script async="" src="/static/js/load.js"></script>'
                                        '<link href="/static/css/load.css" rel="stylesheet" type="text/css"/>'
                                        '<link href="/static/css/load1.css" rel="stylesheet" type="text/css"/>',
                                        'html.parser')
            soup.head.append(soup_append)
            updated = app.replace_words(soup, "f(x)=ac^{x}", wl=5)
            resp._content = updated.encode('utf8')
            response = Response(resp.content, resp.status_code, headers, mimetype='text/html')
        elif 'scripts' in request.args.values():
            response = Response(resp.content, resp.status_code, headers, mimetype='text/javascript')
        elif 'styles' in request.args.values():
            response = Response(resp.content, resp.status_code, headers, mimetype='text/css')
        else:
            response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == 'POST':
        resp = requests.post(f'https://{app.site_name}/{path}',json=request.get_json())
        return clean_headers(resp)
    elif request.method == 'DELETE':
        resp = requests.delete(f'https://{app.site_name}/{path}')
        return clean_headers(resp)


LOCAL_NAME = '127.0.0.1'

if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host=LOCAL_NAME, port=8000, debug=True)
