import sys
import random
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

pygame.init()
pygame.mixer.init()

# constants
FPS = 60
POWERUP_TIME = 3000
WIDTH = 500
HEIGHT = 600
MOBS = 11
CONTROL = 1
# подготовка игры
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
enemy = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
font_name = pygame.font.match_font('arial')
# директории для открытия файлов
img_dir = os.path.join(os.path.dirname(__file__), 'data')
snd_dir = os.path.join(os.path.dirname(__file__), 'data')


# функции для отрисовки экрана подготовки
def draw_control_text():
    if CONTROL:
        draw_text(screen, "Arrow keys to move, Space to fire", 20, WIDTH / 2, HEIGHT * 3 / 4)
    else:
        draw_text(screen, "[A]-[D] keys to move, Space to fire", 20, WIDTH / 2, HEIGHT * 3 / 4)


def ready_screen():
    draw_text(screen, "GET READY!", 40, WIDTH / 2, HEIGHT / 2)
    draw_control_text()
    pygame.display.update()
    pygame.time.wait(1000)
    screen.fill(pygame.Color('Black'))

    draw_text(screen, "3", 40, WIDTH / 2, HEIGHT / 2)
    draw_control_text()
    pygame.display.update()
    pygame.time.wait(1000)
    screen.fill(pygame.Color('Black'))

    draw_text(screen, "2", 40, WIDTH / 2, HEIGHT / 2)
    draw_control_text()
    pygame.display.update()
    pygame.time.wait(1000)
    screen.fill(pygame.Color('Black'))

    draw_text(screen, "1", 40, WIDTH / 2, HEIGHT / 2)
    draw_control_text()
    pygame.display.update()
    pygame.time.wait(1000)
    screen.fill(pygame.Color('Black'))

    draw_text(screen, "GO!", 40, WIDTH / 2, HEIGHT / 2)
    draw_control_text()
    pygame.display.update()
    pygame.time.wait(1000)
    screen.fill(pygame.Color('Black'))


# главное меню
def show_go_screen():
    screen.blit(menu, menu_rect)
    draw_text_menu(screen, ' Press [LEFT ALT] To Go To Settings ', 20, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text_menu(screen, "   Press [RETURN] To Begin Game   ", 20, WIDTH / 2, HEIGHT * 3 / 4 - 20)
    draw_text_menu(screen, '          Press [Q] To Quit       ', 20, WIDTH / 2, HEIGHT * 3 / 4 - 40)
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
                elif event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_q:
                    terminate()


# функции для отрисовки текста
def draw_text_menu(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color('#FF00FF'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color('#9932CC'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# отрисовка полоски здоровья
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, pygame.Color('Green'), fill_rect)
    pygame.draw.rect(surf, pygame.Color('Black'), outline_rect, 2)


# отрисовка жизней
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# функция для загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


# класс настроек управления и сложности
class Setup(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('setup_menu.ui', self)
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon('setup.png'))
        self.setStyleSheet('background: yellow')

        self.ez.setChecked(True)
        self.control1.setChecked(True)

        self.pushButton.clicked.connect(self.next)

    def next(self):
        global MOBS, CONTROL

        if self.ez.isChecked():
            ex.hide()
            MOBS = 11
        elif self.hard.isChecked():
            ex.hide()
            MOBS = 18
        if self.control1.isChecked():
            ex.hide()
            CONTROL = 1
        elif self.control2.isChecked():
            ex.hide()
            CONTROL = 0


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shield = 100
        self.image = pygame.transform.scale(player_img, (70, 70))
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        # таймер бонуса усиления
        if self.power >= 3 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # если жизнь потеряна
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        # управление кораблем
        if CONTROL:
            if keystate[pygame.K_LEFT]:
                self.speedx = -8
            if keystate[pygame.K_RIGHT]:
                self.speedx = 8
        else:
            if keystate[pygame.K_a]:
                self.speedx = -8
            if keystate[pygame.K_d]:
                self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shooting()

        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    # стрельба
    def shooting(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top)  # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)

    # усиление корабля
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    # при потери жизни
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# класс метеорита
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_img)
        self.image_orig.set_colorkey(pygame.Color('Black'))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 10)
        self.speedx = random.randrange(-3, 3)
        self.radius = int(self.rect.width * .85 / 2)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50:
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


# класс патрона корабля
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


# класс ракеты корабля при power >= 3
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(pygame.Color('Black'))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


# анимация взрывов
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


# класс усилителей
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        if random.random() < .8:
            self.type = random.choice(['shield', 'gun'])
        else:
            self.type = 'live'
        self.image = powerup_images[self.type]
        self.image.set_colorkey(pygame.Color('Black'))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 1

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


# функция созданий новых метеоритов
def newmob():
    m = Enemy()
    all_sprites.add(m)
    enemy.add(m)


def terminate():
    pygame.quit()
    sys.exit()


# загрузка всех ресурсов игры
pygame.display.set_caption("Meteorite Destroyer")
pygame.display.set_icon(load_image('game_icon.png'))

background = load_image('background.png')
background_rect = background.get_rect()
screen.blit(background, background_rect)

menu = load_image('menu.png')
menu_rect = menu.get_rect()

player_image = []
player_name_list = ['rocket.png',
                    'rocket_test.png',
                    'rocket_test1.png']
for img in player_name_list:
    filename = img
    player_image.append(load_image(filename))
player_img = random.choice(player_image)
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(pygame.Color('Black'))

meteor_img = []
meteor_name_list = ['meteorBrown_big1.png',
                    'meteorBrown_big2.png',
                    'meteorBrown_med1.png',
                    'meteorBrown_med3.png',
                    'meteorBrown_small1.png',
                    'meteorBrown_small2.png',
                    'meteorBrown_tiny1.png']
for img in meteor_name_list:
    meteor_img.append(pygame.image.load(os.path.join(img_dir, img)).convert())

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
missile_img = load_image('missile.png')
missile_img = pygame.transform.scale(missile_img, (30, 42))

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
ex = Setup()

score = 0
pygame.mixer.music.play(loops=-1)
game_over = True
running = True

# основной игровой цикл
while running:
    if game_over:
        show_go_screen()
        game_over = False
        screen.fill(pygame.Color('Black'))
        ready_screen()

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

    # если произошло столкновение игрока с метеоритом
    hits = pygame.sprite.spritecollide(player, enemy, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 25 + hit.radius * .6
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
    # если произошло столкновение игрока с усилителем
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 20)
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

    hits = pygame.sprite.groupcollide(enemy, bullets, True, True)
    for hit in hits:
        score += 50 - int(hit.radius * .45)
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        newmob()
        if random.random() > .94:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)

    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 10, 7, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives,
               player_mini_img)

    pygame.display.flip()
    clock.tick(FPS)

terminate()
sys.exit(app.exec())
