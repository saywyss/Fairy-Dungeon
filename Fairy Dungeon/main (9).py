import pygame
import time

pygame.init()
screen = pygame.display.set_mode((707, 707))
pygame.display.set_caption("Fairy Dungeon")

background = pygame.image.load("background.PNG")
mw = pygame.transform.scale(background, (1024, 1024))

main_menu = pygame.image.load("menuu.png")

enemy_images = [
    "enemy1.jpeg",
    "enemy2.jpeg", 
    "enemy3.jpeg", 
    "enemy4.jpeg", 
    "enemy5.jpeg", 
    "enemy6.jpeg", 
    "enemy7.jpeg",

]

projectiles = []  # список всех снарядов
enemy_hits = {}  # враг: количество попаданий

original_width, original_height = background.get_size()
scale_factor = 0.69
new_width = int(1024 * 0.69)
new_height = int(1024 * 0.69)

resized_background = pygame.transform.scale(background, (new_width, new_height))

font = pygame.font.SysFont("arial", 36)

class Area:
    def __init__(self, x=0, y=0, w=100, h=200, color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.fill_color = background
        if color:
            self.fill_color = color

    def color(self, color):
        self.fill_color = color

    def fill(self):
        pygame.draw.rect(self.fill_color, self.rect)

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

class Picture(Area):
    def __init__(self, filename, x, y, w, h):
        Area.__init__(self, x, y, w, h, color=None)
        self.image = pygame.image.load(filename)

    def draw(self):
        mw.blit(self.image, (self.rect.x, self.rect.y))

# Новый класс Portal для портала
class Portal:
    def __init__(self, x, y, width, height, image_filename):
        self.rect = pygame.Rect(x, y, width, height)
        image = pygame.image.load(image_filename)
        self.image = pygame.transform.scale(image, (width, height))

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def get_rect(self):
        return self.rect

clock = pygame.time.Clock()

class Hero(pygame.sprite.Sprite):
    def __init__(self, img: str, health: int, strength: int, speed: int, height: int, width: int, x: int, y: int):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(img), (height, width))

        self.rect = self.image.get_rect()
        self.size = height, width

        self.img = img
        self.health = health
        self.strength = strength
        self.speed = speed
        self.height = height
        self.width = width
        self.x = x
        self.y = y

class Player(Hero):
    def __init__(self, img, health, strength, speed, height, width, x, y):
        super().__init__(img, health, strength, speed, height, width, x, y)
        self.last_dir = "right"
        self.shoot_direction = "right"
        self.last_shot_time = 0
        self.last_hit_time = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys, walls):
        if keys[pygame.K_a]:
            new_rect = self.get_rect().move(-self.speed, 0)
            if not any(new_rect.colliderect(wall.get_rect()) for wall in walls):
                self.x -= self.speed
                self.last_dir = "left"
                self.shoot_direction = "left"
        if keys[pygame.K_d]:
            new_rect = self.get_rect().move(self.speed, 0)
            if not any(new_rect.colliderect(wall.get_rect()) for wall in walls):
                self.x += self.speed
                self.last_dir = "right"
                self.shoot_direction = "right"
        if keys[pygame.K_w]:
            new_rect = self.get_rect().move(0, -self.speed)
            if not any(new_rect.colliderect(wall.get_rect()) for wall in walls):
                if not any(new_rect.colliderect(wall.get_rect()) for wall in walls):
                    self.y -= self.speed
                    self.last_dir = "up"
                    self.shoot_direction = "up"
        if keys[pygame.K_s]:
            new_rect = self.get_rect().move(0, self.speed)
            if not any(new_rect.colliderect(wall.get_rect()) for wall in walls):
                self.y += self.speed
                self.last_dir = "down"
                self.shoot_direction = "down"

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        hp_text = font.render(f"HP: {self.health}", True, (255, 255, 255))
        screen.blit(hp_text, (10, 10))

class Projectile:
    def __init__(self, x, y, direction="right", speed=8):
        self.rect = pygame.Rect(x, y, 6, 6)
        self.speed = speed
        self.direction = direction

    def move(self):
        if self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)

player = Player(img="hero.png", health=100, strength=10, speed=5, height=25, width=25, x=50, y=50)

class Enemy(Hero):
    def __init__(self, img, health: int, strength: int, speed: int, height: int, width: int, x: int, y: int, dx=1, dy=0, range_x=100, range_y=0):
        super().__init__(img, health, strength, speed, height, width, x, y)

        self.animation_index = 0
        self.animation_speed = 30
        self.animation_timer = self.animation_speed

        self.start_x = x
        self.start_y = y
        self.dx = dx
        self.dy = dy
        self.range_x = range_x
        self.range_y = range_y

    def update(self):

        if self.animation_timer > 0:
            self.animation_timer -= 1
        else:
            self.animation_timer = self.animation_speed
            self.animation_index = (self.animation_index + 1) % len(enemy_images)
            self.image = pygame.transform.scale(pygame.image.load(enemy_images[self.animation_index]), self.size)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, walls):
        new_x = self.x + self.dx * self.speed
        new_y = self.y + self.dy * self.speed
        new_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        collision = False
        for wall in walls:
            if new_rect.colliderect(wall.get_rect()):
                collision = True
                break

        if collision:
            self.dx *= -1
            self.dy *= -1
        else:
            self.x = new_x
            self.y = new_y

        if abs(self.x - self.start_x) >= self.range_x:
            self.dx *= -1
        if abs(self.y - self.start_y) >= self.range_y:
            self.dy *= -1

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        self.update()

enemies = [
    Enemy("enemy1.jpeg", 100, 10, 2, 26, 26, 200, 215, dx=1, dy=0, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 300, 40, dx=1, dy=1, range_y=100),
    Enemy("enemy1.jpeg", 100, 10, 2, 26, 26, 480, 530, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 132, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 60, 176, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 220, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 60, 264, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 308, dx=1, dy=1, range_x=100),

    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 440, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 440, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 506, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 506, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 572, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 572, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 616, dx=1, dy=1, range_x=100),
    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 616, dx=1, dy=1, range_x=100)
]
enemy = Enemy(img="enemy1.jpeg", health=100, strength=10, speed=5, height=26, width=26, x=100, y=100)

class Wall:
    def __init__(self, x, y, width, height, image_filename):
        image = pygame.image.load(image_filename)
        original_width, original_height = 32, 32
        scale_factor = min(22 / 32, 22 / 32)
        new_width = int(32 * 0.69)
        new_height = int(32 * 0.69)
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = pygame.Rect(x, y, width, height)

    def get_rect(self):
        return self.rect
    
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

