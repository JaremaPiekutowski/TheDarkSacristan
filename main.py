# CZARNY ZAKRYSTIANIN / THE DARK SACRISTAN
# DONE:
# 1. Screen
# 2. Basic game mechanics, main loop (class Game)
# 3. Player (class Player)
# 4. Player sprites
# 4. Player moving
# 5. Player animation
# 6. Player shooting
# 7. Class Enemy
# 8. The first enemy
# 9. Collision detection between player and enemy
# 10. Death animation and GAME OVER label
# 11. A provisional title screen
# 12. Drawn images of all enemies
# 13. Provisional enemy death scene
# 14. Collision arrow/enemy
# 15. Level cutscenes added (provisional)
# 16. Health system added
# 17. Hit and death animations introduced

# TODO:
#  - Introduce music (make chiptunes)
#  - Introduce sound effects
#  - Create final title screen with a picture;
#  - Create instructions screen;
#  - Create intro (3 pictures and text, fading to black)
#  - Create five level cutscenes (fading to black)
#  - Create outro
#  - Check for provisional solutions
#  - Convert to .exe

#  - Further improvements incl. tiles (https://pygame.readthedocs.io/en/latest/tiles/tiles.html),
#    better OOP (an abstract class Player should be created!), parts to files, disable autofire,
#    create collectibles, different weapons, more levels, high score table, full screen mode,
#    waves, enemy groups etc. if necessary.
#
#    In the further levels maybe there could be a bigger probability that the enemies approach the player,
#    instead of just wandering at random, which can be achieved using weighed probabilities (random.choices())
#
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
        # Set the game clock
        self.clock = pygame.time.Clock()
        # Set up the screen
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        # Set the caption
        pygame.display.set_caption("Czarny Zakrystianin")
        # Set level
        self.level = 0
        # Instantiate player
        self.player = Player(100, 100)
        # Create arrow group
        self.arrow_group = pygame.sprite.Group()
        # Create enemy
        self.enemy = Enemy(700, 300, self.level)
        # Set font for game over
        self.game_over_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 40)
        # Set game over label
        self.game_over_label = self.game_over_font.render("GAME OVER", True, (0, 0, 0))
        # Set font for health
        self.health_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 20)
        # Set game over cooldown
        self.game_over_cooldown = 0
        # Set if new level starts
        self.new_level_starts = True

    # Draw the background
    def draw_background(self, color):
        self.screen.fill(color)
        self.screen.blit(self.health_font.render(f"ENEMY HEALTH: {self.enemy.health}", True, (0, 0, 0)),
                         (2, 2))

    # Run the game
    def run(self):
        # Set level
        self.level = 0

        # Set the clock for 60 frames per second
        self.clock.tick(self.settings.fps)

        # Main menu
        self.main_menu()

        # Main loop
        while self.settings.game_run:
            # Listen for level beginnings
            if self.new_level_starts:
                self.new_level_setting()
            # Listen for events
            self.check_events()
            # Draw background
            self.draw_background(self.settings.game_screen_color)
            # Update player
            self.player.update()
            # Draw player
            self.player.draw(self.screen)
            # Update arrow group
            self.arrow_group.update()
            # Draw arrow group
            self.arrow_group.draw(self.screen)
            # Shoot if player shoots
            if self.player.alive and self.player.shooting:
                self.player.shoot(self.arrow_group)
            # Update enemy animation
            self.enemy.update_animation()
            # Move enemy
            if pygame.time.get_ticks() >= self.enemy.next_move and self.enemy.alive:
                self.enemy.move()
                self.enemy.next_move = pygame.time.get_ticks() + 3
            # Draw enemy
            if self.enemy.alive:
                self.enemy.draw(self.screen)
            # ...or draw enemy explosion
            elif not self.enemy.alive and not self.enemy.explosion_coooldown_over:
                self.enemy.update_animation()
                self.enemy.draw(self.screen)
            # ...or go to the  next level
            elif not self.enemy.alive and self.enemy.explosion_coooldown_over:
                self.player.kill()
                for arrow in self.arrow_group:
                    arrow.kill()
                self.new_level_starts = True
                if self.level < 4:
                    self.level += 1
                # TODO: PROVISIONAL. DO: "ELSE -> OUTRO" IN THE FUTURE.
            # Move player
            if pygame.time.get_ticks() >= self.player.next_move and self.player.alive:
                self.player.move()
                self.player.next_move = pygame.time.get_ticks() + 3
            # Check collision of player with the enemy
            self.check_collisions()
            # TODO: PROVISIONAL Check for game over
            if not self.player.alive and self.player.death_animation_over:
                self.game_over()
            # Update display
            pygame.display.update()

    # Event listener
    def check_events(self):
        for event in pygame.event.get():
            # Check for quitting
            if event.type == pygame.QUIT:
                self.settings.game_run = False
            # Player control.
            # Are any keyboard buttons pressed?
            if self.player.alive:
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
                        self.settings.game_run = False
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

    def check_collisions(self):
        # Collision of arrow group and enemy
        colliding_arrows_list = pygame.sprite.spritecollide(self.enemy, self.arrow_group, dokill=True)
        if len(colliding_arrows_list) != 0:
            self.enemy.hit = True
            self.enemy.frame_index = 0
            self.enemy.health -= 1
            if self.enemy.health == 0:
                self.enemy.die()

        # Collision of player and enemy
        if pygame.sprite.collide_rect(self.player, self.enemy) and self.player.alive and self.enemy.alive:
            self.player.alive = False
            self.game_over_cooldown = pygame.time.get_ticks() + 4000

    def main_menu(self):
        # Set font for labels on the title screen
        title_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 40)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 30)
        # Loop for the main menu
        main_menu_run = True
        while main_menu_run:
            # Put labels on the screen
            title_label = title_font.render("CZARNY ZAKRYSTIANIN", True, (255, 0, 0))
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.blit(title_label, (self.settings.screen_width / 2 - title_label.get_width() / 2,
                                           self.settings.screen_height * 0.2))
            self.screen.blit(pushbutton_label, (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                                                self.settings.screen_height * 0.8))
            # Update display
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    main_menu_run = False
                if event.type == pygame.KEYDOWN:
                    print("Key pressed!")
                    main_menu_run = False

    def level_cutscene(self, level):
        # Set font for labels on the title screen
        title_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 40)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 30)
        level_cutscene_run = True
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        print("Started new cutscene")
        pygame.time.delay(1000)
        print("After delay")
        while level_cutscene_run:
            # Background fill
            self.screen.fill((0, 0, 0))
            # Put labels on the screen
            title_label = title_font.render(f"LEVEL {level + 1}", True, (255, 0, 0))
            # TODO: PROVISIONAL, AN IMAGE SHOULD BE THERE!
            image_provisional_label = title_font.render("IMAGE IN PROGRESS", True, (46, 224, 150))
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.blit(title_label,
                             (self.settings.screen_width / 2 - title_label.get_width() / 2,
                              self.settings.screen_height * 0.2))
            self.screen.blit(image_provisional_label,
                             (self.settings.screen_width / 2 - image_provisional_label.get_width() / 2,
                              self.settings.screen_height * 0.5))
            self.screen.blit(pushbutton_label,
                                 (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                                  self.settings.screen_height * 0.9))
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    level_cutscene_run = False
                if event.type == pygame.KEYDOWN:
                    level_cutscene_run = False

    def new_level_setting(self):
        self.level_cutscene(self.level)
        self.enemy = Enemy(x=700, y=300, level=self.level)
        self.player = Player(x=100, y=100)
        self.player.moving_up = False
        self.player.moving_down = False
        self.player.moving_left = False
        self.player.moving_right = False
        self.player.shooting = False
        self.new_level_starts = False

    def game_over(self):
        if pygame.time.get_ticks() < self.game_over_cooldown:
            self.screen.blit(self.game_over_label,
                             (self.settings.screen_width / 2 - self.game_over_label.get_width() / 2,
                              self.settings.screen_height * 0.5))
        else:
            self.player.kill()
            self.enemy.kill()
            for arrow in self.arrow_group:
                arrow.kill()
            self.draw_background((0, 0, 0))
            pygame.display.update()
            self.player = Player(100, 100)
            self.level = 0
            self.new_level_starts = True
            self.player.moving_up = False
            self.player.moving_down = False
            self.player.moving_left = False
            self.player.moving_right = False
            self.player.shooting = False
            self.main_menu()


