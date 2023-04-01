from flask import Flask, render_template, request, jsonify
application = app = Flask(name)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient("mongodb+srv://jykdb:jykdb@cluster0.udupui8.mongodb.net/?retryWrites=true&w=majority")
db = client.pirates_lv1

@app.route('/')
def home():
	return render_template("index.html")

@app.route('/detail')
def detail():
    return render_template("detail.html")

@app.route('/exhibit', methods=["POST"])
def post_exhibit():

    url_receive = request.form["url_give"]
        
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('#container > div.wide-inner > section > h3').text
    period = soup.select_one('#container > div.detial-cont-element.active > div > dl:nth-child(1) > dd').text.strip()
    tags = soup.select_one('#container > section.tag-element.poi > p').text.replace('\n',' ')

    image = soup.select('.item')[1]['style'].replace("background-image:url('",'').replace("');",'')
    image = 'https://korean.visitseoul.net'+image
    post_list = list(db.exhibition.find({},{'_id':False}))
    count = len(post_list)+1
    doc = {
            'url': url_receive,
            'title':title,
            'period':period,
            'tags':tags,
            'image':image,
            'count': count
        }   

    db.exhibition.insert_one(doc)
    
    
    return jsonify({"msg": "완료!"})

@app.route('/exhibit', methods=["GET"])
def get_exhibit():
    exhibitions = list(db.exhibition.find({},{'_id':False}))
    return jsonify({"result": exhibitions})

@app.route('/now', methods=["GET"])
def get_now():

    url = 'https://korean.visitseoul.net/exhibition'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    items = soup.select('.item > a')
    base = 'https://korean.visitseoul.net'

    docs = []
    for item in items:
        url = base+item['href']
        image = base+item.select_one('.thumb')['style'].split('(')[1].replace(')','')
        title = item.select_one('.title').text
        period = item.select_one('.small-text.text-dot-d').text.strip()
        doc = {
            'url':url,
            'image':image,
            'title':title,
            'period':period
        }
        docs.append(doc)
        
    return jsonify({"now": docs})

@app.route('/list', methods=["GET"])
def get_list():

    url = 'https://designcompass.org/'

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    items = soup.select('div > div.wp-block-ultimate-post-post-grid-1.ultp-block-1dc2c2 > div > div.ultp-block-items-wrap.ultp-block-row.ultp-pg1a-style1.ultp-block-column-4.ultp-layout1 > .ultp-block-item')
    docs = []
    for item in items:
        url_elem = item.select_one(' div > div.ultp-block-image.ultp-block-image-opacity > a')
        if url_elem is not None:
            url = url_elem['href']
            imga = item.select_one('.jetpack-lazy-image')['src']
            title = item.select_one('.ultp-block-title > a').text.strip()
            deco = item.select_one('.ultp-block-excerpt > p').text.strip()
            doc = {
                    'url':url,
                    'imga':imga,
                    'title':title,
                    'deco':deco
            }
            docs.append(doc)
    return jsonify({"list": docs})

@app.route('/detail/<int:id>', methods=["GET"])
def details(id):
    exhibition = db.exhibition.find_one({'count': id}, {'_id': False})
    return jsonify({"result": exhibition})


if __name__ == "__main__":
	app.run()