# Стены первого уровня
if 1 == 1:
    wall1 = Wall(0, 0, 22, 22, "wallstone1.png")
    wall3 = Wall(0, 22, 22, 22, "wallstone2.png")
    wall4 = Wall(0, 44, 22, 22, "wallstone1.png")
    wall5 = Wall(0, 66, 22, 22, "wallstone2.png")
    wall6 = Wall(0, 88, 22, 22, "wallstone2.png")
    wall7 = Wall(0, 110, 22, 22, "wallstone1.png")
    wall8 = Wall(0, 132, 22, 22, "wallstone1.png")
    wall9 = Wall(0, 154, 22, 22, "wallstone1.png")
    wall10 = Wall(0, 176, 22, 22, "wallstone2.png")
    wall11 = Wall(0, 198, 22, 22, "wallstone1.png")
    wall12 = Wall(0, 220, 22, 22, "wallstone1.png")
    wall13 = Wall(0, 242, 22, 22, "wallstone1.png")
    wall14 = Wall(0, 264, 22, 22, "wallstone2.png")
    wall15 = Wall(0, 286, 22, 22, "wallstone2.png")
    wall16 = Wall(0, 308, 22, 22, "wallstone1.png")
    wall17 = Wall(0, 330, 22, 22, "wallstone1.png")
    wall18 = Wall(0, 352, 22, 22, "wallstone2.png")
    wall19 = Wall(0, 374, 22, 22, "wallstone2.png")
    wall20 = Wall(0, 396, 22, 22, "wallstone1.png")
    wall21 = Wall(0, 418, 22, 22, "wallstone1.png")
    wall22 = Wall(0, 440, 22, 22, "wallstone1.png")
    wall23 = Wall(0, 462, 22, 22, "wallstone2.png")
    wall24 = Wall(0, 484, 22, 22, "wallstone1.png")
    wall25 = Wall(0, 506, 22, 22, "wallstone1.png")
    wall26 = Wall(0, 528, 22, 22, "wallstone1.png")
    wall27 = Wall(0, 550, 22, 22, "wallstone2.png")
    wall28 = Wall(0, 572, 22, 22, "wallstone2.png")
    wall29 = Wall(0, 594, 22, 22, "wallstone1.png")
    wall30 = Wall(0, 616, 22, 22, "wallstone1.png")
    wall31 = Wall(0, 638, 22, 22, "wallstone2.png")
    wall32 = Wall(0, 660, 22, 22, "wallstone1.png")
    wall33 = Wall(0, 682, 22, 22, "wallstone2.png")
    wall34 = Wall(22, 0, 22, 22, "wallstone2.png")
    wall35 = Wall(44, 0, 22, 22, "wallstone1.png")
    wall36 = Wall(66, 0, 22, 22, "wallstone1.png")
    wall37 = Wall(88, 0, 22, 22, "wallstone1.png")
    wall38 = Wall(88, 0, 22, 22, "wallstone2.png")
    wall39 = Wall(110, 0, 22, 22, "wallstone1.png")
    wall40 = Wall(132, 0, 22, 22, "wallstone1.png")
    wall41 = Wall(154, 0, 22, 22, "wallstone1.png")
    wall42 = Wall(176, 0, 22, 22, "wallstone2.png")
    wall43 = Wall(198, 0, 22, 22, "wallstone1.png")
    wall44 = Wall(220, 0, 22, 22, "wallstone1.png")
    wall45 = Wall(242, 0, 22, 22, "wallstone1.png")
    wall46 = Wall(264, 0, 22, 22, "wallstone2.png")
    wall47 = Wall(286, 0, 22, 22, "wallstone2.png")
    wall48 = Wall(308, 0, 22, 22, "wallstone1.png")
    wall49 = Wall(330, 0, 22, 22, "wallstone1.png")
    wall50 = Wall(352, 0, 22, 22, "wallstone2.png")
    wall51 = Wall(374, 0, 22, 22, "wallstone2.png")
    wall52 = Wall(396, 0, 22, 22, "wallstone1.png")
    wall53 = Wall(418, 0, 22, 22, "wallstone1.png")
    wall54 = Wall(440, 0, 22, 22, "wallstone1.png")
    wall55 = Wall(462, 0, 22, 22, "wallstone2.png")
    wall56 = Wall(484, 0, 22, 22, "wallstone1.png")
    wall57 = Wall(506, 0, 22, 22, "wallstone1.png")
    wall58 = Wall(528, 0, 22, 22, "wallstone1.png")
    wall59 = Wall(550, 0, 22, 22, "wallstone2.png")
    wall60 = Wall(572, 0, 22, 22, "wallstone2.png")
    wall61 = Wall(594, 0, 22, 22, "wallstone1.png")
    wall62 = Wall(616, 0, 22, 22, "wallstone1.png")
    wall63 = Wall(638, 0, 22, 22, "wallstone2.png")
    wall64 = Wall(660, 0, 22, 22, "wallstone1.png")
    wall65 = Wall(682, 0, 22, 22, "wallstone2.png")
    wall66 = Wall(682, 22, 22, 22, "wallstone2.png")
    wall67 = Wall(682, 44, 22, 22, "wallstone1.png")
    wall68 = Wall(682, 66, 22, 22, "wallstone2.png")
    wall69 = Wall(682, 88, 22, 22, "wallstone2.png")
    wall70 = Wall(682, 110, 22, 22, "wallstone1.png")
    wall71 = Wall(682, 132, 22, 22, "wallstone1.png")
    wall249 = Wall(682, 154, 22, 22, "wallstone1.png")
    wall72 = Wall(682, 176, 22, 22, "wallstone2.png")
    wall73 = Wall(682, 198, 22, 22, "wallstone1.png")
    wall74 = Wall(682, 220, 22, 22, "wallstone1.png")
    wall75 = Wall(682, 242, 22, 22, "wallstone1.png")
    wall76 = Wall(682, 264, 22, 22, "wallstone2.png")
    wall77 = Wall(682, 286, 22, 22, "wallstone2.png")
    wall78 = Wall(682, 308, 22, 22, "wallstone1.png")
    wall79 = Wall(682, 330, 22, 22, "wallstone1.png")
    wall80 = Wall(682, 352, 22, 22, "wallstone2.png")
    wall81 = Wall(682, 374, 22, 22, "wallstone2.png")
    wall82 = Wall(682, 396, 22, 22, "wallstone1.png")
    wall83 = Wall(682, 418, 22, 22, "wallstone1.png")
    wall84 = Wall(682, 440, 22, 22, "wallstone1.png")
    wall85 = Wall(682, 462, 22, 22, "wallstone2.png")
    wall86 = Wall(682, 484, 22, 22, "wallstone1.png")
    wall87 = Wall(682, 506, 22, 22, "wallstone1.png")
    wall88 = Wall(682, 528, 22, 22, "wallstone1.png")
    wall89 = Wall(682, 550, 22, 22, "wallstone2.png")
    wall90 = Wall(682, 572, 22, 22, "wallstone2.png")
    wall91 = Wall(682, 594, 22, 22, "wallstone1.png")
    wall92 = Wall(682, 616, 22, 22, "wallstone1.png")
    wall93 = Wall(682, 638, 22, 22, "wallstone2.png")
    wall94 = Wall(682, 660, 22, 22, "wallstone1.png")
    wall95 = Wall(682, 682, 22, 22, "wallstone2.png")
    wall96 = Wall(22, 682, 22, 22, "wallstone2.png")
    wall97 = Wall(44, 682, 22, 22, "wallstone1.png")
    wall98 = Wall(66, 682, 22, 22, "wallstone1.png")
    wall99 = Wall(88, 682, 22, 22, "wallstone1.png")
    wall100 = Wall(88, 682, 22, 22, "wallstone2.png")
    wall101 = Wall(110, 682, 22, 22, "wallstone1.png")
    wall102 = Wall(132, 682, 22, 22, "wallstone1.png")
    wall103 = Wall(154, 682, 22, 22, "wallstone1.png")
    wall104 = Wall(176, 682, 22, 22, "wallstone2.png")
    wall105 = Wall(198, 682, 22, 22, "wallstone1.png")
    wall106 = Wall(220, 682, 22, 22, "wallstone1.png")
    wall107 = Wall(242, 682, 22, 22, "wallstone1.png")
    wall108 = Wall(264, 682, 22, 22, "wallstone2.png")
    wall109 = Wall(286, 682, 22, 22, "wallstone2.png")
    wall110 = Wall(308, 682, 22, 22, "wallstone1.png")
    wall111 = Wall(330, 682, 22, 22, "wallstone1.png")
    wall112 = Wall(352, 682, 22, 22, "wallstone2.png")
    wall113 = Wall(374, 682, 22, 22, "wallstone2.png")
    wall114 = Wall(396, 682, 22, 22, "wallstone1.png")
    wall115 = Wall(418, 682, 22, 22, "wallstone1.png")
    wall116 = Wall(440, 682, 22, 22, "wallstone1.png")
    wall117 = Wall(462, 682, 22, 22, "wallstone2.png")
    wall118 = Wall(484, 682, 22, 22, "wallstone1.png")
    wall119 = Wall(506, 682, 22, 22, "wallstone1.png")
    wall120 = Wall(528, 682, 22, 22, "wallstone1.png")
    wall121 = Wall(550, 682, 22, 22, "wallstone2.png")
    wall122 = Wall(572, 682, 22, 22, "wallstone2.png")
    wall123 = Wall(594, 682, 22, 22, "wallstone1.png")
    wall124 = Wall(616, 682, 22, 22, "wallstone1.png")
    wall125 = Wall(638, 682, 22, 22, "wallstone2.png")
    wall126 = Wall(660, 682, 22, 22, "wallstone1.png")
    wall127 = Wall(682, 682, 22, 22, "wallstone2.png")
    wall128 = Wall(88, 22, 22, 22, "wallstone2.png")
    wall129 = Wall(88, 44, 22, 22, "wallstone1.png")
    wall130 = Wall(88, 66, 22, 22, "wallstone1.png")
    wall131 = Wall(88, 88, 22, 22, "wallstone1.png")
    wall132 = Wall(88, 110, 22, 22, "wallstone2.png")
    wall133 = Wall(88, 132, 22, 22, "wallstone2.png")
    wall134 = Wall(88, 154, 22, 22, "wallstone1.png")
    wall135 = Wall(88, 176, 22, 22, "wallstone1.png")
    wall136 = Wall(88, 198, 22, 22, "wallstone2.png")
    wall137 = Wall(88, 220, 22, 22, "wallstone1.png")
    wall138 = Wall(88, 242, 22, 22, "wallstone1.png")
    wall139 = Wall(88, 264, 22, 22, "wallstone2.png")
    wall140 = Wall(88, 286, 22, 22, "wallstone2.png")
    wall141 = Wall(88, 308, 22, 22, "wallstone1.png")
    wall142 = Wall(110, 308, 22, 22, "wallstone2.png")
    wall143 = Wall(132, 308, 22, 22, "wallstone1.png")
    wall144 = Wall(154, 308, 22, 22, "wallstone1.png")
    wall145 = Wall(176, 308, 22, 22, "wallstone1.png")
    wall146 = Wall(198, 308, 22, 22, "wallstone2.png")
    wall147 = Wall(220, 308, 22, 22, "wallstone2.png")
    wall148 = Wall(242, 308, 22, 22, "wallstone1.png")
    wall152 = Wall(330, 308, 22, 22, "wallstone2.png")
    wall153 = Wall(330, 330, 22, 22, "wallstone2.png")
    wall154 = Wall(330, 352, 22, 22, "wallstone1.png")
    wall155 = Wall(330, 374, 22, 22, "wallstone1.png")
    wall156 = Wall(330, 396, 22, 22, "wallstone1.png")
    wall157 = Wall(330, 418, 22, 22, "wallstone2.png")
    wall158 = Wall(330, 440, 22, 22, "wallstone1.png")
    wall159 = Wall(330, 462, 22, 22, "wallstone2.png")
    wall160 = Wall(330, 484, 22, 22, "wallstone2.png")
    wall161 = Wall(330, 506, 22, 22, "wallstone1.png")
    wall162 = Wall(330, 528, 22, 22, "wallstone1.png")
    wall163 = Wall(330, 286, 22, 22, "wallstone2.png")
    wall164 = Wall(330, 264, 22, 22, "wallstone1.png")
    wall165 = Wall(330, 242, 22, 22, "wallstone1.png")
    wall166 = Wall(308, 242, 22, 22, "wallstone2.png")
    wall167 = Wall(286, 242, 22, 22, "wallstone2.png")
    wall168 = Wall(264, 242, 22, 22, "wallstone1.png")
    wall169 = Wall(242, 242, 22, 22, "wallstone1.png")
    wall170 = Wall(220, 242, 22, 22, "wallstone1.png")
    wall171 = Wall(198, 242, 22, 22, "wallstone1.png")
    wall172 = Wall(176, 242, 22, 22, "wallstone2.png")
    wall173 = Wall(154, 242, 22, 22, "wallstone1.png")
    wall174 = Wall(264, 220, 22, 22, "wallstone2.png")
    wall175 = Wall(264, 198, 22, 22, "wallstone1.png")
    wall176 = Wall(264, 176, 22, 22, "wallstone1.png")
    wall177 = Wall(264, 154, 22, 22, "wallstone1.png")
    wall178 = Wall(264, 132, 22, 22, "wallstone1.png")
    wall179 = Wall(264, 110, 22, 22, "wallstone2.png")
    wall180 = Wall(264, 88, 22, 22, "wallstone2.png")
    wall181 = Wall(286, 88, 22, 22, "wallstone2.png")
    wall182 = Wall(308, 88, 22, 22, "wallstone1.png")
    wall183 = Wall(330, 88, 22, 22, "wallstone2.png")
    wall184 = Wall(352, 88, 22, 22, "wallstone1.png")
    wall185 = Wall(374, 88, 22, 22, "wallstone1.png")
    wall186 = Wall(396, 88, 22, 22, "wallstone2.png")
    wall187 = Wall(418, 88, 22, 22, "wallstone1.png")
    wall188 = Wall(440, 88, 22, 22, "wallstone1.png")
    wall189 = Wall(462, 88, 22, 22, "wallstone2.png")
    wall190 = Wall(242, 330, 22, 22, "wallstone2.png")
    wall191 = Wall(242, 352, 22, 22, "wallstone1.png")
    wall192 = Wall(242, 374, 22, 22, "wallstone2.png")
    wall193 = Wall(242, 396, 22, 22, "wallstone2.png")
    wall194 = Wall(242, 418, 22, 22, "wallstone1.png")
    wall195 = Wall(242, 440, 22, 22, "wallstone1.png")
    wall196 = Wall(242, 462, 22, 22, "wallstone2.png")
    wall197 = Wall(242, 484, 22, 22, "wallstone2.png")
    wall198 = Wall(242, 506, 22, 22, "wallstone1.png")
    wall199 = Wall(242, 528, 22, 22, "wallstone2.png")
    wall200 = Wall(242, 550, 22, 22, "wallstone1.png")
    wall201 = Wall(242, 572, 22, 22, "wallstone1.png")
    wall202 = Wall(242, 594, 22, 22, "wallstone2.png")
    wall203 = Wall(242, 594, 22, 22, "wallstone2.png")
    wall204 = Wall(264, 594, 22, 22, "wallstone1.png")
    wall205 = Wall(286, 594, 22, 22, "wallstone1.png")
    wall206 = Wall(308, 594, 22, 22, "wallstone1.png")
    wall207 = Wall(330, 594, 22, 22, "wallstone2.png")
    wall208 = Wall(352, 594, 22, 22, "wallstone1.png")
    wall209 = Wall(374, 594, 22, 22, "wallstone2.png")
    wall210 = Wall(396, 594, 22, 22, "wallstone1.png")
    wall211 = Wall(396, 594, 22, 22, "wallstone1.png")
    wall212 = Wall(396, 572, 22, 22, "wallstone2.png")
    wall213 = Wall(396, 550, 22, 22, "wallstone2.png")
    wall214 = Wall(396, 528, 22, 22, "wallstone1.png")
    wall215 = Wall(396, 506, 22, 22, "wallstone1.png")
    wall216 = Wall(396, 484, 22, 22, "wallstone2.png")
    wall217 = Wall(396, 462, 22, 22, "wallstone1.png")
    wall218 = Wall(396, 440, 22, 22, "wallstone2.png")
    wall219 = Wall(396, 440, 22, 22, "wallstone2.png")
    wall220 = Wall(418, 440, 22, 22, "wallstone1.png")
    wall221 = Wall(440, 440, 22, 22, "wallstone1.png")
    wall222 = Wall(462, 440, 22, 22, "wallstone1.png")
    wall223 = Wall(484, 440, 22, 22, "wallstone2.png")
    wall224 = Wall(506, 440, 22, 22, "wallstone1.png")
    wall225 = Wall(528, 440, 22, 22, "wallstone1.png")
    wall226 = Wall(528, 418, 22, 22, "wallstone2.png")
    wall227 = Wall(528, 396, 22, 22, "wallstone1.png")
    wall228 = Wall(528, 374, 22, 22, "wallstone1.png")
    wall229 = Wall(528, 352, 22, 22, "wallstone2.png")
    wall230 = Wall(528, 330, 22, 22, "wallstone2.png")
    wall231 = Wall(528, 308, 22, 22, "wallstone2.png")
    wall232 = Wall(528, 286, 22, 22, "wallstone1.png")
    wall233 = Wall(528, 264, 22, 22, "wallstone2.png")
    wall234 = Wall(528, 242, 22, 22, "wallstone1.png")
    wall235 = Wall(528, 220, 22, 22, "wallstone1.png")
    wall236 = Wall(528, 198, 22, 22, "wallstone2.png")
    wall237 = Wall(528, 176, 22, 22, "wallstone2.png")
    wall238 = Wall(528, 154, 22, 22, "wallstone1.png")
    wall239 = Wall(528, 132, 22, 22, "wallstone2.png")
    wall240 = Wall(528, 110, 22, 22, "wallstone1.png")
    wall241 = Wall(506, 264, 22, 22, "wallstone2.png")
    wall242 = Wall(484, 264, 22, 22, "wallstone1.png")
    wall243 = Wall(462, 264, 22, 22, "wallstone1.png")
    wall244 = Wall(440, 264, 22, 22, "wallstone1.png")
    wall245 = Wall(418, 264, 22, 22, "wallstone2.png")
    wall246 = Wall(396, 264, 22, 22, "wallstone1.png")
    wall247 = Wall(374, 264, 22, 22, "wallstone2.png")
    wall248 = Wall(352, 264, 22, 22, "wallstone1.png")
    wall250 = Wall(330, 264, 22, 22, "wallstone1.png")
    wall251 = Wall(132, 660, 22, 22, "wallstone2.png")
    wall252 = Wall(132, 638, 22, 22, "wallstone1.png")
    wall253 = Wall(132, 616, 22, 22, "wallstone1.png")
    wall254 = Wall(132, 594, 22, 22, "wallstone1.png")
    wall255 = Wall(132, 572, 22, 22, "wallstone2.png")
    wall256 = Wall(132, 550, 22, 22, "wallstone2.png")
    wall257 = Wall(132, 528, 22, 22, "wallstone1.png")
    wall258 = Wall(132, 506, 22, 22, "wallstone2.png")
    wall259 = Wall(132, 484, 22, 22, "wallstone1.png")
    wall260 = Wall(132, 462, 22, 22, "wallstone2.png")
    wall261 = Wall(132, 440, 22, 22, "wallstone1.png")
    wall262 = Wall(528, 660, 22, 22, "wallstone2.png")
    wall263 = Wall(528, 638, 22, 22, "wallstone1.png")
    wall264 = Wall(528, 616, 22, 22, "wallstone1.png")
    wall265 = Wall(528, 594, 22, 22, "wallstone1.png")
    wall266 = Wall(528, 572, 22, 22, "wallstone2.png")
    wall267 = Wall(528, 550, 22, 22, "wallstone1.png")
    wall268 = Wall(528, 528, 22, 22, "wallstone2.png")

