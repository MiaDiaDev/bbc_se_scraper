#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timezone
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
    soup = BeautifulSoup(requests.get(url).content, 'xml')
    items = soup.find_all('link')

    links = []
    maxItems = 20
    counter = 0
    for item in items:
        itemText = item.get_text()
        if counter <= maxItems:
            if not itemText.endswith('/'):
                links.append(itemText)
            else: continue
            counter += 1
    
    return links


# Extrahiert alle notwendigen informationen von einem einzigen Artikel
def scrape(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    [s.extract() for s in soup('script')]  # entfernt alle script tags

    # HEADLINE
    headline = soup.find('h1').string

    # TOPIC
    topic = ''
    if soup.find("a", class_="navigation-wide-list__link navigation-arrow--open"):
        menuActive = soup.find("a", class_="navigation-wide-list__link navigation-arrow--open")
        topic = menuActive.find("span").get_text()

    # AUTHOR
    author = ''
    if soup.find('span', class_='byline__name'):
        author = soup.find('span', class_='byline__name').get_text()

    # TEXT_BODY
    if soup.find('div', class_='story-body__inner'):
        innerArticle = soup.find('div', class_='story-body__inner')
    elif soup.find('div', class_='vxp-media__summary'): 
        innerArticle = soup.find('div', class_='vxp-media__summary')
    else: 
        print ("no content found on" + link)
        return 
        
    pList = innerArticle.find_all('p')

    text_body = ''
    for p in pList:
        text_body += p.get_text() + ' '

    # CREATION_DATE
    creation_date = ''

    #soup.find('div', class_='date date--v2 relative-time').get('data-datetime')
    if soup.find('div', class_='date date--v2 relative-time'):
        timeStamp = soup.find('div', class_='date date--v2 relative-time').get('data-seconds')
        creation_date = datetime.fromtimestamp(timeStamp, timezone.utc)
        #creation_date = datetime.fromtimestamp(timeStamp).strftime("%A, %B %d, %Y %I:%M:%S")

    # CRAWL_DATE
    crawl_date = datetime.now()

    return Article(headline, link, text_body, 'https://www.bbc.com', 'bbc', author, topic, crawl_date, creation_date)


# ************************* Flask web app *************************  #


app = Flask(__name__)


# Hier wird der Pfad(route) angegeben der den scraper arbeiten lässt.

@app.route('/bbc')
def get_articles():
    links = get_news_links('http://feeds.bbci.co.uk/news/rss.xml')
    articles = []
    for link in links:
        if scrape(link):
            articles.append(scrape(link))
        time.sleep(.5)
    return jsonify([e.serialize() for e in articles])  # jsonify erzeugt aus einem Objekt einen String im JSON Format


@app.route('/')
def index():
    return "<h1>Hier passiert nichts. Bitte gehe zu 'localhost:5000/bbc</h1>"


# Web Application wird gestartet
if __name__ == '__main__':
    app.run()
