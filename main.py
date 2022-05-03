# CZARNY ZAKRYSTIANIN / THE DARK SACRISTAN
# DONE:
# 1. Screen
# 2. Basic game mechanics (class Game)
# 3. Character (class Character)
# 4. Character moving
# 5. Character animation

# TODO:
#  6. Shooting
#  7. First level - tiles (?), enemies, collisions
#  8. Other levels
#  9. Music and sound effects
#  10. Outro
#  11. Convert to .exe
#  12. Further improvements incl. better OOP, parts to files etc.

# IMPORT NECESSARY MODULES
import pygame
import os
import random
from settings import Settings

# INITIALIZE PYGAME
pygame.init()
vec = pygame.math.Vector2


# CLASS GAME
class Game:
    # Initialize game
    def __init__(self):
        # Get settings
        self.settings = Settings()
        # Set up the screen
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        # Set the caption
        pygame.display.set_caption("Czarny Zakrystianin")
        # Set the game clock
        self.clock = pygame.time.Clock()
        # Instantiate player
        self.player = Character(100, 100)
        # Set level
        self.level = 0

    # Draw the background
    def draw_background(self):
        self.screen.fill(self.settings.screen_color)

    # Run the game
    def run(self):
        # Set the clock for 60 frames per second
        self.clock.tick(self.settings.fps)

        # Main loop
        while self.settings.run:
            # Listen for events
            self.check_events()
            # Draw background
            self.draw_background()
            # Update player
            self.player.update()
            # Draw player
            self.player.draw(self.screen)
            # TODO: update and draw enemies and bullets

            # Update action
            if self.player.moving_up:
                self.player.update_action(1)
            elif self.player.moving_right:
                self.player.update_action(2)
            elif self.player.moving_down:
                self.player.update_action(3)
            elif self.player.moving_left:
                self.player.update_action(4)
            else:
                self.player.update_action(0)

            # Move player (TODO: it's provisional. There should be an update _and_ a move method in Player class)
            if pygame.time.get_ticks() >= self.player.next_move:
                self.player.move()
                self.player.next_move = pygame.time.get_ticks() + 3

            # Update display
            pygame.display.update()

    # Event listener
    def check_events(self):
        for event in pygame.event.get():
            # Check for quitting
            if event.type == pygame.QUIT:
                self.settings.run = False
        # Player control.
        # Are any keyboard buttons pressed?
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = True
                if event.key == pygame.K_UP:
                    self.player.moving_up = True
                if event.key == pygame.K_DOWN:
                    self.player.moving_down = True
                if event.key == pygame.K_z:
                    self.player.shooting = True
                # Quitting by Esc key
                if event.key == pygame.K_ESCAPE:
                    self.settings.run = False
            # Are any keyboard buttons released?
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
                if event.key == pygame.K_UP:
                    self.player.moving_up = False
                if event.key == pygame.K_DOWN:
                    self.player.moving_down = False
                if event.key == pygame.K_z:
                    self.player.shooting = False


# CLASS CHARACTER
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=2):
        # Initialize the parent Sprite class
        super().__init__()
        # Get settings
        self.settings = Settings()
        # Check if alive
        self.alive = True
        # Set position
        self.x = x
        self.y = y
        # Set movement markers
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.shooting = False
        # Set speed
        self.speed = 1
        # Set health
        self.health = 10
        # Set max health
        self.max_health = 10
        # Initialize an empty animation list
        self.animation_list = []
        # Set frame index
        self.frame_index = 0
        # Set next move time
        self.next_move = pygame.time.get_ticks() + 3
        # Set action
        # (0 - idle, 1 - moving up, 2 - moving right,
        #  3 - moving left, 4 - moving right, TODO: 5 - dead)
        self.action = 0
        # Set animation cooldown
        self.animation_cooldown = 100
        # Set scale
        self.scale = scale
        # Set update time for updating animation (get baseline for animation sequence)
        self.update_time = pygame.time.get_ticks()

        # Create a list of lists for animation
        # Create a dictionary of animation types
        animation_types = {"idle": 4, "up": 4, "right": 5, "down": 4, "left": 5}
        # Iterate over dictionary
        for key, value in animation_types.items():
            # Create/reset a temporary list of frames
            current_frame_list = []
            # Iterate over the frames from the current animation
            for frame_number in range(value):
                # Load i-th image from the specified directory
                img = pygame.image.load(f'assets/player_{key}_{frame_number}.png').convert_alpha()
                # Transform the image according to the scale
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale),
                                                   int(img.get_height() * self.scale)))
                # Add the image to the list as the next frame
                current_frame_list.append(img)
            # Append the temporary frame list to the animation list of lists
            self.animation_list.append(current_frame_list)

        # Set character image
        self.image = self.animation_list[self.action][self.frame_index]
        # Get rectangle
        self.rect = self.image.get_rect()

    # Update the state of the character
    def update(self):
        # Update animation
        self.update_animation()
        # TODO: Check if alive, decrease the shoot cooldown counter etc.

    # Update the action of character
    def update_action(self, new_action):
        # Check if the new action is different than the previous one
        # And if so - set new action
        if new_action != self.action:
            self.action = new_action
            # Update animation settings
            # Reset frame index to 0
            self.frame_index = 0
            # Set current time as the update time
            self.update_time = pygame.time.get_ticks()

    # Move the character
    def move(self):
        if self.moving_up and (self.y - (self.image.get_height() / 2)) > 0:
            self.y -= self.speed
        if self.moving_down and (self.y + (self.image.get_height() / 2)) < self.settings.screen_height:
            self.y += self.speed
        if self.moving_left and (self.x - (self.image.get_width() / 2)) > 0:
            self.x -= self.speed
        if self.moving_right and (self.x + (self.image.get_width() / 2)) < self.settings.screen_width:
            self.x += self.speed

    # Define a method for updating animation
    def update_animation(self):
        # Change the animation's index after a short time.
        # Update image depending on current action and frame index
        self.image = self.animation_list[self.action][self.frame_index]
        # Animation cooldown
        if self.action == 0:
            self.animation_cooldown = 500
        else:
            self.animation_cooldown = 100
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.animation_cooldown:
            # Reset the animation timer
            self.update_time = pygame.time.get_ticks()
            # Add 1 to frame index to choose the next animation frame
            self.frame_index += 1
        # If the animation list for current action has run out of frames,
        # reset frame index back to 0
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    # Draw the character on the screen
    def draw(self, screen):
        self.rect.center = vec(self.x, self.y)
        screen.blit(self.image, self.rect)


# RUN GAME
game = Game()
if __name__ == "__main__":
    game.run()