walls = [wall1, wall3, wall4, wall5, wall6, wall7, wall8, wall9, wall10, wall11, wall12, 
wall13, wall14, wall15, wall16, wall17, wall18, wall19, wall20, wall21, wall22, wall23, wall24, wall25,
wall26, wall27, wall28, wall29, wall30, wall31, wall32, wall33, wall34, wall35, wall36, wall37, wall38,
wall39, wall40, wall41, wall42, wall43, wall44, wall45, wall46, wall47, wall48, wall49, wall50, wall51,
wall52, wall53, wall54, wall55, wall56, wall57, wall58, wall59, wall60, wall61, wall62, wall63, wall64,
wall65, wall66, wall67, wall68, wall69, wall70, wall71, wall72, wall73, wall74, wall75, wall76, wall77,
wall78, wall79, wall80, wall81, wall82, wall83, wall84, wall85, wall86, wall87, wall88, wall89, wall90,
wall91, wall92, wall93, wall94, wall95, wall96, wall97, wall98, wall99, wall100, wall101, wall102, wall103,
wall104, wall105, wall106, wall107, wall108, wall109, wall110, wall111, wall112, wall113, wall114,
wall115, wall116, wall117, wall118, wall119, wall120, wall121, wall122, wall123, wall124, wall125, wall126,
wall127, wall128, wall129, wall130, wall131, wall132, wall133, wall134, wall135, wall136, wall137, wall138,
wall139, wall140, wall141, wall142, wall143, wall144, wall145, wall146, wall147, wall148, 
wall152, wall153, wall154, wall155, wall156, wall157, wall158, wall159, wall160, wall161, wall162,
wall163, wall164, wall165, wall166, wall167, wall168, wall169, wall170, wall171, wall172, wall173, wall174,
wall175, wall176, wall177, wall178, wall179, wall180, wall181, wall182, wall183, wall184, wall185, wall186,
wall187, wall188, wall189, wall190, wall191, wall192, wall193, wall194, wall195, wall196, wall197, wall198,
wall199, wall200, wall201, wall202, wall203, wall204, wall205, wall206, wall207, wall208, wall209, wall210,
wall211, wall212, wall213, wall214, wall215, wall216, wall217, wall218, wall219, wall220, wall221, wall222,
wall223, wall224, wall225, wall226, wall227, wall228, wall229, wall230, wall231, wall232, wall233, wall234,
wall235, wall236, wall237, wall238, wall239, wall240, wall241, wall242, wall243, wall244, wall245, wall246,
wall247, wall248, wall249, wall250, wall251, wall252, wall253, wall254, wall255, wall256, wall257,
wall258, wall259, wall260, wall261, wall262, wall263, wall264, wall265, wall266, wall267, wall268]

