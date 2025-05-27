import pygame
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280, 1280
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Defense Game")

font = pygame.font.SysFont("Arial", 32)
clock = pygame.time.Clock()
asteroid_image = pygame.image.load("assets/asteroid.jpg")
asteroid_image = pygame.transform.scale(asteroid_image, (150, 150))  # Resize if needed
explosion_img = pygame.image.load("assets/explosion.jpg")
explosion_img = pygame.transform.scale(explosion_img, (150, 150))  # Match falling object size

# Falling object class
class WordObject:
    def __init__(self, word, x, y, speed, image):
        self.word = word
        self.x = x
        self.y = y
        self.speed = speed
        self.image = image
        self.typed = ""

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        # Draw image
        surface.blit(self.image, (self.x, self.y))
        
        # Draw word centered on image
        text = font.render(self.word, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x + self.image.get_width() // 2,
                                        self.y + self.image.get_height() // 2))
        surface.blit(text, text_rect)
    
    def is_hit(self):
        return self.typed == self.word

    def has_reached_ground(self):
        return self.y > HEIGHT - 50

# Explosion class
class Explosion:
    def __init__(self, x, y, image, duration=15):  # duration = frames
        self.x = x
        self.y = y
        self.image = image
        self.timer = duration

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_done(self):
        return self.timer <= 0

# Word list and setup
words = ["apple", "banana", "cherry", "door", "cat", "dog", "elephant", "frog", "grape"]
falling_objects = []
explosions = []
spawn_delay = 60
frame_count = 0
game_active = False
game_over = False


input_buffer = ""

# Game loop
running = True
destroyed_count = 0
missed_count = 0
while running:
    screen.fill((0, 0, 30))  # Dark blue background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- CLICK TO START ---
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_active:
            game_active = True

        elif event.type == pygame.KEYDOWN and game_active:
            if event.unicode.isalpha():
                input_buffer += event.unicode
            elif event.key == pygame.K_BACKSPACE:
                input_buffer = input_buffer[:-1]
            elif event.key == pygame.K_RETURN:
                for obj in falling_objects:
                    if obj.word.startswith(input_buffer):
                        obj.typed = input_buffer
                        if obj.is_hit():
                            print(f"Destroyed: {obj.word}")
                            # Add explosion here
                            explosions.append(Explosion(obj.x, obj.y, explosion_img))
                            falling_objects.remove(obj)
                            destroyed_count += 1
                            break
                input_buffer = ""

    # --- IF GAME IS NOT ACTIVE: Show Start Screen ---
    if not game_active and not game_over:
        title_text = font.render("Typing Defense Game", True, (255, 255, 255))
        prompt_text = font.render("Click to Play", True, (100, 255, 100))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()

    # --- IF GAME IS ACTIVE: Run Game Logic ---
    elif game_active:
        
        # Spawn new words
        frame_count += 1
        if frame_count % spawn_delay == 0:
            new_word = random.choice(words)
            x = random.randint(50, WIDTH - 150)
            falling_objects.append(WordObject(new_word, x, 0, speed=2, image=asteroid_image))

        # Update & draw explosions
        for explosion in explosions[:]:
            explosion.update()
            explosion.draw(screen)
            if explosion.is_done():
                explosions.remove(explosion)

        # Update and draw falling objects
        for obj in falling_objects[:]:
            obj.update()
            obj.draw(screen)
            if obj.has_reached_ground():
                print(f"Missed: {obj.word}")
                missed_count += 1
                falling_objects.remove(obj)

        # Draw input text
        input_text = font.render(">" + input_buffer, True, (0, 255, 0))
        screen.blit(input_text, (20, HEIGHT - 40))
        if missed_count >= 10:
            game_active = False
            game_over = True
        pygame.display.flip()
        clock.tick(60)
        word_count = destroyed_count + missed_count

    elif not game_active and game_over:
        # 🔴 GAME OVER SCREEN
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        stats_text = font.render(f"Destroyed: {destroyed_count}  Missed: {missed_count}", True, (255, 255, 255))
        restart_text = font.render("Click to Restart", True, (0, 255, 0))

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))
        pygame.display.flip()

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if not game_active and not game_over:
            game_active = True  # Start game for the first time
            destroyed_count = 0
            missed_count = 0
            falling_objects.clear()
            explosions.clear()
            input_buffer = ""
        elif game_over:
            # Restart game after game over
            game_active = True
            game_over = False
            destroyed_count = 0
            missed_count = 0
            falling_objects.clear()
            explosions.clear()
            input_buffer = ""

print(" you destroyed:", destroyed_count, "( %.2f%%" % (100*float(destroyed_count)/word_count), ")", "you missed:", missed_count, "( %.2f%%" % (100*float(missed_count)/word_count), ")")

pygame.quit()
