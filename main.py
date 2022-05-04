# CZARNY ZAKRYSTIANIN / THE DARK SACRISTAN
# DONE:
# 1. Screen
# 2. Basic game mechanics (class Game)
# 3. Character (class Character)
# 4. Character moving
# 5. Character animation
# 6. Character shooting
# 7. Class Enemy
# 8. Introduce the first enemy

# TODO:
#  - Draw enemy sprites (ca. 2 frames each,size=32x32):
#       - the Cthulhu dogs: scale=2, health=1, waves: (4, 6, 8) - 1 frame
#       - Small Cthulhus: scale=1 health=1, waves: (8, 10, 12) - 2 frames
#       - Dzhiengas: scale=2, health=2 (changing colour after shoot or healthbar), waves: (4, 6, 8)  - 2 frames
#       - Big Cthulhus: scale=2, health=3 (a.a.), waves: (4, 6, 8) - 2 frames
#       - The Great Cthulhu: scale=4/5, health=20, one wave - 2/3 frames
#  - Add necessary methods to the Enemy class (animations, cooldowns, collision)
#  - Add collision detection to Player and Arrow;
#  - Add Enemy and Player hurt/death scenes;
#  - Add healthbar for the player;
#  - Add healthbars for enemies (?)
#  - Add scoring system and score labels;
#  - Add levels;
#  - Create title screen;
#  - Create intro (3 pictures and text, fading to black)
#  - Create five level cutscenes (fading to black)
#  - Create outro
#  - Create game over scene
#  - Introduce music (make chiptunes)
#  - Introduce sound effects
#  - Convert to .exe

#  - Further improvements incl. tiles (https://pygame.readthedocs.io/en/latest/tiles/tiles.html),
#    better OOP (an abstract class Character should be created!), parts to files, disable autofire,
#    create collectibles, different weapons, more levels, high score table etc. if necessary.
#    In the further levels maybe there could be a bigger probability that the enemies approach the player,
#    instead of just wandering at random, which can be achieved using weighed probabilities (random.choices())
#    The links should be created using the os.join() method to provide work under all OS's.



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
        # Create arrow group
        self.arrow_group = pygame.sprite.Group()
        # Create enemy
        self.enemy = Enemy(150, 150)
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
            # Update arrow group
            self.arrow_group.update()
            # Draw arrow group
            self.arrow_group.draw(self.screen)
            # Shoot if player shoots
            if self.player.shooting:
                self.player.shoot(self.arrow_group)
            # Move enemy
            self.enemy.move()
            # Draw enemy
            self.enemy.draw(self.screen)

            # TODO: update and draw enemy group

            # Move player
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
                if event.key == pygame.K_UP:
                    self.player.moving_up = True
                if event.key == pygame.K_DOWN:
                    self.player.moving_down = True
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = True
                if event.key == pygame.K_z and self.player.shoot_cooldown == 0:
                    self.player.shooting = True
                # Quitting by Esc key
                if event.key == pygame.K_ESCAPE:
                    self.settings.run = False
            # Are any keyboard buttons released?
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.moving_up = False
                if event.key == pygame.K_DOWN:
                    self.player.moving_down = False
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
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
        # Set the shoot cooldown counter
        self.shoot_cooldown = 0
        # Set health
        self.health = 10
        # Set max health
        self.max_health = 10
        # Set shoot direction
        self.shoot_direction = 180
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
        # Update action
        if self.moving_up:
            self.update_action(1)
        elif self.moving_down:
            self.update_action(3)
        elif self.moving_right:
            self.update_action(2)
        elif self.moving_left:
            self.update_action(4)
        else:
            self.update_action(0)
        # Update animation
        self.update_animation()
        # Decrease shoot cooldown counter
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # TODO: Check if alive

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

    # Shoot arrows
    def shoot(self, arrow_group):
        # Shoot arrows - instantiate Bullet next to the barrel of the gun
        # Check if the cooldown counter == 0 and ammo > 0
        # TODO: disable autofire (not very important)
        if self.shoot_cooldown == 0:
            # Set cooldown counter to 20 (it will decrease then)
            self.shoot_cooldown = 300
            self.shoot_direction = self.get_shoot_direction()
            # Create arrow
            # centerx, centery -> the middle of the player
            # player.rect.size[0] -> width of the player
            # the player.direction is 1 or -1
            arrow = Arrow(self.rect.centerx,
                          self.rect.centery,
                          self.shoot_direction)
            # Add the arrow to the arrow group
            arrow_group.add(arrow)

    # Get shooding direction
    def get_shoot_direction(self):
        if self.moving_up and not self.moving_left and not self.moving_right:
            return 0
        elif self.moving_up and self.moving_left:
            return 45
        elif self.moving_left and not self.moving_up and not self.moving_down:
            return 90
        elif self.moving_down and self.moving_left:
            return 135
        elif self.moving_down and not self.moving_right and not self.moving_left:
            return 180
        elif self.moving_down and self.moving_right:
            return 225
        elif self.moving_right and not self.moving_down and not self.moving_up:
            return 270
        elif self.moving_right and self.moving_up:
            return 315
        else:
            return 180

    # Update animation
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