# Стены второго уровня
if 1 == 1:
    walll1 = Wall(0, 0, 22, 22, "wallstone1.png")
    walll2 = Wall(0, 22, 22, 22, "wallstone2.png")
    walll3 = Wall(0, 44, 22, 22, "wallstone1.png")
    walll4 = Wall(0, 66, 22, 22, "wallstone2.png")
    walll5 = Wall(0, 88, 22, 22, "wallstone2.png")
    walll6 = Wall(0, 110, 22, 22, "wallstone1.png")
    walll7 = Wall(0, 132, 22, 22, "wallstone1.png")
    walll8 = Wall(0, 154, 22, 22, "wallstone1.png")
    walll9 = Wall(0, 176, 22, 22, "wallstone2.png")
    walll10 = Wall(0, 198, 22, 22, "wallstone1.png")
    walll11 = Wall(0, 220, 22, 22, "wallstone1.png")
    walll12 = Wall(0, 242, 22, 22, "wallstone1.png")
    walll13 = Wall(0, 264, 22, 22, "wallstone2.png")
    walll14 = Wall(0, 286, 22, 22, "wallstone2.png")
    walll15 = Wall(0, 308, 22, 22, "wallstone1.png")
    walll16 = Wall(0, 330, 22, 22, "wallstone1.png")
    walll17 = Wall(0, 352, 22, 22, "wallstone2.png")
    walll18 = Wall(0, 374, 22, 22, "wallstone2.png")
    walll19 = Wall(0, 396, 22, 22, "wallstone1.png")
    walll20 = Wall(0, 418, 22, 22, "wallstone1.png")
    walll21 = Wall(0, 440, 22, 22, "wallstone1.png")
    walll22 = Wall(0, 462, 22, 22, "wallstone2.png")
    walll23 = Wall(0, 484, 22, 22, "wallstone1.png")
    walll24 = Wall(0, 506, 22, 22, "wallstone1.png")
    walll25 = Wall(0, 528, 22, 22, "wallstone1.png")
    walll26 = Wall(0, 550, 22, 22, "wallstone2.png")
    walll27 = Wall(0, 572, 22, 22, "wallstone2.png")
    walll28 = Wall(0, 594, 22, 22, "wallstone1.png")
    walll29 = Wall(0, 616, 22, 22, "wallstone1.png")
    walll30 = Wall(0, 638, 22, 22, "wallstone2.png")
    walll31 = Wall(0, 660, 22, 22, "wallstone1.png")
    walll32 = Wall(0, 682, 22, 22, "wallstone2.png")
    walll33 = Wall(22, 0, 22, 22, "wallstone2.png")
    walll34 = Wall(44, 0, 22, 22, "wallstone1.png")
    walll35 = Wall(66, 0, 22, 22, "wallstone1.png")
    walll36 = Wall(88, 0, 22, 22, "wallstone1.png")
    walll37 = Wall(88, 0, 22, 22, "wallstone2.png")
    walll38 = Wall(110, 0, 22, 22, "wallstone1.png")
    walll39 = Wall(132, 0, 22, 22, "wallstone1.png")
    walll40 = Wall(154, 0, 22, 22, "wallstone1.png")
    walll41 = Wall(176, 0, 22, 22, "wallstone2.png")
    walll42 = Wall(198, 0, 22, 22, "wallstone1.png")
    walll43 = Wall(220, 0, 22, 22, "wallstone1.png")
    walll44 = Wall(242, 0, 22, 22, "wallstone2.png")
    walll45 = Wall(264, 0, 22, 22, "wallstone2.png")
    walll46 = Wall(286, 0, 22, 22, "wallstone2.png")
    walll47 = Wall(308, 0, 22, 22, "wallstone1.png")
    walll48 = Wall(330, 0, 22, 22, "wallstone1.png")
    walll49 = Wall(352, 0, 22, 22, "wallstone2.png")
    walll50 = Wall(374, 0, 22, 22, "wallstone2.png")
    walll51 = Wall(396, 0, 22, 22, "wallstone1.png")
    walll52 = Wall(418, 0, 22, 22, "wallstone1.png")
    walll53 = Wall(440, 0, 22, 22, "wallstone1.png")
    walll54 = Wall(462, 0, 22, 22, "wallstone2.png")
    walll55 = Wall(484, 0, 22, 22, "wallstone1.png")
    walll56 = Wall(506, 0, 22, 22, "wallstone1.png")
    walll57 = Wall(528, 0, 22, 22, "wallstone1.png")
    walll58 = Wall(550, 0, 22, 22, "wallstone2.png")
    walll59 = Wall(572, 0, 22, 22, "wallstone2.png")
    walll60 = Wall(594, 0, 22, 22, "wallstone1.png")
    walll61 = Wall(616, 0, 22, 22, "wallstone1.png")
    walll62 = Wall(638, 0, 22, 22, "wallstone2.png")
    walll63 = Wall(660, 0, 22, 22, "wallstone1.png")
    walll64 = Wall(682, 0, 22, 22, "wallstone2.png")
    walll65 = Wall(682, 22, 22, 22, "wallstone2.png")
    walll66 = Wall(682, 44, 22, 22, "wallstone1.png")
    walll67 = Wall(682, 66, 22, 22, "wallstone2.png")
    walll68 = Wall(682, 88, 22, 22, "wallstone2.png")
    walll69 = Wall(682, 110, 22, 22, "wallstone1.png")
    walll70 = Wall(682, 132, 22, 22, "wallstone1.png")
    walll71 = Wall(682, 154, 22, 22, "wallstone1.png")
    walll72 = Wall(682, 176, 22, 22, "wallstone2.png")
    walll73 = Wall(682, 198, 22, 22, "wallstone1.png")
    walll74 = Wall(682, 220, 22, 22, "wallstone1.png")
    walll75 = Wall(682, 242, 22, 22, "wallstone1.png")
    walll76 = Wall(682, 264, 22, 22, "wallstone2.png")
    walll77 = Wall(682, 286, 22, 22, "wallstone2.png")
    walll78 = Wall(682, 308, 22, 22, "wallstone1.png")
    walll79 = Wall(682, 330, 22, 22, "wallstone1.png")
    walll80 = Wall(682, 352, 22, 22, "wallstone2.png")
    walll81 = Wall(682, 374, 22, 22, "wallstone2.png")
    walll82 = Wall(682, 396, 22, 22, "wallstone1.png")
    walll83 = Wall(682, 418, 22, 22, "wallstone1.png")
    walll84 = Wall(682, 440, 22, 22, "wallstone1.png")
    walll85 = Wall(682, 462, 22, 22, "wallstone2.png")
    walll86 = Wall(682, 484, 22, 22, "wallstone1.png")
    walll87 = Wall(682, 506, 22, 22, "wallstone1.png")
    walll88 = Wall(682, 528, 22, 22, "wallstone1.png")
    walll89 = Wall(682, 550, 22, 22, "wallstone2.png")
    walll90 = Wall(682, 572, 22, 22, "wallstone2.png")
    walll91 = Wall(682, 594, 22, 22, "wallstone1.png")
    walll92 = Wall(682, 616, 22, 22, "wallstone1.png")
    walll93 = Wall(682, 638, 22, 22, "wallstone2.png")
    walll94 = Wall(682, 660, 22, 22, "wallstone1.png")
    walll95 = Wall(682, 682, 22, 22, "wallstone2.png")
    walll96 = Wall(22, 682, 22, 22, "wallstone2.png")
    walll97 = Wall(44, 682, 22, 22, "wallstone1.png")
    walll98 = Wall(66, 682, 22, 22, "wallstone1.png")
    walll99 = Wall(88, 682, 22, 22, "wallstone1.png")
    walll100 = Wall(88, 682, 22, 22, "wallstone2.png")
    walll101 = Wall(110, 682, 22, 22, "wallstone1.png")
    walll102 = Wall(132, 682, 22, 22, "wallstone1.png")
    walll103 = Wall(154, 682, 22, 22, "wallstone1.png")
    walll104 = Wall(176, 682, 22, 22, "wallstone2.png")
    walll105 = Wall(198, 682, 22, 22, "wallstone1.png")
    walll106 = Wall(220, 682, 22, 22, "wallstone1.png")
    walll107 = Wall(242, 682, 22, 22, "wallstone1.png")
    walll108 = Wall(264, 682, 22, 22, "wallstone2.png")
    walll109 = Wall(286, 682, 22, 22, "wallstone2.png")
    walll110 = Wall(308, 682, 22, 22, "wallstone1.png")
    walll111 = Wall(330, 682, 22, 22, "wallstone1.png")
    walll112 = Wall(352, 682, 22, 22, "wallstone2.png")
    walll113 = Wall(374, 682, 22, 22, "wallstone2.png")
    walll114 = Wall(396, 682, 22, 22, "wallstone1.png")
    walll115 = Wall(418, 682, 22, 22, "wallstone1.png")
    walll116 = Wall(440, 682, 22, 22, "wallstone1.png")
    walll117 = Wall(462, 682, 22, 22, "wallstone2.png")
    walll118 = Wall(484, 682, 22, 22, "wallstone1.png")
    walll119 = Wall(506, 682, 22, 22, "wallstone1.png")
    walll120 = Wall(528, 682, 22, 22, "wallstone1.png")
    walll121 = Wall(550, 682, 22, 22, "wallstone2.png")
    walll122 = Wall(572, 682, 22, 22, "wallstone2.png")
    walll123 = Wall(594, 682, 22, 22, "wallstone1.png")
    walll124 = Wall(616, 682, 22, 22, "wallstone1.png")
    walll125 = Wall(638, 682, 22, 22, "wallstone2.png")
    walll126 = Wall(660, 682, 22, 22, "wallstone1.png")
    walll127 = Wall(682, 682, 22, 22, "wallstone2.png")
    walll128 = Wall(242, 22, 22, 22, "wallstone2.png")
    walll129 = Wall(242, 44, 22, 22, "wallstone1.png")
    walll130 = Wall(242, 66, 22, 22, "wallstone1.png")
    walll131 = Wall(242, 88, 22, 22, "wallstone1.png")
    walll132 = Wall(242, 110, 22, 22, "wallstone2.png")
    walll133 = Wall(242, 132, 22, 22, "wallstone1.png")
    walll134 = Wall(242, 154, 22, 22, "wallstone2.png")
    walll135 = Wall(22, 374, 22, 22, "wallstone2.png")
    walll136 = Wall(44, 374, 22, 22, "wallstone2.png")
    walll137 = Wall(66, 374, 22, 22, "wallstone1.png")
    walll138 = Wall(88, 374, 22, 22, "wallstone2.png")
    walll139 = Wall(110, 374, 22, 22, "wallstone1.png")
    walll140 = Wall(132, 374, 22, 22, "wallstone2.png")
    walll141 = Wall(132, 286, 22, 22, "wallstone2.png")
    walll142 = Wall(132, 264, 22, 22, "wallstone1.png")
    walll143 = Wall(132, 242, 22, 22, "wallstone1.png")
    walll144 = Wall(132, 220, 22, 22, "wallstone2.png")
    walll145 = Wall(132, 198, 22, 22, "wallstone1.png")
    walll146 = Wall(132, 176, 22, 22, "wallstone2.png")
    walll147 = Wall(132, 154, 22, 22, "wallstone2.png")
    walll148 = Wall(154, 286, 22, 22, "wallstone2.png")
    walll149 = Wall(176, 286, 22, 22, "wallstone1.png")
    walll150 = Wall(198, 286, 22, 22, "wallstone1.png")
    walll151 = Wall(220, 286, 22, 22, "wallstone2.png")
    walll152 = Wall(242, 286, 22, 22, "wallstone1.png")
    walll153 = Wall(264, 286, 22, 22, "wallstone2.png")
    walll154 = Wall(286, 286, 22, 22, "wallstone2.png")
    walll155 = Wall(308, 286, 22, 22, "wallstone1.png")
    walll156 = Wall(330, 286, 22, 22, "wallstone2.png")
    walll157 = Wall(352, 176, 22, 22, "wallstone2.png")
    walll158 = Wall(352, 198, 22, 22, "wallstone1.png")
    walll159 = Wall(352, 220, 22, 22, "wallstone1.png")
    walll160 = Wall(352, 242, 22, 22, "wallstone1.png")
    walll161 = Wall(352, 264, 22, 22, "wallstone2.png")
    walll162 = Wall(352, 286, 22, 22, "wallstone1.png")
    walll163 = Wall(352, 308, 22, 22, "wallstone2.png")
    walll164 = Wall(352, 330, 22, 22, "wallstone2.png")
    walll165 = Wall(352, 352, 22, 22, "wallstone1.png")
    walll166 = Wall(352, 374, 22, 22, "wallstone2.png")
    walll167 = Wall(352, 396, 22, 22, "wallstone1.png")
    walll168 = Wall(462, 396, 22, 22, "wallstone1.png")
    walll169 = Wall(462, 418, 22, 22, "wallstone2.png")
    walll170 = Wall(462, 440, 22, 22, "wallstone2.png")
    walll171 = Wall(462, 462, 22, 22, "wallstone1.png")
    walll172 = Wall(462, 484, 22, 22, "wallstone2.png")
    walll173 = Wall(572, 506, 22, 22, "wallstone2.png")
    walll174 = Wall(550, 506, 22, 22, "wallstone1.png")
    walll175 = Wall(528, 506, 22, 22, "wallstone1.png")
    walll176 = Wall(506, 506, 22, 22, "wallstone2.png")
    walll177 = Wall(484, 506, 22, 22, "wallstone1.png")
    walll178 = Wall(462, 506, 22, 22, "wallstone2.png")
    walll179 = Wall(440, 506, 22, 22, "wallstone2.png")
    walll180 = Wall(418, 506, 22, 22, "wallstone1.png")
    walll181 = Wall(396, 506, 22, 22, "wallstone1.png")
    walll182 = Wall(374, 506, 22, 22, "wallstone1.png")
    walll183 = Wall(352, 506, 22, 22, "wallstone2.png")
    walll184 = Wall(330, 506, 22, 22, "wallstone1.png")
    walll185 = Wall(308, 506, 22, 22, "wallstone2.png")
    walll186 = Wall(286, 506, 22, 22, "wallstone2.png")
    walll187 = Wall(264, 506, 22, 22, "wallstone1.png")
    walll188 = Wall(242, 506, 22, 22, "wallstone1.png")
    walll189 = Wall(220, 506, 22, 22, "wallstone2.png")
    walll190 = Wall(198, 506, 22, 22, "wallstone1.png")
    walll191 = Wall(176, 506, 22, 22, "wallstone1.png")
    walll192 = Wall(154, 506, 22, 22, "wallstone2.png")
    walll193 = Wall(132, 506, 22, 22, "wallstone1.png")
    walll194 = Wall(242, 484, 22, 22, "wallstone2.png")
    walll195 = Wall(242, 462, 22, 22, "wallstone1.png")
    walll196 = Wall(242, 440, 22, 22, "wallstone1.png")
    walll197 = Wall(242, 418, 22, 22, "wallstone2.png")
    walll198 = Wall(242, 396, 22, 22, "wallstone1.png")
    walll199 = Wall(242, 374, 22, 22, "wallstone2.png")
    walll200 = Wall(374, 396, 22, 22, "wallstone2.png")
    walll201 = Wall(396, 396, 22, 22, "wallstone1.png")
    walll202 = Wall(418, 396, 22, 22, "wallstone2.png")
    walll203 = Wall(440, 396, 22, 22, "wallstone1.png")
    walll204 = Wall(572, 396, 22, 22, "wallstone2.png")
    walll205 = Wall(572, 374, 22, 22, "wallstone1.png")
    walll206 = Wall(572, 352, 22, 22, "wallstone1.png")
    walll207 = Wall(572, 330, 22, 22, "wallstone2.png")
    walll208 = Wall(572, 308, 22, 22, "wallstone2.png")
    walll209 = Wall(572, 286, 22, 22, "wallstone1.png")
    walll210 = Wall(572, 264, 22, 22, "wallstone2.png")
    walll211 = Wall(550, 264, 22, 22, "wallstone2.png")
    walll212 = Wall(528, 264, 22, 22, "wallstone1.png")
    walll213 = Wall(506, 264, 22, 22, "wallstone1.png")
    walll214 = Wall(484, 264, 22, 22, "wallstone2.png")
    walll215 = Wall(462, 264, 22, 22, "wallstone1.png")
    walll216 = Wall(462, 242, 22, 22, "wallstone1.png")
    walll217 = Wall(462, 220, 22, 22, "wallstone2.png")
    walll218 = Wall(462, 198, 22, 22, "wallstone1.png")
    walll219 = Wall(462, 176, 22, 22, "wallstone2.png")
    walll220 = Wall(462, 154, 22, 22, "wallstone1.png")
    walll221 = Wall(484, 154, 22, 22, "wallstone2.png")
    walll222 = Wall(506, 154, 22, 22, "wallstone1.png")
    walll223 = Wall(528, 154, 22, 22, "wallstone2.png")
    walll224 = Wall(550, 154, 22, 22, "wallstone2.png")
    walll225 = Wall(572, 154, 22, 22, "wallstone1.png")
    walll226 = Wall(594, 154, 22, 22, "wallstone1.png")
    walll227 = Wall(616, 154, 22, 22, "wallstone2.png")
    walll228 = Wall(638, 154, 22, 22, "wallstone2.png")
    walll229 = Wall(660, 154, 22, 22, "wallstone1.png")

    walll230 = Wall(462, 528, 22, 22, "wallstone2.png")
    walll231 = Wall(462, 550, 22, 22, "wallstone1.png")