# CLASS PLAYER
class Player(pygame.sprite.Sprite):
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
        # (0 - idle, 1 - moving up, 2 - moving down,
        #  3 - moving left, 4 - moving right, 5 - dead TODO: CHANGE,
        #  6 - up right, 7 - up left, 8 - down right, 9 - down left)
        # THERE SHOULD ACTUALLY BE FOUR "IDLES": FACING UP, RIGHT, DOWN AND LEFT
        self.action = 0
        # Set animation cooldown
        self.animation_cooldown = 100
        # Set scale
        self.scale = scale
        # Set update time for updating animation (get baseline for animation sequence)
        self.update_time = pygame.time.get_ticks()
        # Set death animation cooldown
        self.death_animation_over = False

        # Create a list of lists for animation
        # Create a dictionary of animation types
        animation_types = {"idle": 4, "up": 4, "right": 5, "down": 4, "left": 5, "dead": 6}
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

        # Add the same images ("up" and "down") for diagonal movement
        # TODO: I know it's stupid but I do it only for time purposes
        animation_types_diagonal = {"up": 4, "down": 4}
        for _ in range(2):
            for key, value in animation_types_diagonal.items():
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

        # Set player image
        self.image = self.animation_list[self.action][self.frame_index]
        # Get rectangle
        self.rect = self.image.get_rect()

    # Update the state of the player
    def update(self):
        # Update action
        if self.alive:
            if self.moving_up and not self.moving_left and not self.moving_right:
                self.update_action(1)
            elif self.moving_right and not self.moving_up and not self.moving_down:
                self.update_action(2)
            elif self.moving_down and not self.moving_left and not self.moving_right:
                self.update_action(3)
            elif self.moving_left and not self.moving_up and not self.moving_down:
                self.update_action(4)
            elif self.moving_up and self.moving_right:
                self.update_action(6)
            elif self.moving_down and self.moving_right:
                self.update_action(7)
            elif self.moving_up and self.moving_left:
                self.update_action(8)
            elif self.moving_down and self.moving_left:
                self.update_action(9)
        else:
            self.update_action(5)
        if not self.moving_up and not self.moving_down and not self.moving_right \
                and not self.moving_left and not self.action == 0 and self.alive:
            self.image = self.animation_list[self.action][0]
        else:
            self.update_animation()
        # Decrease shoot cooldown counter
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    # Update the action of the player
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

    # TODO: Check if the player is alive (?)

    # Move the player
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
            # TODO: SHOULDN'T THE ARROW GROUP BE AN ATTRIBUTE OF THE PLAYER?
            arrow_group.add(arrow)
            # Set shooting to False to prevent shooting more than one arrow
            self.shooting = False

    # Get shooding direction
    def get_shoot_direction(self):
        if self.action == 1:  # if self.moving_up and not self.moving_left and not self.moving_right:
            return 0
        elif self.action == 9:
            return 135
        elif self.action == 4:
            return 90
        elif self.action == 8:
            return 45
        elif self.action == 3:
            return 180
        elif self.action == 7:
            return 225
        elif self.action == 2:
            return 270
        elif self.action == 6:
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
        # If the animation list for current action has game_run out of frames,
        # reset frame index back to 0
        if self.frame_index >= len(self.animation_list[self.action]) and self.action != 5:
            self.frame_index = 0
        elif self.frame_index >= len(self.animation_list[self.action]) and self.action == 5:
            self.frame_index = len(self.animation_list[self.action]) - 1
            self.death_animation_over = True

    # Draw the player on the screen
    def draw(self, screen):
        self.rect.center = vec(self.x, self.y)
        screen.blit(self.image, self.rect)


