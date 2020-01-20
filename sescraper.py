#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import time


# Article Klasse die die zu scrapenden Daten speichert
class Article:
    def __init__(self, headline, link, text_body, source, source_name, author, topic, crawl_date, creation_date):
        self.headline = headline
        self.link = link
        self.text_body = text_body
        self.source = source
        self.source_name = source_name
        self.author = author
        self.topic = topic
        self.crawl_date = crawl_date
        self.creation_date = creation_date

    # Helfer Methode die es später ermöglicht einen JSON String zu erstellen
    # siehe return von 'def get_articles()'
    def serialize(self):
        return {
            'headline': self.headline,
            'textBody': self.text_body,
            'source': self.source,
            'source_name': self.source_name,
            'author': self.author,
            'topic': self.topic,
            'link': self.link,
            'crawl_date': self.crawl_date,
            'creation_date': self.creation_date,
        }


# Sucht sich die eine Liste mit allen Artikel links zusammen
def get_news_links(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    items = soup.find_all('div', class_='element__media')

    links = []
    maxItems = 20
    counter = 0
    for item in items:
        if counter <= maxItems:
            if item.find('a').get('href').startswith('//'):
                links.append("https:" + item.find('a').get('href').strip())
            else: 
                links.append(item.find('a').get('href').strip())
        counter += 1
    return links


# Extrahiert alle notwendigen informationen von einem einzigen Artikel
def scrape(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    [s.extract() for s in soup('script')]  # entfernt alle script tags

    # HEADLINE
    headline = soup.find('h1').string
    #headline = soup.find('div', class_='title').string

    # TOPIC
    topic = ''
    #if len(soup.find_all('div', class_='breadcrumbs')) > 0:
        #topic = soup.find_all('div', class_='breadcrumbs')[0].find_all('a')[1].get('title')
    #topic = soup.find("a", class_="active").get_text()

    # AUTHOR
    author = ''
    if soup.find('meta', itemprop='name'):
        author = soup.find('meta', itemprop='name').get('content')

    # TEXT_BODY
    text_body = soup.find_all('div', 'gl_plugin article')[0].get_text()
    text_body = ' '.join(text_body.split())  # entfernt alle überschüssigen whitespaces und Zeilenumbrüche

    # CREATION_DATE
    creation_date = ''
    #if soup.find('time'):
    #    creation_date = soup.find('time').get('datetime')

    if soup.find('meta', itemprop ='datePublished'):
        creation_date =  soup.find('meta', itemprop ='datePublished').get('content')
    
    # CRAWL_DATE
    crawl_date = datetime.now()


    return Article(headline, link, text_body, 'https://www.se.pl', 'super-express', author, topic, crawl_date, creation_date)


# ************************* Flask web app *************************  #


app = Flask(__name__)


# Hier wird der Pfad(route) angegeben der den scraper arbeiten lässt.

@app.route('/super-express')
def get_articles():
    links = get_news_links('https://www.se.pl/najnowsze/')
    articles = []
    for link in links:
        articles.append(scrape(link))
        time.sleep(.5)
    return jsonify([e.serialize() for e in articles])  # jsonify erzeugt aus einem Objekt einen String im JSON Format


@app.route('/')
def index():
    return "<h1>Hier passiert nichts. Bitte gehe zu 'localhost:5000/super-express</h1>"


# Web Application wird gestartet
if __name__ == '__main__':
    app.run()