walls2 = [walll1, walll2, walll3, walll4, walll5, walll6, walll7, walll8, walll9, walll10, walll11, walll12,
walll13, walll14, walll15, walll16, walll17, walll18, walll19, walll20, walll21, walll22, walll23, walll24, 
walll25, walll26, walll27, walll28, walll29, walll30, walll31, walll32, walll33, walll34, walll35, walll36,
walll37, walll38, walll39, walll40, walll41, walll42, walll43, walll44, walll45, walll46, walll47, walll48,
walll49, walll50, walll51, walll52, walll53, walll54, walll55, walll56, walll57, walll58, walll59, walll60,
walll61, walll62, walll63, walll64, walll65, walll66, walll67, walll68, walll69, walll70, walll71, walll72,
walll73, walll74, walll75, walll76, walll77, walll78, walll79, walll80, walll81, walll82, walll83, walll84,
walll85, walll86, walll87, walll88, walll89, walll90, walll91, walll92, walll93, walll94, walll95, walll96,
walll97, walll98, walll99, walll100, walll101, walll102, walll103, walll104, walll105, walll106, walll107,
walll108, walll109, walll110, walll111, walll112, walll113, walll114, walll115, walll116, walll117,
walll118, walll119, walll120, walll121, walll122, walll123, walll124, walll125, walll126, walll127, walll128,
walll129, walll130, walll131, walll132, walll133, walll134, walll135, walll136, walll137, walll138, walll139,
walll140, walll141, walll142, walll143, walll144, walll145, walll146, walll147, walll148, walll149, walll150,
walll151, walll152, walll153, walll154, walll155, walll156, walll157, walll158, walll159, walll160, walll161,
walll162, walll163, walll164, walll165, walll166, walll167, walll168, walll169, walll170, walll171, walll172,
walll173, walll174, walll175, walll176, walll177, walll178, walll179, walll180, walll181, walll182, walll183,
walll184, walll185, walll186, walll187, walll188, walll189, walll190, walll191, walll192, walll193, walll194,
walll195, walll196, walll197, walll198, walll199, walll200, walll201, walll202, walll203, walll204, walll205,
walll206, walll207, walll208, walll209, walll210, walll211, walll212, walll213, walll214, walll215, walll216,
walll217, walll218, walll219, walll220, walll221, walll222, walll223, walll224, walll225, walll226, walll227,
walll228, walll229, walll230, walll231]