# ENEMY CLASS
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        # Initialize the parent Sprite class
        super().__init__()
        # Set position
        self.x = x
        self.y = y
        # Set level
        self.level = level
        # Set scale based on a level/scale dictionary
        level_scale_dict = {0: 5, 1: 6, 2: 6, 3: 6, 4: 7}
        self.scale = level_scale_dict[self.level]
        # Get settings
        self.settings = Settings()
        # Check if alive
        self.alive = True
        # Set move list
        self.move_list = ["up", "up_right", "right", "down_right", "down", "down_left", "left", "up_left"]
        # Set first movement
        self.movement = random.choice(self.move_list)
        # Set speed
        self.speed = 1
        # Set if hit
        self.hit = False
        # Set health
        self.health = 3
        # Set max health
        self.max_health = 10
        # Set next move time
        self.next_move = pygame.time.get_ticks() + 3
        # Set animation cooldown
        self.animation_cooldown = 100
        # Set animation list
        self.animation_list = []
        # Set hit animation list
        self.hit_animation_list = []
        # Set dead animation list
        self.dead_animation_list = []
        # Set frame index
        self.frame_index = 0
        # Set update time
        self.update_time = pygame.time.get_ticks()
        # Set explosion cooldown over marker
        self.explosion_coooldown_over = False
        # Create a list for animation
        for level in range(5):
            temp_list = []
            for frame_number in range(3):
                # Load i-th image from the specified directory
                img = pygame.image.load(f'assets/lev{level + 1}_{frame_number}.png').convert_alpha()
                # Transform the image according to the scale
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale),
                                                   int(img.get_height() * self.scale)))
                # Add the image to the list as the next frame
                temp_list.append(img)
            self.animation_list.append(temp_list)
        # Append hit animations
        for level in range(5):
            temp_list = []
            for frame_number in range(3):
                # Load i-th image from the specified directory
                img = pygame.image.load(f'assets/hitlev{level + 1}_{frame_number}.png').convert_alpha()
                # Transform the image according to the scale
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale),
                                                   int(img.get_height() * self.scale)))
                # Add the image to the list as the next frame
                temp_list.append(img)
            self.hit_animation_list.append(temp_list)
        # Append death animations
        for level in range(5):
            temp_list = []
            for frame_number in range(3):
                # Load i-th image from the specified directory
                img = pygame.image.load(f'assets/deadlev{level + 1}_{frame_number}.png').convert_alpha()
                # Transform the image according to the scale
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale),
                                                   int(img.get_height() * self.scale)))
                # Add the image to the list as the next frame
                temp_list.append(img)
            self.dead_animation_list.append(temp_list)
        # Set enemy image
        self.image = self.animation_list[self.level][self.frame_index]
        # Get rectangle
        self.rect = self.image.get_rect()

    # Move the enemy
    def move(self):
        # Check if hits wall
        if self.y - self.speed - (self.image.get_height() / 2) <= 0:
            self.movement = random.choice(["down_left", "down", "down_right"])
        if self.y + self.speed + (self.image.get_height() / 2) > self.settings.screen_height:
            self.movement = random.choice(["up_left", "up", "up_right"])
        if self.x - self.speed - (self.image.get_width() / 2) <= 0:
            self.movement = random.choice(["up_right", "right", "down_right"])
        if self.x + self.speed + (self.image.get_width() / 2) > self.settings.screen_width:
            self.movement = random.choice(["up_left", "left", "down_left"])
        # Movement
        if self.movement == "up_right":
            self.x += self.speed
            self.y -= self.speed
        elif self.movement == "up_left":
            self.x -= self.speed
            self.y -= self.speed
        elif self.movement == "down_right":
            self.x += self.speed
            self.y += self.speed
        elif self.movement == "down_left":
            self.x -= self.speed
            self.y += self.speed
        elif self.movement == "down":
            self.y += self.speed
        elif self.movement == "up":
            self.y += self.speed
        elif self.movement == "right":
            self.x += self.speed
        elif self.movement == "left":
            self.x -= self.speed

    # Update animation
    def update_animation(self):
        # If the animation list for current action has game_run out of frames,
        # reset frame index back to 0
        # TODO: in the future it can be changed to: len(self.animation_list[level]) or in some other way
        if self.frame_index >= len(self.animation_list[self.level]):
            if self.alive and self.hit:
                self.frame_index = 0
                self.hit = False
            if self.alive and not self.hit:
                if self.frame_index >= len(self.hit_animation_list[self.level]):
                    self.frame_index = 0
            if not self.alive:
                self.frame_index = len(self.dead_animation_list[self.level]) - 1
        # Change the animation's index after a short time.
        # Update image depending on current action and frame index
        # TODO: PROVISIONAL DEATH ANIMATION HAS BEEN MADE, A BETTER ONE SHOULD BE MADE
        # Change self image
        if self.alive and not self.hit:
            self.image = self.animation_list[self.level][self.frame_index]
        elif self.alive and self.hit:
            self.image = self.hit_animation_list[self.level][self.frame_index]
        if not self.alive:
            self.image = self.dead_animation_list[self.level][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.animation_cooldown:
            # TODO: PROVISIONAL!
            if not self.alive:
                # Add 1 to frame index to choose the next animation frame
                self.frame_index += 1
                if self.frame_index >= len(self.dead_animation_list[self.level]):
                    self.frame_index = len(self.dead_animation_list)
                    pygame.time.delay(1500)
                    self.explosion_coooldown_over = True
            else:
                # Reset the animation timer
                self.update_time = pygame.time.get_ticks()
                # Add 1 to frame index to choose the next animation frame
                self.frame_index += 1

    # Check if the enemy is dead TODO: PROVISIONAL!
    def die(self):
        self.alive = False
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 200

    # Draw the enemy on the screen
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


# RUN GAME
if __name__ == "__main__":
    game = Game()
    game.run()
