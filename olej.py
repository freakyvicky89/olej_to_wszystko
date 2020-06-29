import pygame
from pygame import mixer
from pygame.colordict import THECOLORS as COLOR
import os
import youtube_dl
from bs4 import BeautifulSoup as bs
from urllib import request
import tempfile
import feedparser


#########
# SETUP #
#########
pygame.init()
X = 1280
Y = 720
screen = pygame.display.set_mode((X, Y))
pygame.display.set_caption("Olej to wszystko [LOADING]")
font = pygame.font.Font('freesansbold.ttf', 32)


def display_text(text):
    screen.fill((COLOR['darkcyan']))
    loading_images = font.render(text, True, COLOR['lavender'])
    loading_images_rect = loading_images.get_rect()
    loading_images_rect.center = (X // 2, Y // 2)
    screen.blit(loading_images, loading_images_rect)
    pygame.display.flip()
    pygame.event.get()


display_text('LOADING IMAGES...')

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

display_text('LOADING MUSIC...')

if not os.path.exists('./saku.wav'):
    ydl_options = {
        'format': 'bestaudio/best',
        'outtmpl': 'saku.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }]
    }
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download(['https://www.youtube.com/watch?v=7RGf2zYG1vw'])

mixer.init()
mixer.music.load('saku.wav')
mixer.music.set_volume(.8)
mixer.music.play()

screen.fill(COLOR['darkcyan'])
pygame.display.flip()
pygame.event.get()

pygame.display.set_caption("Olej to wszystko")

#############
# MAIN LOOP #
#############
while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    screen.fill(COLOR['darkcyan'])
    pygame.display.flip()
