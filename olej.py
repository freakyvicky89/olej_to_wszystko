import pygame
from bs4 import BeautifulSoup as bs
from urllib import request
import tempfile
import feedparser

pygame.init()
fotos = []
tvn_feed = feedparser.parse('https://tvn24.pl/najnowsze.xml')

for entry in tvn_feed.entries:
    soup = bs(entry.summary)
    temp = tempfile.TemporaryFile()
    image = request.urlopen(soup.find("img")["src"]).read()
    temp.write(image)
    temp.flush()
    temp.seek(0)
    fotos.append(pygame.image.load_extended(temp))
