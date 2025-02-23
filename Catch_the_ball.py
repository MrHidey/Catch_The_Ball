import os
import pygame
import sys
import random
import datetime
import mysql.connector
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv('.env')

# Access the variables using os.getenv()
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Function to connect to the database
def connect_db():
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    return connection

# Function to save the result to the database
def save_result(connection, GameNo, Score, Date_time):
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO ScoreTable (GameNo, Score, Date_time) VALUES (%s, %s, %s)"
        cursor.execute(query, (GameNo, Score, Date_time))
        connection.commit()
        cursor.close()

pygame.init()
pygame.mixer.init()

# Database connection
db = connect_db()
GameNo = 1
Date_time = datetime.datetime.now()

# Set up the game window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = pygame.display.get_surface().get_size()

# Game constants
FPS = 120
WHITE = (255, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player attributes
player_size = 75
player_image_path = "Player.png"
player_image = pygame.image.load(player_image_path)
player_image = pygame.transform.scale(player_image, (player_size, player_size))

player_x = (WIDTH - player_size) // 2
player_y = (HEIGHT - player_size) - 30

# Falling object attributes
object_size = 50
object_image_path = "object.png"
object_image = pygame.image.load(object_image_path)
object_image = pygame.transform.scale(object_image, (object_size, object_size))

object_speed = 3
object_x = random.randint(0, WIDTH - object_size)
object_y = 0

# Rotation angle for the falling object
rotation_angle = 0

# Initialize fonts
font_path = "NevisBold-KGwl.ttf"
font = pygame.font.Font(font_path, 25)

# Initialize sound effects
miss_sound_path = "jump-15984.mp3"
miss_sound = pygame.mixer.Sound(miss_sound_path)

# Background music
music_path = "Run-Amok(chosic.com).mp3"
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)

# Display an introduction screen
screen.fill(WHITE)
intro_font = pygame.font.Font("kn.otf", 120)
intro_text = intro_font.render("Catch the Ball", True, RED)
intro_rect = intro_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(intro_text, intro_rect)

pygame.display.flip()

# Wait for a key press to start the game
waiting_for_start = True
while waiting_for_start:
    for event in pygame.event.get():
        if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
            waiting_for_start = False
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# Game variables
score = 0
life = 5
increment = 10

# Find the highest score
highest_score = 0
if db:
    cursor = db.cursor()
    query = "SELECT MAX(Score) FROM ScoreTable"
    cursor.execute(query)
    result = cursor.fetchone()
    if result and result[0] is not None:
        highest_score = result[0]
    cursor.close()

# Game loop
clock = pygame.time.Clock()

while life > 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
            pygame.quit()
            sys.exit()

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 8
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += 8

    # Falling object movement
    object_y += object_speed
    rotation_angle += 0.4

    # Reset falling object when it hits the ground
    if object_y > HEIGHT:
        object_y = 0
        object_x = random.randint(0, WIDTH - object_size)
        life -= 1
        miss_sound.play()
        rotation_angle = 0

        # Adjust speed based on score
        if score >= 150:
            object_speed = 4
        elif score >= 300:
            object_speed = 5
        elif score >= 700:
            object_speed = 6

    # Collision detection
    rotated_object_image = pygame.transform.rotate(object_image, rotation_angle)
    rotated_object_rect = rotated_object_image.get_rect(topleft=(object_x, object_y))
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    if player_rect.colliderect(rotated_object_rect):
        object_y = 0
        object_x = random.randint(0, WIDTH - object_size)
        score += increment
        if score > highest_score:
            highest_score = score

    # Drawing to the screen
    screen.fill(WHITE)
    screen.blit(rotated_object_image, (object_x, object_y))
    screen.blit(player_image, (player_x, player_y))

    # Display scores and lives
    score_text = font.render(f"Score: {score}", True, BLUE)
    screen.blit(score_text, (10, 10))

    highest_score_text = font.render(f"Highest Score: {highest_score}", True, BLUE)
    screen.blit(highest_score_text, (10, 50))

    life_text = font.render(f"Life: {life}", True, BLUE)
    screen.blit(life_text, (10, 90))

    pygame.display.flip()

    clock.tick(FPS)

# Game over screen
game_over_font = pygame.font.Font(font_path, 100)
game_over_text = game_over_font.render("Game Over!", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(game_over_text, game_over_rect)
pygame.display.flip()

pygame.time.delay(3000)

# Save the game result to the database
save_result(db, GameNo, score, Date_time)

pygame.quit()
sys.exit()
