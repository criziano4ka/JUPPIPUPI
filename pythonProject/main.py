import os
import sys

import pygame
import pygame_gui
import pygame_menu
from pygame_gui.core import ObjectID


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.collided_monster = None
        self.image = None
        self.idle_anim_l = None
        self.idle_anim_r = None
        self.jump_l = None
        self.jump_r = None
        self.run_l = None
        self.run_r = None
        self.load_run_r()
        self.load_run_l(self.run_r)

        self.load_jump_r()
        self.load_jump_l(self.jump_r)

        self.load_idle_animation_r()
        self.load_idle_animation_l(self.idle_anim_r)

        self.player_r = load_image('char.png')
        self.player_l = pygame.transform.flip(self.player_r, True, False)
        self.rect = self.player_r.get_rect()
        self.rect.y = 500
        self.rect.x = WIDTH / 5 + 1
        self.player_last_x = self.rect.x
        self.high_of_jump = 25

        self.walk_r = False
        self.walk_l = False
        self.jump_bool = False
        self.fall_bool = False

        self.VELOCITY = 10
        self.HEALTH = 3

        self.cur_char_frame = 0
        self.idle_frame = 0
        self.jump_ind = 0

        self.right = True

        self.push_l = False
        self.push_r = False
        self.push_distance = 15
        self.WIN = False

    def update(self, cur_frame, scroll):
        global dir, change_lvl, WIN, LOSE
        if cur_frame % 5 == 0:
            self.idle_frame += 1
        if self.idle_frame == len(self.idle_anim_r):
            self.idle_frame = 0
        if self.right:
            self.image = self.idle_anim_r[self.idle_frame]
        else:
            self.image = self.idle_anim_l[self.idle_frame]

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.walk_l = True
                    self.right = False
                elif event.key == pygame.K_d:
                    self.walk_r = True
                    self.right = True
                elif event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    if self.jump_ind == 0:
                        self.jump_bool = True
                if event.key == pygame.K_LSHIFT:
                    self.VELOCITY = 20
                if event.key == pygame.K_ESCAPE:
                    menu.enable()
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == settings:
                    if menu.is_enabled():
                        menu.disable()
                    else:
                        menu.enable()
                elif event.ui_element == retry:
                    change_lvl = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.walk_l = False
                elif event.key == pygame.K_d:
                    self.walk_r = False
                elif event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    self.jump_bool = False
                    self.fall_bool = True
                if event.key == pygame.K_LSHIFT:
                    self.VELOCITY = 10
            manager.process_events(event)
        if not self.push_l and not self.push_r:
            if self.walk_r:
                self.rect.move_ip(self.VELOCITY, 0)
                self.image = self.run_r[self.cur_char_frame]

                d = 4
                if running:
                    d = 1
                if cur_frame % d == 0:
                    self.cur_char_frame += 1

                if self.cur_char_frame == len(self.run_r):
                    self.cur_char_frame = 0
            elif self.walk_l:
                self.rect.move_ip(-self.VELOCITY, 0)
                self.image = self.run_l[self.cur_char_frame]

                d = 4
                if running:
                    d = 1
                if cur_frame % d == 0:
                    self.cur_char_frame += 1

                if self.cur_char_frame == len(self.run_l):
                    self.cur_char_frame = 0
            if self.jump_bool and self.jump_ind <= self.high_of_jump:
                self.rect.move_ip(0, -10)
                if self.right:
                    self.image = self.jump_r[0]
                else:
                    self.image = self.jump_l[0]
                self.jump_ind += 1
            elif self.fall_bool and self.jump_ind != 0:
                self.rect.move_ip(0, 10)
                if self.right:
                    self.image = self.jump_r[1]
                else:
                    self.image = self.jump_l[1]
                self.jump_ind -= 1
            if self.jump_ind == self.high_of_jump:
                self.jump_bool = False
                self.fall_bool = True
            elif self.jump_ind == 0:
                self.fall_bool = False
        else:
            if self.push_r:
                if self.push_distance > 15:
                    self.rect.move_ip(10, -7)
                else:
                    self.rect.move_ip(10, 7)
            else:
                if self.push_distance > 15:
                    self.rect.move_ip(-10, -7)
                else:
                    self.rect.move_ip(-10, 7)
            self.push_distance -= 1
            if self.push_distance == 0:
                self.push_l = False
                self.push_r = False

        if not (self.push_r or self.push_l):
            self.collided_monster = pygame.sprite.spritecollide(player, monsters, False,
                                                                collided=pygame.sprite.collide_mask)
            if len(self.collided_monster) > 0:
                self.push_distance = 30
                self.HEALTH -= 1
                if self.collided_monster[0].m_right:
                    self.push_r = True
                else:
                    self.push_l = True

        if self.rect.y >= 1000:
            self.HEALTH = 0

        if self.HEALTH == 0:
            LOSE = True

        self.collide_coin = pygame.sprite.spritecollide(player, win, False,
                                                        collided=pygame.sprite.collide_mask)
        if len(self.collide_coin) > 0:
            menu_win.enable()
            WIN = True

        blocks = self.find_near_blocks()

        collided_blocks = pygame.sprite.spritecollide(player, blocks, False,
                                                      collided=pygame.sprite.collide_mask)

        if not self.push_r and not self.push_l:
            if len(collided_blocks) == 0:
                if not self.jump_bool and not self.fall_bool:
                    if self.right:
                        self.image = self.jump_r[1]
                    else:
                        self.image = self.jump_l[1]
                    player.rect.move_ip(0, 20)
                    self.jump_ind = 0

            collided_blocks = pygame.sprite.spritecollide(player, blocks, False,
                                                          collided=pygame.sprite.collide_mask)
            if len(collided_blocks) > 0:
                if collided_blocks[0].name == 'Dirt.png':
                    if self.walk_r:
                        dir = -1
                        self.rect.move_ip(-10, 0)
                    elif self.walk_l:
                        dir = 1

                    done = False
                    while dir and not done:
                        self.rect.move_ip(dir, 0)
                        done = pygame.sprite.collide_mask(player, collided_blocks[0]) is None
                else:
                    done = False
                    while not done:
                        player.rect.move_ip(0, -1)
                        done = all(list(map(lambda x: pygame.sprite.collide_mask(player, x) is None, collided_blocks)))
                    player.rect.move_ip(0, 10)

        self.rect.move_ip(-scroll, 0)

    def find_near_blocks(self):
        return list(filter(lambda block: abs(block.rect.x - self.rect.x < 100) or abs(block.rect.y - self.rect.y < 100),
                           all_blocks))

    def load_run_r(self):
        lst = []
        coords = [(0, 3, 65, 74), (86, 3, 150, 76), (170, 3, 235, 77), (255, 2, 320, 77), (340, 1, 405, 77),
                  (425, 0, 490, 77), (510, 1, 576, 77), (596, 1, 677, 77), (697, 3, 784, 74), (805, 3, 901, 74),
                  (63, 103, 162, 176), (182, 102, 277, 177), (297, 101, 385, 177), (405, 100, 483, 177),
                  (503, 99, 569, 177), (589, 100, 654, 177), (674, 101, 739, 176), (759, 102, 824, 172)]
        fullname = os.path.join('data', 'run_r.png')
        anim = pygame.image.load(fullname)
        coords = list(map(lambda x: (x[0], x[1], x[2] - x[0], x[3] - x[1]), coords))
        for i in range(len(coords)):
            img = anim.subsurface(pygame.Rect(coords[i][0], coords[i][1], coords[i][2], coords[i][3]))
            img = img.convert_alpha()
            lst.append(img)
        self.run_r = lst

    def load_run_l(self, anim):
        anim = list(map(lambda x: pygame.transform.flip(x, True, False), anim))
        self.run_l = anim

    def load_jump_r(self):
        lst = []
        coords = [(37, 25, 112, 102), (152, 25, 218, 102)]
        fullname = os.path.join('data', 'jump.png')
        anim = pygame.image.load(fullname)
        coords = list(map(lambda x: (x[0], x[1], x[2] - x[0], x[3] - x[1]), coords))
        for i in range(len(coords)):
            img = anim.subsurface(pygame.Rect(coords[i][0], coords[i][1], coords[i][2], coords[i][3]))
            img = img.convert_alpha()
            lst.append(img)
        self.jump_r = lst

    def load_jump_l(self, lst):
        lst = list(map(lambda x: pygame.transform.flip(x, True, False), lst))
        self.jump_l = lst

    def load_idle_animation_r(self):
        lst = []
        coords = [(28, 29, 100, 101), (110, 28, 181, 101), (191, 28, 262, 101), (272, 27, 344, 101),
                  (354, 27, 425, 101),
                  (435, 26, 506, 101), (517, 26, 588, 101), (598, 27, 669, 101), (679, 27, 751, 101),
                  (761, 28, 832, 101),
                  (842, 28, 913, 101), (923, 29, 995, 101)]
        fullname = os.path.join('data', 'idle.png')
        anim = pygame.image.load(fullname)
        coords = list(map(lambda x: (x[0], x[1], x[2] - x[0], x[3] - x[1]), coords))
        for i in range(len(coords)):
            img = anim.subsurface(pygame.Rect(coords[i][0], coords[i][1], coords[i][2], coords[i][3]))
            img = img.convert_alpha()
            lst.append(img)
        self.idle_anim_r = lst

    def load_idle_animation_l(self, lst):
        lst = list(map(lambda x: pygame.transform.flip(x, True, False), lst))
        self.idle_anim_l = lst

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_push(self):
        if self.push_r or self.push_l:
            return False
        return True


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.monster_walk_r = None
        self.monster_walk_l = None
        self.monster_idle_r = None
        self.monster_idle_l = None
        self.monster = load_image('monster.png')
        self.rect = self.monster.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

        self.load_monster_idle_l()
        self.load_monster_idle_r(self.monster_idle_l)

        self.load_monster_walk_l()
        self.load_monster_walk_r(self.monster_walk_l)

        self.M_VELOCITY = 7

        self.m_idle_frame = 0
        self.m_cur_char_frame = 0

        self.m_right = False

        self.image = None

    def update(self, current_frame, x, y, move, scroll):

        if current_frame % 5 == 0:
            self.m_idle_frame += 1

        if self.m_idle_frame == len(self.monster_idle_l):
            self.m_idle_frame = 0
        if self.m_right:
            self.image = self.monster_idle_r[self.m_idle_frame]
        else:
            self.image = self.monster_idle_l[self.m_idle_frame]

        if move:
            if self.rect.x > x:
                if self.rect.x - x <= FOLLOW_RANGE:
                    if self.rect.y > y:
                        if self.rect.y - y <= FOLLOW_RANGE:
                            self.rect.move_ip(-self.M_VELOCITY, 0)
                            self.image = self.monster_walk_l[self.m_cur_char_frame]
                            self.m_right = False
                            self.rect.move_ip(0, -self.M_VELOCITY)
                    else:
                        if y - self.rect.y <= FOLLOW_RANGE:
                            self.image = self.monster_walk_l[self.m_cur_char_frame]
                            self.m_right = False
                            self.rect.move_ip(-self.M_VELOCITY, 0)
                            self.rect.move_ip(0, self.M_VELOCITY)
            else:
                if x - self.rect.x <= FOLLOW_RANGE:
                    if self.rect.y > y:
                        if self.rect.y - y <= FOLLOW_RANGE:
                            self.rect.move_ip(self.M_VELOCITY, 0)
                            self.m_right = True
                            self.image = self.monster_walk_r[self.m_cur_char_frame]
                            self.rect.move_ip(0, -self.M_VELOCITY)
                    else:
                        if y - self.rect.y <= FOLLOW_RANGE:
                            self.rect.move_ip(self.M_VELOCITY, 0)
                            self.image = self.monster_walk_r[self.m_cur_char_frame]
                            self.m_right = True
                            self.rect.move_ip(0, self.M_VELOCITY)

        if current_frame % 3 == 0:
            self.m_cur_char_frame += 1

        if self.m_cur_char_frame == len(self.monster_walk_l):
            self.m_cur_char_frame = 0

        self.rect.move_ip(-scroll, 0)

    def load_monster_idle_l(self):
        ret = []
        fullname = os.path.join('data', 'idle')
        lst = os.listdir(fullname)
        for i in range(len(lst)):
            ret.append(pygame.image.load(os.path.join(fullname, lst[i])))
        self.monster_idle_l = ret

    def load_monster_idle_r(self, lst):
        lst = list(map(lambda x: pygame.transform.flip(x, True, False), lst))
        self.monster_idle_r = lst

    def load_monster_walk_l(self):
        ret = []
        fullname = os.path.join('data', 'walk')
        lst = os.listdir(fullname)
        for i in range(len(lst)):
            ret.append(pygame.image.load(os.path.join(fullname, lst[i])))
        self.monster_walk_l = ret

    def load_monster_walk_r(self, lst):
        lst = list(map(lambda x: pygame.transform.flip(x, True, False), lst))
        self.monster_walk_r = lst


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.move_ip(-scroll, 0)