# ENEMY CLASS
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=3):
        # Initialize the parent Sprite class
        super().__init__()
        # Get settings
        self.settings = Settings()
        # Check if alive
        self.alive = True
        # Set position
        self.x = x
        self.y = y
        # Set move list
        self.move_list = ["up", "up_right", "right", "down_right", "down", "down_left", "left", "up_left"]
        # Set first movement
        self.movement = random.choice(self.move_list)
        # Set speed
        self.speed = 1
        # Set health
        self.health = 10
        # Set max health
        self.max_health = 10
        # Set next move time
        self.next_move = pygame.time.get_ticks() + 3
        # Set scale
        self.scale = scale

        # # TODO: Initialize an empty animation list
        # self.animation_list = []

        # # TODO: Set frame index
        # self.frame_index = 0

        # TODO: Set action
        # (0 - idle, 1 - moving up, 2 - moving right,
        #  3 - moving left, 4 - moving right, TODO: 5 - dead)
        # self.action = 0

        # TODO: Set animation cooldown
        # self.animation_cooldown = 100

        # TODO: Set update time for updating animation (get baseline for animation sequence)
        # self.update_time = pygame.time.get_ticks()

        # TODO: Create a list of lists (OR LIST?) for animation
        # # Create a dictionary of animation types
        # animation_types = {"idle": 4, "up": 4, "right": 5, "down": 4, "left": 5}
        # # Iterate over dictionary
        # for key, value in animation_types.items():
        #     # Create/reset a temporary list of frames
        #     current_frame_list = []
        #     # Iterate over the frames from the current animation
        #     for frame_number in range(value):
        #         # Load i-th image from the specified directory
        #         img = pygame.image.load(f'assets/player_{key}_{frame_number}.png').convert_alpha()
        #         # Transform the image according to the scale
        #         img = pygame.transform.scale(img, (int(img.get_width() * self.scale),
        #                                            int(img.get_height() * self.scale)))
        #         # Add the image to the list as the next frame
        #         current_frame_list.append(img)
        #     # Append the temporary frame list to the animation list of lists
        #     self.animation_list.append(current_frame_list)

        # Set character image
        # TODO: from the animation list
        # self.image = self.animation_list[self.action][self.frame_index]
        # CURRENTLY: PROVISIONAL
        enemy_image = pygame.image.load(f'assets/lev1_0.png').convert_alpha()
        self.image = pygame.transform.scale(enemy_image, (int(enemy_image.get_width() * self.scale),
                                                          int(enemy_image.get_height() * self.scale)))
        # Get rectangle
        self.rect = self.image.get_rect()

    # # TODO: Update the state of the character
    # def update(self):
    #     # Update action
    #     if self.moving_up:
    #         self.update_action(1)
    #     elif self.moving_down:
    #         self.update_action(3)
    #     elif self.moving_right:
    #         self.update_action(2)
    #     elif self.moving_left:
    #         self.update_action(4)
    #     else:
    #         self.update_action(0)
    #     # Update animation
    #     self.update_animation()
    #     # Decrease shoot cooldown counter
    #     if self.shoot_cooldown > 0:
    #         self.shoot_cooldown -= 1
    #     # TODO: Check if alive

    # # TODO: Update the action of character
    # def update_action(self, new_action):
    #     # Check if the new action is different than the previous one
    #     # And if so - set new action
    #     if new_action != self.action:
    #         self.action = new_action
    #         # Update animation settings
    #         # Reset frame index to 0
    #         self.frame_index = 0
    #         # Set current time as the update time
    #         self.update_time = pygame.time.get_ticks()

    # Move the character
    def move(self):
        print(f"\nMovement: {self.movement}")
        print(f"X: {self.x}")
        print(f"Y: {self.y}")

        # Movement up
        if self.movement == "up" and self.y - (self.image.get_height() / 2) > 0:
            self.y -= self.speed
        elif self.movement == "up" and self.y - (self.image.get_height() / 2) <= 0:
            self.movement = random.choice(["down_left", "down", "down_right"])

        # Movement up-right
        if self.movement == "up_right" \
                and self.y - (self.image.get_height() / 2) > 0 \
                and self.x + (self.image.get_width() / 2) < self.settings.screen_width:
            self.x += self.speed
            self.y -= self.speed
        elif self.movement == "up_right" \
                and self.y - (self.image.get_height() / 2) <= 0:
            self.movement = random.choice(["down_left", "down", "down_right"])
        elif self.movement == "up_right" \
                and self.x + (self.image.get_width() / 2) <= self.settings.screen_width:
            self.movement = random.choice(["up_left", "left", "down_left"])

        # Movement up-left
        if self.movement == "up_left" \
                and self.y - (self.image.get_height() / 2) > 0 \
                and self.x - (self.image.get_width() / 2) > 0:
            self.x -= self.speed
            self.y -= self.speed
        elif self.movement == "up_left" \
                and self.y - (self.image.get_height() / 2) <= 0:
            self.movement = random.choice(["down_left", "down", "down_right"])
        elif self.movement == "up_left" \
                and self.x - (self.image.get_width() / 2) <= 0:
            self.movement = random.choice(["up_right", "right", "down_right"])

        # Movement down
        if self.movement == "down" \
                and self.y + (self.image.get_height() / 2) < self.settings.screen_height:
            self.y += self.speed
        elif self.movement == "down" \
                and self.y + (self.image.get_height() / 2) >= self.settings.screen_height:
            self.movement = random.choice(["up_left", "up", "up_right"])

        # Movement down-right
        if self.movement == "down_right" \
                and self.y + (self.image.get_height() / 2) < self.settings.screen_height \
                and self.x + (self.image.get_width() / 2) < self.settings.screen_width:
            self.x += self.speed
            self.y += self.speed
        elif self.movement == "down_right" \
                and self.y + (self.image.get_height() / 2) >= self.settings.screen_height:
            self.movement = random.choice(["up_left", "up", "up_right"])
        elif self.movement == "down_right" \
                and self.x + (self.image.get_width() / 2) >= self.settings.screen_width:
            self.movement = random.choice(["up_left", "left", "down_left"])

        if self.movement == "down_left" \
                and self.y + (self.image.get_height() / 2) < self.settings.screen_height \
                and self.x - (self.image.get_width() / 2) > 0:
            self.x -= self.speed
            self.y += self.speed
        elif self.movement == "down_left" \
                and self.y + (self.image.get_height() / 2) >= self.settings.screen_height:
            self.movement = random.choice(["up_left", "up", "up_right"])
        elif self.movement == "down_left" \
                and self.x - (self.image.get_width() / 2) >= 0:
            self.movement = random.choice(["up_right", "right", "down_right"])

        if self.movement == "right" and self.x + (self.image.get_width() / 2) < self.settings.screen_width:
            self.x += self.speed
        elif self.movement == "right" and self.x + (self.image.get_width() / 2) >= self.settings.screen_width:
            self.movement = random.choice(["up_left", "left", "down_left"])

        if self.movement == "left" and self.x - (self.image.get_width() / 2) > 0:
            self.x -= self.speed
        elif self.movement == "left" and self.x - (self.image.get_width() / 2) <= 0:
            self.movement = random.choice(["up_right", "right", "down_right"])

    # # TODO: Update animation
    # def update_animation(self):
    #     # Change the animation's index after a short time.
    #     # Update image depending on current action and frame index
    #     self.image = self.animation_list[self.action][self.frame_index]
    #     # Animation cooldown
    #     if self.action == 0:
    #         self.animation_cooldown = 500
    #     else:
    #         self.animation_cooldown = 100
    #     # Check if enough time has passed since the last update
    #     if pygame.time.get_ticks() - self.update_time > self.animation_cooldown:
    #         # Reset the animation timer
    #         self.update_time = pygame.time.get_ticks()
    #         # Add 1 to frame index to choose the next animation frame
    #         self.frame_index += 1
    #     # If the animation list for current action has run out of frames,
    #     # reset frame index back to 0
    #     if self.frame_index >= len(self.animation_list[self.action]):
    #         self.frame_index = 0

    # Draw the character on the screen
    def draw(self, screen):
        self.rect.center = vec(self.x, self.y)
        screen.blit(self.image, self.rect)


