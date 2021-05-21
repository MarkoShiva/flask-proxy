from flask import Flask, request ,Response
import requests

from bs4 import BeautifulSoup

from werkzeug.serving import WSGIRequestHandler
from replace_chars.main import replace_words
import mimetypes


app = Flask(__name__, static_folder = "static/")
mimetypes.add_type("text/javascript", ".js", False)
mimetypes.add_type("text/css", ".css", False)
LOCAL_NAME = '127.0.0.1'
SITE_NAME = 'https://en.wikipedia.org/'





@app.route('/')
def index():
    return 'root'

@app.route('/<path:path>', methods=['GET', 'POST', "DELETE"])
def proxy(path):
    global SITE_NAME
    if request.method == 'GET':
        resp = requests.get(f'{SITE_NAME}{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        if 'php' not in path:    # exclude stuff that are not regular page request from soup
            # append links or just download them with same filename like in page.
            soup = BeautifulSoup(resp.content)
            soup_append = BeautifulSoup('<link href="/static/css/Vector.css" rel="stylesheet" type="text/css"/>',
                                        'html.parser')
            soup.head.append(soup_append)
            soup_append = BeautifulSoup('<script async="" src="/static/js/load.js"></script>', 'html.parser')
            soup.head.append(soup_append)
            soup_append = BeautifulSoup('<link href="/static/css/load.css" rel="stylesheet" type="text/css"/>',
                                        'html.parser')
            soup.head.append(soup_append)
            soup_append = BeautifulSoup('<link href="/static/css/load1.css" rel="stylesheet" type="text/css"/>',
                                        'html.parser')
            soup.head.append(soup_append)
            updated = replace_words(soup)   # run word replacement
            resp._content = updated.encode('utf8')  # use setter and encode as bytestream
            response = Response(resp.content, resp.status_code, headers, mimetype='text/html')
            # specify response mimetype='text/html'
        elif 'scripts' in request.args.values():
            # print(request.args)
            # specify response mimetype='text/javascript'
            response = Response(resp.content, resp.status_code, headers, mimetype='text/javascript')
        elif 'styles' in request.args.values():
            # resp._content
            # specify response mimetype='text/css'
            response = Response(resp.content, resp.status_code, headers, mimetype='text/css')
        else:
            # do not modify
            response = Response(resp.content, resp.status_code, headers)
        return response

    elif request.method == 'POST':
        # we are not posting anything to wikipedia because proxy do not have need to edit as well. :)
        resp = requests.post(f'{SITE_NAME}/{path}',json=request.get_json())
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        print(resp.content)
        response = Response(resp.content, resp.status_code, headers)
        return response





    elif request.method == 'DELETE':
        resp = requests.delete(f'{SITE_NAME}/{path}').content
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        print(resp.content)
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response






if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host=LOCAL_NAME, port=8000, debug=True)
    # app.run(host=LOCAL_NAME, port=8000, debug=True)
