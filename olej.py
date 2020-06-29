import pygame
from pygame import mixer
from pygame.math import Vector2
from pygame.colordict import THECOLORS as COLOR
import os
from abc import ABC
import random
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
clock = pygame.time.Clock()
max_tps = 20.0
rot_speed = 5.0
delta = 0.0


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


################
# GAME OBJECTS #
################
class GameObject(ABC):

    def __init__(self):
        self.pos = None
        self.vel = None

    def move(self):
        self.pos += self.vel
        if self.pos.x > X:
            self.pos.x -= X
        if self.pos.x < 0:
            self.pos.x += X
        if self.pos.y > Y:
            self.pos.y -= Y
        if self.pos.y < 0:
            self.pos.y += Y


class Cock(GameObject):
    cock = None

    def __init__(self):
        self.pos = Vector2(X / 2, Y / 2)
        self.dir = Vector2(0, -1)
        self.vel = Vector2(0, 0)
        Cock.cock = self

    def up(self):
        self.vel += self.dir

    def down(self):
        self.vel -= self.dir

    def left(self): # TODO not working [debug]
        self.dir.rotate(rot_speed)

    def right(self):
        self.dir.rotate(-rot_speed)


class Rock(GameObject):
    rocks = []

    def __init__(self, pos, vel, size):
        self.pos = pos
        self.vel = vel
        self.size = size
        self.hp = size
        self.foto = random.choice(fotos)
        Rock.rocks.append(self)

    def force(self, force):
        self.vel += force


class GameState(object):
    game = None

    def __init__(self):
        Rock.rocks.clear()
        Cock()
        GameState.game = self


GameState()
#############
# MAIN LOOP #
#############
while True:

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # TICKING
    tick = clock.tick() / 1000.0
    delta += tick
    keys = pygame.key.get_pressed()
    while delta > 1 / max_tps:
        delta -= 1 / max_tps

        if keys[pygame.K_r]:
            GameState()
        if keys[pygame.K_UP]:
            Cock.cock.up()
        if keys[pygame.K_DOWN]:
            Cock.cock.down()
        if keys[pygame.K_LEFT]:
            Cock.cock.left()
        if keys[pygame.K_RIGHT]:
            Cock.cock.right()

        Cock.cock.move()
        for rock in Rock.rocks:
            rock.move()

    # DRAWING
    screen.fill(COLOR['darkcyan'])

    pygame.display.flip()
