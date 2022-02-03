import random

import pygame
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

Base = declarative_base()

Vector2 = pygame.math.Vector2
player = ""
score_list = {}


class Snake:  # Just a snake class
    def __init__(self):
        self.body = [Vector2(cell_number / 2, cell_number / 2), Vector2(cell_number / 2 - 1, cell_number / 2)]
        # list of body elements - starting with 2
        self.direction = Vector2(1, 0)
        self.new_block = False  # if we are adding a new block in current move
        self.score = 0
        self.move = False  # if snake is in move

    def draw_snake(self):  # drawing function
        for block in self.body:
            position_x = int(block.x * cell_size)
            position_y = int(block.y * cell_size)
            block_rect = pygame.Rect(position_x, position_y, cell_size, cell_size)
            pygame.draw.rect(screen, (62, 87, 34), block_rect)

    def move_snake(self):  # moving function
        if self.move:
            # if it is on move - copy entire body without last element -> insert last element at the beginning
            if self.new_block:  # if it is on apple -> copy body with last element
                body_copy = self.body[:]
                body_copy.insert(0, body_copy[0] + self.direction)
                self.body = body_copy[:]
                self.new_block = False
            else:
                body_copy = self.body[:-1]
                body_copy.insert(0, body_copy[0] + self.direction)
                self.body = body_copy[:]

    def enlarge(self):
        self.new_block = True

    def reset(self):  # Start from default settings
        self.body = [Vector2(cell_number / 2, cell_number / 2), Vector2(cell_number / 2 - 1, cell_number / 2)]
        self.direction = Vector2(1, 0)
        self.score = 0
        self.move = False


class Apple:  # simple class for apple
    def __init__(self):  # random position on a board
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.position = Vector2(self.x, self.y)

    def draw_apple(self):  # drawing function with apple structure form .png file
        position_x = int(self.position.x * cell_size) + 10
        position_y = int(self.position.y * cell_size) + 7
        apple_rect = pygame.Rect(position_x, position_y, cell_size, cell_size)
        screen.blit(apple_image, apple_rect)

    def change_position(self):  # generating new coordinates for apple
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.position = Vector2(self.x, self.y)


class Game:  # main game class
    def __init__(self):
        self.player = player
        self.snake = Snake()
        self.apple = Apple()
        self.sorted_list = sorted_score_list

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.game_over_check()
        self.player_update()

    def player_update(self):
        self.player = player

    def draw(self):
        self.draw_grass()
        for block in self.snake.body:
            if self.apple.position == block:
                self.apple.change_position()
        self.apple.draw_apple()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):  # if snake eats the apple
        if self.snake.body[0] == self.apple.position:
            self.apple.change_position()
            self.snake.enlarge()

    def game_over(self):  # game is lost if snake eats hits a wall, or its own body
        current_player = self.player
        current_score = self.snake.score
        current_player_score = {current_player: current_score}
        if current_player in score_list.keys():  # if current nickname exists -> update database
            if current_score > score_list[current_player]:
                score_list.update(current_player_score)
                query = update(Scoreboard).where(Scoreboard.nickname == str(current_player)).values(score=current_score)
                S.execute(query)
                S.commit()
        else:  # if current nickname does not exist -> create a new table record
            score_list.update(current_player_score)
            new_score = Scoreboard(nickname=current_player,
                                   score=current_score)
            S.add(new_score)
            S.commit()
        self.sorted_list = sorted(score_list.items(), key=lambda x: x[1], reverse=True)
        pygame.time.wait(360)
        self.snake.reset()

    def game_over_check(self):  # checking game over conditions
        if self.snake.body[0].x > cell_number - 1 or self.snake.body[0].x < 0 or self.snake.body[0].y < 0 or \
                self.snake.body[0].y > cell_number - 1:
            self.game_over()

        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    @staticmethod
    def draw_grass():  # simple grass structures
        dark_grass_color = (130, 180, 75)
        for column in range(cell_number):
            if column % 2 == 0:
                for row in range(cell_number):
                    if row % 2 == 0:
                        grass_rect = pygame.Rect(column * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, dark_grass_color, grass_rect)
            else:
                for row in range(cell_number):
                    if row % 2 != 0:
                        grass_rect = pygame.Rect(column * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, dark_grass_color, grass_rect)

    def draw_score(self):  # display a current score in write bottom corner
        self.snake.score = len(self.snake.body) - 2
        score_text = str(self.snake.score)
        score_surface = score_font.render(score_text, True, pygame.Color("white"))
        score_position_x = int(cell_size * cell_number) - 30
        score_position_y = int(cell_size * cell_number) - 30
        score_rect = score_surface.get_rect(center=(score_position_x, score_position_y))
        screen.blit(score_surface, score_rect)

    @staticmethod
    def quit_game():  # function tu unify a quiting procedure
        pygame.quit()
        sys.exit()

    def scoreboard_display(self):  # displaying scoreboard with top 10 highscores
        scoreboard_status = True
        screen.fill(pygame.Color('black'))
        while scoreboard_status:
            for key in pygame.event.get():
                if key.type == pygame.QUIT:
                    self.quit_game()
                if key.type == pygame.KEYDOWN:
                    if key.key == pygame.K_ESCAPE:
                        scoreboard_status = False
                        break
            display_correction = 0
            place = 0
            scoreboard_title_surface = scoreboard_title_font.render("Scoreboard", True, scoreboard_title_color)
            screen.blit(scoreboard_title_surface, (60, 10))
            for element in self.sorted_list:
                display_correction += 40
                place += 1
                if place > 10:
                    break
                text_surface = scoreboard_font.render(str(place) + ".", True, pygame.Color('white'))
                screen.blit(text_surface, (280, 80 + display_correction))
                text_surface = scoreboard_font.render(" | " + str(element[0]), True, pygame.Color('white'))
                screen.blit(text_surface, (320, 80 + display_correction))
                score_surface = scoreboard_font.render(" | " + str(element[1]), True, pygame.Color('white'))
                screen.blit(score_surface, (450, 80 + display_correction))
                pygame.display.update()