class Block(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.width = self.height = 128
        self.name = name
        self.image = tiles[name]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.move_ip(-scroll, 0)


def load_all_tiles():
    ret = []
    fullname = os.path.join('data', 'tiles')
    lst = os.listdir(fullname)
    for i in range(len(lst)):
        ret.append(pygame.image.load(os.path.join(fullname, lst[i])))
    return [ret, lst]


def load_coin():
    fullname = os.path.join('data', 'coin.png')
    img = pygame.image.load(fullname)
    return img


def set_up_gui():
    rect = pygame.Rect((10, 10, 85, 85), )
    settings = pygame_gui.elements.UIButton(relative_rect=rect, text='', manager=manager,
                                            object_id=ObjectID(class_id='@buttons', object_id='#settings_button'))

    rect = pygame.Rect((1830, 10, 85, 85), )
    retry = pygame_gui.elements.UIButton(relative_rect=rect, text='', manager=manager,
                                         object_id=ObjectID(class_id='@buttons', object_id='#retry_button'))

    rect = pygame.Rect((200, 10, 160, 85), )
    hp = pygame_gui.elements.UIButton(relative_rect=rect, text='', manager=manager,
                                      object_id=ObjectID(class_id='@buttons', object_id='#hp'))

    return settings, retry


def set_up_background():
    background = load_image('background.png')
    return background


def load_lvl(name):
    legend = {'d': 'Dirt.png',
              'g': 'GrassMid.png',
              'u': 'GrassHillLeft.png',
              'y': 'GrassHillLeft2.png',
              'h': 'GrassHillRight.png',
              'm': 'GrassHillRight2.png',
              'c': 'coin',
              'M': 'Monster'}
    name = str(name) + 'lvl.txt'
    lvl = open(os.path.join('data', name)).readlines()
    for y in range(len(lvl)):
        for x in range(len(lvl[y])):
            if lvl[y][x] == 'M':
                y1 = (9 - len(lvl) + y) * 128
                x1 = x * 128
                a = Monster(x1, y1)
                monsters.add(a)
            elif lvl[y][x] == 'c':
                y1 = (9 - len(lvl) + y) * 128
                x1 = x * 128
                a = Coin(x1, y1)
                win.add(a)
            elif lvl[y][x] != ' ' and lvl[y][x] != '\n':
                y1 = (9 - len(lvl) + y) * 128
                x1 = x * 128
                block = Block(legend[lvl[y][x]], x1, y1)
                all_blocks.add(block)

    return lvl


def start_the_game():
    menu.disable()
    lose.disable()
    menu_win.disable()


def level_menu():
    menu._open(level)


def retry_lvl():
    global change_lvl
    change_lvl = True
    lose.disable()
    menu_win.disable()


def choose_lvl(value, lvl):
    global LEVEL, change_lvl
    LEVEL = lvl
    change_lvl = True


def menu_update():
    if menu.is_enabled():
        menu.update(pygame.event.get())
        if menu.is_enabled():
            menu.draw(screen)
            pygame.time.delay(1)


def lose_update():
    if LOSE:
        lose.enable()
        lose.update(pygame.event.get())
        if lose.is_enabled():
            lose.draw(screen)
            pygame.time.delay(1)


def win_update():
    if WIN:
        menu_win.update(pygame.event.get())
        if menu_win.is_enabled():
            menu_win.draw(screen)
            pygame.time.delay(1)


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()

    size_scr = WIDTH, HEIGHT = 1920, 1080

    coin = load_coin()

    dir = 1
    LEVEL = 1
    FPS = 144
    timer = pygame.time.Clock()
    count = 0

    screen = pygame.display.set_mode(size_scr)
    manager = pygame_gui.UIManager(size_scr, 'data/theme.json')

    running = True

    FOLLOW_RANGE = 400

    all_sprtes = pygame.sprite.Group()

    tiles = dict()
    all_tiles_image = load_all_tiles()[0]
    all_tiles_names = load_all_tiles()[1]

    for i in range(len(all_tiles_names)):
        tiles[all_tiles_names[i]] = all_tiles_image[i]

    all_blocks = pygame.sprite.Group()

    change_lvl = True

    player = Player()
    all_sprtes.add(player)

    monsters = pygame.sprite.Group()
    win = pygame.sprite.Group()

    background = set_up_background()
    background_r = background.get_rect()

    scroll = 0
    WIN = False
    LOSE = False
    bg_scroll = 0

    # Menu
    menu = pygame_menu.Menu('Juppipupi', 400, 300, theme=pygame_menu.themes.THEME_GREEN)
    menu_win = pygame_menu.Menu('WIN', 1000, 300, theme=pygame_menu.themes.THEME_SOLARIZED)
    lose = pygame_menu.Menu('Lose', 1000, 500, theme=pygame_menu.themes.THEME_ORANGE)

    menu.add.button('Start', start_the_game)
    menu.add.button('Levels', level_menu)

    level = pygame_menu.Menu('Select a Level', 600, 400, theme=pygame_menu.themes.THEME_GREEN)
    level.add.selector('Level :', [('1', 1), ('2', 2), ('3', 3)], onchange=choose_lvl)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    menu.mainloop(screen)

    lose.add.button('Retry', retry_lvl)
    lose.add.button('Quit', pygame_menu.events.EXIT)

    menu_win.add.button('Retry', retry_lvl)
    menu_win.add.button('Quit', pygame_menu.events.EXIT)

    settings, retry = set_up_gui()

    f1 = pygame.font.SysFont('arial', 36)

    while running:
        count += 1
        screen.fill((0, 0, 0))
        text = f1.render(f'{player.HEALTH} hp', True, (220, 220, 220))

        if change_lvl:
            player.push_r = False
            player.push_l = False
            player.walk_r = False
            player.walk_l = False
            if LEVEL == 3:
                player.HEALTH = 5
            else:
                player.HEALTH = 3
            all_blocks.empty()
            win.empty()
            monsters.empty()
            load_lvl(LEVEL)
            change_lvl = False
            dir = 1
            player.rect.x = WIDTH / 5 + 200
            player.rect.y = 500
            WIN = False
            menu_win.disable()
            LOSE = False
            lose.disable()

        if WIN:
            menu_win.enable()
        elif LOSE:
            lose.enable()

        else:
            monsters.update(count, player.get_x(), player.get_y(), player.get_push(), scroll)
            player.update(count, scroll)
            all_blocks.update()
            win.update()

            if player.rect.x > WIDTH / 5 * 4:
                scroll = player.rect.x - WIDTH / 5 * 4
                bg_scroll += scroll - 5
            elif player.rect.x < WIDTH / 5:
                scroll = player.rect.x - WIDTH / 5
                bg_scroll += scroll + 5
            else:
                scroll = 0

            if bg_scroll < -WIDTH:
                bg_scroll += WIDTH
            elif bg_scroll > WIDTH:
                bg_scroll -= WIDTH

            bg_r = background_r.move(-bg_scroll, 0)
            bg2_r = bg_r.move(background.get_width(), 0)
            bg3_r = bg_r.move(-background.get_width(), 0)

            screen.blit(background, bg_r)
            screen.blit(background, bg2_r)
            screen.blit(background, bg3_r)

            time_delta = timer.tick(FPS) / 1000
            manager.update(time_delta)
            all_blocks.draw(screen)
            win.draw(screen)
            monsters.draw(screen)
            all_sprtes.draw(screen)

        manager.draw_ui(screen)
        screen.blit(text, (250, 30))
        menu_update()
        win_update()
        lose_update()
        pygame.display.update()
