import pygame
from pygame import mixer
from pygame.math import Vector2
from pygame.colordict import THECOLORS as COLOR
import os
from time import sleep
from abc import ABC
import random
from itertools import combinations
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
fg_color = COLOR['lavender']
bg_color = COLOR['darkcyan']
piss_color = COLOR['lightgoldenrod1']
clock = pygame.time.Clock()
max_tps = 20.0
rot_speed = 10.0
delta = 0.0
CENTER = Vector2(X // 2, Y // 2)
ROCK_V = Vector2(X // 4, 0)
COCK_V = Vector2(0, -1)
COCK_L = 50
PISS_SPEED_BOOST = 10
PISS_L = 5


def display_text(text):
    screen.fill((bg_color))
    render = font.render(text, True, fg_color)
    rect = render.get_rect()
    rect.center = CENTER
    screen.blit(render, rect)
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
mixer.music.set_volume(.75)
mixer.music.play(loops=-1)

screen.fill(bg_color)
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


def round_vector(v):
    return int(v.x), int(v.y)


class Piss(GameObject):
    bullets = []

    def __init__(self, pos, vel, vector):
        self.pos = pos
        self.vel = vel + (vector * PISS_SPEED_BOOST)
        self.vector = vector * PISS_L
        Piss.bullets.append(self)

    def draw(self):
        width_vector = self.vector.normalize().rotate(90)
        pygame.draw.polygon(screen, piss_color, (
                            round_vector(self.pos + width_vector),
                            round_vector(self.pos + width_vector * -1),
                            round_vector(self.pos + self.vector * PISS_L + width_vector * -1),
                            round_vector(self.pos + self.vector * PISS_L + width_vector)
                            ))

    def collision_points(self):
        return [round_vector(self.pos), round_vector(self.pos + self.vector)]


class Cock(GameObject):
    cock = None

    def __init__(self):
        self.pos = Vector2(X / 2, Y / 2)
        self.angle = 0
        self.vel = Vector2(0, 0)
        Cock.cock = self

    def up(self):
        self.vel += COCK_V.rotate(self.angle)

    def left(self):
        self.angle -= rot_speed
        if self.angle > 360:
            self.angle -= 360

    def right(self):
        self.angle += rot_speed
        if self.angle < 0:
            self.angle += 360

    def draw(self):
        cock_vector = self.get_cock_vector()
        ball_vector = cock_vector.rotate(90)
        pygame.draw.circle(screen, fg_color, round_vector(self.pos + ball_vector * 10), 15)
        pygame.draw.circle(screen, fg_color, round_vector(self.pos + ball_vector * -10), 15)
        pygame.draw.polygon(screen, fg_color, (
            round_vector(self.pos + ball_vector * 10),
            round_vector(self.pos + ball_vector * -10),
            round_vector(self.pos + cock_vector * COCK_L + ball_vector * -10),
            round_vector(self.pos + cock_vector * COCK_L + ball_vector * 10)
        ))
        pygame.draw.circle(screen, fg_color, round_vector(self.pos + cock_vector * COCK_L), 10)

    def collision_points(self):
        cock_vector = self.get_cock_vector()
        ball_vector = cock_vector.rotate(90)
        return [round_vector(self.pos + ball_vector * 25),
                round_vector(self.pos + ball_vector * -25),
                round_vector(self.pos + cock_vector * (COCK_L + 10))]

    def shoot(self):
        Piss(self.pos + self.get_cock_vector() * (COCK_L + 10), self.vel, self.get_cock_vector())

    def get_cock_vector(self):
        return COCK_V.rotate(self.angle)


class Rock(GameObject):
    rocks = []

    def __init__(self, pos, vel, size):
        self.pos = pos
        self.vel = vel
        self.size = size
        self.hp = size
        self.foto = pygame.transform.scale(
            random.choice(fotos), ((X // 20) * size, (Y // 20) * size))
        self.got_hit = 0
        Rock.rocks.append(self)

    def hit(self, force):
        if self not in Rock.rocks:
            return
        self.hp -= 1
        if self.hp > 0:
            self.vel += force / 4
            self.got_hit = 5
        else:
            if self.size > 1:
                new_vel = self.vel.rotate(90).normalize()
                Rock(self.pos + new_vel, self.vel + (new_vel * self.size), self.size - 1)
                Rock(self.pos - new_vel, self.vel - (new_vel * self.size), self.size - 1)
            Rock.rocks.remove(self)

    def draw(self):
        if self.got_hit == 0:
            screen.blit(self.foto, self.get_rect())
        else:
            pygame.draw.rect(screen, fg_color, self.get_rect())
            self.got_hit -= 1

    def get_rect(self):
        rect = self.foto.get_rect()
        rect.center = self.pos
        return rect


def rock_collisions():
    for pair in combinations(Rock.rocks, 2):
        if pair[0].get_rect().colliderect(pair[1].get_rect()):
            normal = (pair[0].pos - pair[1].pos).normalize()
            pair[0].vel.reflect_ip(normal)
            pair[1].vel.reflect_ip(normal)
            while pair[0].get_rect().colliderect(pair[1].get_rect()):
                pair[0].move()
                pair[1].move()


def piss_collisions():
    for rock in Rock.rocks:
        for piss in Piss.bullets:
            for point in piss.collision_points():
                if rock.get_rect().collidepoint(point):
                    Piss.bullets.remove(piss)
                    rock.hit(piss.vel)
                    break


class GameState(object):
    game = None

    def __init__(self, level):
        self.level = level
        self.lives = 3
        display_text("LEVEL %d" % level)
        sleep(3)
        self.init_level(level)
        GameState.game = self

    def init_level(self, level):
        Rock.rocks.clear()
        Piss.bullets.clear()
        for i in range(level):
            vector = ROCK_V.rotate(i * (360 // level))
            Rock(CENTER + vector, vector.normalize(), 5)
        Cock()

    def death(self):
        self.lives -= 1
        if self.lives > 0:
            display_text("%d LIVES LEFT" % self.lives)
            sleep(3)
            self.init_level(self.level)
        else:
            display_text("GAME OVER :(")
            sleep(3)
            GameState(1)

    def next_level(self):
        GameState(self.level + 1)


GameState(1)
#############
# MAIN LOOP #
#############
while True:

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            Cock.cock.shoot()

    # TICKING
    tick = clock.tick() / 1000.0
    delta += tick
    cock_collision = False
    keys = pygame.key.get_pressed()
    while delta > 1 / max_tps:
        delta -= 1 / max_tps

        if keys[pygame.K_r]:
            GameState(1)
        if keys[pygame.K_UP]:
            Cock.cock.up()
        if keys[pygame.K_LEFT]:
            Cock.cock.left()
        if keys[pygame.K_RIGHT]:
            Cock.cock.right()

        Cock.cock.move()
        for rock in Rock.rocks:
            rock.move()
        for piss in Piss.bullets:
            piss.move()

        piss_collisions()
        rock_collisions()
        for point in Cock.cock.collision_points():
            for rock in Rock.rocks:
                if rock.get_rect().collidepoint(point):
                    cock_collision = True

    if cock_collision:
        GameState.game.death()
        continue

    if len(Rock.rocks) == 0:
        GameState.game.next_level()

    # DRAWING
    screen.fill(bg_color)
    for rock in Rock.rocks:
        rock.draw()
    Cock.cock.draw()
    for piss in Piss.bullets:
        piss.draw()
    pygame.display.flip()
