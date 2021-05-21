import re
from flask import Flask,request,redirect,Response
import requests

from bs4 import BeautifulSoup as bs
app = Flask(__name__)


LOCAL_NAME = 'http://localhost:8000'
SITE_NAME = 'http://en.wikipedia.org'

@app.route('/')
def index():
    return 'root'





def replace_words(soup):
    # page = soup.find('body').getText()
    exp = re.compile(r"\b\w{5}\b")
    if soup.find('body'):
        page = soup.body.find_all(text = exp)
        print(len(page))
        print(count_text(exp, soup.text))
        for i, line in enumerate(page):
            # print(line)
            # words = re.findall(exp, line)
            words = re.sub(exp, "VURP!", line)
            # for word in words:
            #     replaced_word = line.replace(word, "VURP!")
            # line.replace_with(replaced_word)
            line.replace_with(words)
            # print(line)
            # print(page[i])
        print(soup.text.count("VURP!"))
    return soup

import operator
from functools import reduce


def count_text(exp, obj):
    count = reduce(operator.add, (1 for _ in re.finditer(exp, obj)))
    return count



@app.route('/<path:path>', methods=['GET', 'POST', "DELETE"])
def proxy(path):
    global SITE_NAME
    if request.method == 'GET':
        resp = requests.get(f'{SITE_NAME}/{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
        soup = bs(resp.content)
        with open("original.html", "w", encoding = 'utf-8') as file:
            file.write(str(soup))
        updated = replace_words(soup)
        with open("updated.html", "w", encoding = 'utf-8') as file:
            file.write(str(updated))
        resp._content = updated.encode('utf8')


        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='POST':
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