# Создаем портал на первом уровне
portal = Portal(415, 345, 40, 40, "portal.png")  

level_now = 0
levels = [
    [walls],
    [walls2]
]

game_started = False

running = True 
game_over = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.health = 100
                player.x = 50
                player.y = 50
                enemies = [
                    Enemy("enemy1.jpeg", 100, 10, 2, 26, 26, 200, 215, dx=1, dy=0, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 300, 40, dx=1, dy=1, range_y=100),
                    Enemy("enemy1.jpeg", 100, 10, 2, 26, 26, 480, 530, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 132, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 60, 176, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 220, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 60, 264, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 308, dx=1, dy=1, range_x=100),

                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 440, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 440, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 506, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 506, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 572, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 572, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 29, 616, dx=1, dy=1, range_x=100),
                    Enemy("enemy1.jpeg", 100, 10, 1, 26, 26, 105, 616, dx=1, dy=1, range_x=100)
                ]
                enemy_hits = {}
                projectiles = []
                game_over = False
                level_now = 0  # Сбрасываем уровень при рестарте

    if not game_started:
        start_text = font.render("Натисніть Enter (кейпад) щоб почати гру!", True, (255, 255, 255))
        screen.blit(main_menu, (0, 0))
        screen.blit(start_text, (100, 500))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP_ENTER:
                print("1")

                game_started = True
                pass
                print(game_started)
        if game_started == True:
            game_over = False


    if not game_over:

        keys = pygame.key.get_pressed()

        # Движение игрока в зависимости от уровня
        if level_now == 0:
            player.move(keys, walls)
        elif level_now == 1:
            player.move(keys, walls2)

        # Стрельба
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - player.last_shot_time >= 2000:
            bullet = Projectile(player.x + player.width, player.y + player.height // 2, direction=player.shoot_direction)
            projectiles.append(bullet)
            player.last_shot_time = current_time

        # Отрисовка
        screen.fill((0, 0, 0))
        screen.blit(resized_background, (0, 0))

        # Отрисовка игрока и врагов
        player.draw(screen)
        if level_now == 0:
            enemy.draw(screen)

        # Отрисовка стен в зависимости от уровня
        if level_now == 0:
            for wall in walls:
                wall.draw(screen)
            portal.draw(screen)  # Отрисовываем портал на первом уровне
        elif level_now == 1:
            for wall in walls2:
                wall.draw(screen)

        for enemy in enemies:
            if level_now == 0:
                enemy.move(walls)
            elif level_now == 1:
                enemy.move(walls2)
            enemy.draw(screen)
            if player.get_rect().colliderect(enemy.get_rect()) and current_time - player.last_hit_time >= 1000:
                player.health -= 10
                player.last_hit_time = current_time
                # print(f"Player hit by {enemy.name}! HP: {player.health}")
                if player.health <= 0:
                    game_over = True

        # Проверка столкновения с порталом
        if level_now == 0 and player.get_rect().colliderect(portal.get_rect()):
            level_now = 1
            player.x = 50  # Перемещаем игрока в начальную позицию на втором уровне
            player.y = 50
            print("Переход на второй уровень!")

        for projectile in projectiles[:]:
            projectile.move()
            projectile.draw(screen)

            for enemy in enemies[:]:
                if projectile.rect.colliderect(enemy.get_rect()):
                    name = enemy.img
                    enemy_hits[name] = enemy_hits.get(name, 0) + 1
                    projectiles.remove(projectile)
                    if enemy_hits[name] >= 3:
                        enemies.remove(enemy)
                    break

            if (projectile.rect.x > screen.get_width() or projectile.rect.x < 0 or 
                projectile.rect.y > screen.get_height() or projectile.rect.y < 0):
                projectiles.remove(projectile)

    else:
        if game_started == True:
            screen.fill((0, 0, 0))
            game_over_text = font.render("Ви програли! Натисніть R щоб почати знову", True, (255, 0, 0))
            screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 
                                        screen.get_height() // 2 - game_over_text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)