# ARROW CLASS
class Arrow(pygame.sprite.Sprite):
    # Create the constructor for the Bullet class
    # (args: x, y -> coordinates,
    #        direction -> angle
    def __init__(self, x, y, direction):
        # Initialize Sprite
        super().__init__()
        # Set settings
        self.settings = Settings()
        # Set speed (in this case all bullets have the same speed)
        self.speed = 1
        # Set direction
        self.direction = direction
        # Set next move
        self.next_move = pygame.time.get_ticks() + 2
        # Set arrow image (pointing at proper direction)
        upright_arrow = pygame.image.load(f'assets/arrow.png').convert_alpha()
        self.image = pygame.transform.rotate(upright_arrow, self.direction)
        # Create rectangle for the arrow
        self.rect = self.image.get_rect()
        # Set position of the rectangle's center
        self.rect.center = (x, y)

    def update(self):
        # Move bullet left, right, up, down or diagonally at the bullet's speed
        if pygame.time.get_ticks() >= self.next_move:
            self.next_move = pygame.time.get_ticks() + 2
            if self.direction == 0:
                self.rect.y -= self.speed
            if self.direction == 45:
                self.rect.y -= self.speed
                self.rect.x -= self.speed
            if self.direction == 90:
                self.rect.x -= self.speed
            if self.direction == 135:
                self.rect.x -= self.speed
                self.rect.y += self.speed
            if self.direction == 180:
                self.rect.y += self.speed
            if self.direction == 225:
                self.rect.y += self.speed
                self.rect.x += self.speed
            if self.direction == 270:
                self.rect.x += self.speed
            if self.direction == 315:
                self.rect.x += self.speed
                self.rect.y -= self.speed

        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > self.settings.screen_width or self.rect.bottom < 0 or \
                self.rect.top > self.settings.screen_height:
            # Delete the bullet, if it's off screen
            # The method .kill is inherited from the Sprite class
            self.kill()

        # Check collision of the bullet with player
        # TODO: update all this. How to pass in a player object? Is it really a good idea?
        #  See some tutorials on bullet shooting to solve this problem.
        #  Maybe the collision check should be in the Game class? It seems so!
        # Args: sprite -> sprite which collides
        #       group -> group of sprites to collide with
        #       dokill -> remove automatically each collided sprite from the group
        # NOTE: mask not used! Collides with rect (to improve later)
        # If the bullet hits the player:
        # if pygame.sprite.spritecollide(sprite=player, # TODO: ???
        #                                group=arrow_group, # TODO: ???
        #                                dokill=False):
        #     # If the player is alive:
        #     if player.alive:
        #         # Decrease player's health by 5
        #         player.health -= 5
        #         # Delete bullet
        #         self.kill()
        # # Check collision of the bullet with enemy
        # if pygame.sprite.spritecollide(sprite=enemy,
        #                                group=bullet_group,
        #                                dokill=False):
        #     # Delete bullet if the enemy is alive
        #     if enemy.alive:
        #         # Decrease enemy health by 25
        #         enemy.health -= 25
        #         # Delete bullet
        #         self.kill()


# RUN GAME
game = Game()
if __name__ == "__main__":
    game.run()