class Scoreboard(Base):  # game scores' table class
    __tablename__ = 'Scoreboard'
    id = Column(Integer, primary_key=True)
    nickname = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)


# simple connection to a database
engine = create_engine('sqlite:///Scoreboard.db', echo=True)
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
S = session()

Scores = S.query(Scoreboard).all()

for s in Scores:  # reading database and saving records to dictionary
    nickname = s.nickname
    score = s.score
    player_score = {nickname: score}
    score_list.update(player_score)

sorted_score_list = sorted(score_list.items(), key=lambda x: x[1], reverse=True)
# sorting dictionary -> will be used later to display highscores (defined above)

pygame.init()
cell_size = 40
cell_number = 20
screen_middle = Vector2(40 * 20 / 2, 40 * 20 / 2)
info_position_1 = Vector2(40 * 20 / 2, 40 * 20 / 2 - 40)
info_position_2 = Vector2(40 * 20 / 2, 40 * 20 / 2 + 60)
screen = pygame.display.set_mode((cell_size * cell_number, cell_size * cell_number))
clock = pygame.time.Clock()

apple_image = pygame.image.load('C:/Users/j1311/OneDrive/Pulpit/Projekt/apple.png')

event_update = pygame.USEREVENT
pygame.time.set_timer(event_update, 90)
pygame.time.delay(120)

# a lot of font schemas
game_font = "C:/Users/j1311/OneDrive/Pulpit/Projekt/ka1.ttf"
scoreboard_title_font = pygame.font.Font(game_font, 80)
scoreboard_font = pygame.font.Font(None, 40)
info_font_1 = pygame.font.Font(game_font, 30)
info_font_2 = pygame.font.Font(game_font, 40)
score_font = pygame.font.Font(game_font, 30)
input_font = pygame.font.Font(None, 40)
input_color = pygame.Color('lightskyblue3')
scoreboard_title_color = pygame.Color('lightskyblue3')

game = Game()
main_menu_status = True

input_text = ''
start_message_1 = 'Please write your nickname:'
start_message_2 = 'Press enter to start...'

while main_menu_status:  # Kinda starting screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.quit_game()
        if event.type == pygame.KEYDOWN:
            input_text += event.unicode
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-2]
            if event.key == pygame.K_RETURN:
                if input_text[:-1] == "":
                    player = "Guess"  # Guess is default user nickname
                else:
                    player = input_text[:-1]
                main_menu_status = False
                break

    # Some classical communicates
    screen.fill(pygame.Color('black'))

    info_surface_1 = info_font_1.render(start_message_1, True, pygame.Color('white'))
    info_correction_1 = Vector2(len(start_message_1) * 11, 160)
    screen.blit(info_surface_1, info_position_1 - info_correction_1)

    info_surface_2 = info_font_2.render(start_message_2, True, pygame.Color('white'))
    info_correction_2 = Vector2(len(start_message_1) * 12, 0)
    screen.blit(info_surface_2, info_position_2 - info_correction_2)

    input_surface = input_font.render(input_text, True, input_color)
    input_correction = Vector2(len(input_text) * 8, 120)
    screen.blit(input_surface, screen_middle - input_correction)

    pygame.display.update()
    clock.tick(60)

while True:  # main loop to operate a game functions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.quit_game()
        if event.type == event_update:
            game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.scoreboard_display()
            if event.key == pygame.K_UP:
                game.snake.move = True
                if game.snake.direction.y != 1:
                    game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN:
                game.snake.move = True
                if game.snake.direction.y != -1:
                    game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_RIGHT:
                game.snake.move = True
                if game.snake.direction.x != -1:
                    game.snake.direction = Vector2(1, 0)
            if event.key == pygame.K_LEFT:
                game.snake.move = True
                if game.snake.direction.x != 1:
                    game.snake.direction = Vector2(-1, 0)
    screen.fill((135, 185, 78))
    game.draw()
    pygame.display.update()
    clock.tick(60)  # Framerate
