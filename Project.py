import pygame
import sys
import random
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

pygame.init()
pygame.mixer.init()

FPS = 60
POWERUP_TIME = 5000
WIDTH = 500
HEIGHT = 600
MOBS = 5
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
enemy = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

font_name = pygame.font.match_font('arial')

snd_dir = os.path.join(os.path.dirname(__file__), 'data')


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "GAME!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, 'Press left shift to go to settings', 20, WIDTH / 2, HEIGHT * 3 / 4 - 22)
    draw_text(screen, "Press any other key to begin", 20, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LALT:
                    ex.show()
            elif event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                try:
                    if event.key != pygame.K_LALT:
                        waiting = False
                except AttributeError:
                    waiting = False


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


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('setup_menu.ui', self)
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon('setup.png'))
        self.ez.setChecked(True)

        self.pushButton.clicked.connect(self.next)

    def next(self):
        global MOBS
        if self.ez.isChecked():
            ex.hide()
            MOBS = 9
        elif self.hard.isChecked():
            ex.hide()
            MOBS = 18


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
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shooting()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shooting(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(random.choice(meteor_img),
                                            (random.randrange(46, 70), random.randrange(40, 65)))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 10)
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


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'live'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(pygame.Color('Black'))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
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
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(pygame.Color('Black'))
meteor_img = []
meteor_name_list = ['meteor1.png', 'meteor2.png']
for img in meteor_name_list:
    meteor_img.append(load_image('{}'.format(img)))
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = load_image(filename)
    img.set_colorkey(pygame.Color('Black'))
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = load_image(filename)
    img.set_colorkey(pygame.Color('Black'))
    explosion_anim['player'].append(img)
bullet_img = load_image('bullet.png')
screen.blit(background, background_rect)

shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
clash_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'clash.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_dir, snd)))
pygame.mixer.music.load(os.path.join(snd_dir, 'music.wav'))
pygame.mixer.music.set_volume(0.3)
powerup_images = {}
shield_img = load_image('shield_up.png')
shield_img = pygame.transform.scale(shield_img, (24, 40))
powerup_images['shield'] = shield_img
gun_img = load_image('gun_up.png')
gun_img = pygame.transform.scale(gun_img, (24, 40))
powerup_images['gun'] = gun_img
live_png = load_image('live.png')
live_png = pygame.transform.scale(live_png, (24, 40))
powerup_images['live'] = live_png
player = Player()
all_sprites.add(player)
app = QApplication(sys.argv)
ex = MyWidget()

score = 0
pygame.mixer.music.play(loops=-1)
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(MOBS):
            newmob()
        score = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.draw(screen)
    all_sprites.update()

    hits = pygame.sprite.spritecollide(player, enemy, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 36 + hit.radius * .6
        clash_sound.play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
        if hit.type == 'live':
            if player.lives >= 3:
                player.lives = 3
            else:
                player.lives += 1
    if player.lives == 0 and not death_explosion.alive():
        game_over = True
    screen.fill(pygame.Color("Black"))
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 10, 7, player.shield)
    hits = pygame.sprite.groupcollide(enemy, bullets, True, True)
    for hit in hits:
        score += 50 - int(hit.radius * .45)
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        newmob()
        if random.random() > .97:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
    draw_lives(screen, WIDTH - 100, 5, player.lives,
               player_mini_img)
    pygame.display.flip()
    clock.tick(FPS)

terminate()
sys.exit(app.exec())
