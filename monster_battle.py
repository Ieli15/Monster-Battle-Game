import os
import pygame
import random

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monster Battle")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)

font = pygame.font.Font(None, 36)

# Load assets
background_img = pygame.image.load("assets/background_image.jpeg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

player_img = pygame.image.load("assets/player_monster.png")
player_img = pygame.transform.scale(player_img, (250, 250))

enemy_img = pygame.image.load("assets/enemy_monster.png")
enemy_img = pygame.transform.scale(enemy_img, (250, 250))

# Load sounds
light_attack_sound = pygame.mixer.Sound("assets/light_attack.mp3")
heavy_attack_sound = pygame.mixer.Sound("assets/heavy_attack.mp3")
miss_sound = pygame.mixer.Sound("assets/miss.mp3")
win_music = "assets/victory_music.mp3"
lose_music = "assets/defeat_music.mp3"

pygame.mixer.music.load("assets/background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop background music

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = font.render(text, True, BLACK)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.rect.collidepoint(mouse_pos) else self.color, self.rect)
        screen.blit(self.text, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Draw health bars
def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 200, 20))
    pygame.draw.rect(screen, GREEN, (x, y, int(200 * (health / max_health)), 20))

# Player attack logic
def player_attack(attack_type):
    global enemy_health
    if attack_type == "light":
        damage = random.randint(5, 15)
        if random.random() < 0.2:
            damage *= 2
            print("Critical Hit!")
        light_attack_sound.play()
    else:
        if random.random() < 0.7:
            damage = random.randint(15, 25)
            if random.random() < 0.2:
                damage *= 2
                print("Critical Hit!")
            heavy_attack_sound.play()
        else:
            print("Heavy attack missed!")
            miss_sound.play()
            if random.random() < 0.5:
                counter_damage = random.randint(10, 20)
                global player_health
                player_health = max(0, player_health - counter_damage)
                print(f"Enemy counterattacks for {counter_damage} damage!")
            return
    enemy_health = max(0, enemy_health - damage)
    print(f"Player used {attack_type} attack for {damage} damage!")

# Enemy attack logic
def enemy_attack():
    global player_health, enemy_health
    if enemy_health < 30 and random.random() < 0.5:
        heal_amount = random.randint(10, 20)
        enemy_health = min(100, enemy_health + heal_amount)
        print(f"Enemy healed {heal_amount} HP!")
    else:
        damage = random.randint(15, 25) if (player_health < 40 and random.random() < 0.6) else random.randint(5, 15)
        print("Enemy used a heavy attack!" if damage > 15 else "Enemy used a light attack!")

        if random.random() < 0.2:
            damage *= 2
            print("Enemy lands a Critical Hit!")

        player_health = max(0, player_health - damage)
        print(f"Enemy attacks for {damage} damage!")

# Healing logic
def use_potion():
    global player_health, potions
    if potions > 0:
        heal_amount = random.randint(15, 30)
        player_health = min(100, player_health + heal_amount)
        potions -= 1
        print(f"Player used a potion! Healed {heal_amount} HP. ({potions} left)")
    else:
        print("No potions left!")

# Game over screen
def show_game_over(message, won):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(win_music if won else lose_music)
    pygame.mixer.music.play()
    screen.fill(WHITE)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(3000)
    pygame.quit()

# Main battle loop
def battle():
    global player_health, enemy_health, potions
    running = True
    player_health = 100
    enemy_health = 100
    potions = 2
    turn = "player"

    # Create buttons
    light_attack_button = Button(50, 500, 200, 50, "Light Attack", GREEN, LIGHT_GRAY, lambda: player_attack("light"))
    heavy_attack_button = Button(300, 500, 200, 50, "Heavy Attack", RED, LIGHT_GRAY, lambda: player_attack("heavy"))
    heal_button = Button(550, 500, 200, 50, "Heal (P)", BLUE, LIGHT_GRAY, use_potion)
    buttons = [light_attack_button, heavy_attack_button, heal_button]

    while running:
        screen.blit(background_img, (0, 0))  
        screen.blit(player_img, (100, 200))  # Fix: Added player image
        screen.blit(enemy_img, (550, 200))  

        draw_health_bar(50, 50, player_health, 100)
        draw_health_bar(550, 50, enemy_health, 100)

        player_text = font.render("Player", True, BLACK)
        enemy_text = font.render("Enemy", True, BLACK)
        screen.blit(player_text, (50, 20))
        screen.blit(enemy_text, (550, 20))

        for button in buttons:
            button.draw()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        button.action()
                        turn = "enemy"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    player_attack("light")
                    turn = "enemy"
                elif event.key == pygame.K_h:
                    player_attack("heavy")
                    turn = "enemy"
                elif event.key == pygame.K_p:
                    use_potion()

        if turn == "enemy":
            enemy_attack()
            turn = "player"

        if player_health <= 0:
            show_game_over("You Lost!", False)
            running = False
        elif enemy_health <= 0:
            show_game_over("You Won!", True)
            running = False

battle()
