from flask import Flask,request,Response
import requests

from bs4 import BeautifulSoup as bs

from replace_chars.main import replace_words

app = Flask(__name__,  static_folder='static')
LOCAL_NAME = 'https://localhost:8000'
SITE_NAME = 'https://en.wikipedia.org'


@app.route('/')
def index():
    return 'root'








@app.route('/<path:path>', methods=['GET', 'POST', "DELETE"])
def proxy(path):
    global SITE_NAME
    if request.method == 'GET':
        resp = requests.get(f'{SITE_NAME}/{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        if 'php' not in path:
            soup = bs(resp.content)
            # with open("original.html", "w", encoding = 'utf-8') as file:
            #     file.write(str(soup))
            updated = replace_words(soup)
            # with open("updated.html", "w", encoding = 'utf-8') as file:
            #     file.write(str(updated))
            resp._content = updated.encode('utf8')
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == 'POST':
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
    app.run(host="127.0.0.1", debug=True, port=8000)
    # gunicorn.app(host="127.0.0.1", debug=True, port=8000)