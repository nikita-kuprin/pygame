import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

FPS = 60

WIDTH = 750
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
enemy = pygame.sprite.Group()
bullets = pygame.sprite.Group()

font_name = pygame.font.match_font('arial')

snd_dir = os.path.join(os.path.dirname(__file__), 'data')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color('White'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, pygame.Color('Green'), fill_rect)
    pygame.draw.rect(surf, pygame.Color('White'), outline_rect, 2)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shield = 100
        self.image = pygame.transform.scale(player_img, (65, 40))
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shooting(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(random.choice(meteor_img), (70, 60))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.radius = int(self.rect.width * .85 / 2)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


def newmob():
    m = Enemy()
    all_sprites.add(m)
    enemy.add(m)


def terminate():
    pygame.quit()
    sys.exit()


background = load_image('background.png')
background_rect = background.get_rect()
player_img = load_image('rocket.png')
meteor_img = []
meteor_name_list = ['meteor1.png', 'meteor2.png']
for img in meteor_name_list:
    meteor_img.append(load_image('{}'.format(img)))
bullet_img = load_image('bullet.png')
screen.blit(background, background_rect)
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_dir, snd)))
pygame.mixer.music.load(os.path.join(snd_dir, 'music.wav'))
pygame.mixer.music.set_volume(0.3)
player = Player()
all_sprites.add(player)
for i in range(10):
    newmob()

score = 0
pygame.mixer.music.play(loops=-1)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shooting()

    all_sprites.draw(screen)
    all_sprites.update()

    hits = pygame.sprite.spritecollide(player, enemy, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 10
        newmob()
        if player.shield <= 0:
            running = False
    screen.fill(pygame.Color("Black"))
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 10, 7, player.shield)
    hits = pygame.sprite.groupcollide(enemy, bullets, True, True)
    for hit in hits:
        score += 50
        random.choice(expl_sounds).play()
        newmob()

    pygame.display.flip()
    clock.tick(FPS)

terminate()
