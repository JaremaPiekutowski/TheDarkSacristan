# CZARNY ZAKRYSTIANIN / THE DARK SACRISTAN
# TODO:
#  - Esthel's pictures
#  - Level difficulty (health, scale, speed) adjustment
#  - Convert to .exe: https://www.youtube.com/watch?v=lTxaran0Cig
#    or https://pythoninoffice.com/freeze-python-code-how-to-run-script-without-python-installed/
#  - Test on other computers

#  - Further improvements incl. tiles (https://pygame.readthedocs.io/en/latest/tiles/tiles.html), fading to black,
#    parts to files, create collectibles, different weapons, more levels, high score table, full screen mode,
#    waves, enemy groups etc. if necessary. In the further levels maybe there could be a bigger probability that
#    the enemies approach the player, instead of just wandering at random, which can be achieved using
#    weighed probabilities (random.choices()).  The links should be created using the os.join() method to provide
#    work under all OS's. Lastly, the code should be cleaned for a better OOP. For deployment purposes,
#    also the comments should be deleted (should they?).

# IMPORT NECESSARY MODULES
import pygame
import os
import random
from settings import Settings

# INITIALIZE PYGAME
pygame.init()
pygame.font.init()
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
        self.game_over_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 40)
        # Set game over label
        self.game_over_label = self.game_over_font.render("GAME OVER", True, (0, 0, 0))
        # Set font for health
        self.health_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 20)
        # Set game over cooldown
        self.game_over_cooldown = 0
        # Set if new level starts
        self.new_level_starts = True
        # Game beginning sound
        self.game_beginning_sound = pygame.mixer.Sound("assets/sound/key_pressed.wav")
        # Texts for lore, level cutscenes and outro
        self.main_lore_texts = [
            '''Nazywasz się Maciej Szymkiewicz. Pracujesz jako zakrystianin w parafii pod wezwaniem Narodzenia NMP w Choszcznie. Nienawidzisz tej pracy. Nazywasz ja kieratem. Dziś jest koniec sierpnia 2022 roku. To twój kolejny dzień w kieracie.''',
            '''Myjąc naczynia liturgiczne i odpierając ostatnie ataki babć, dopraszających się o msze w intencji jakiegoś kolejnego <<Jana Nowak>>, usłyszałeś dobywające się spod ziemi szepty i wrzaski w przedziwnym języku. Jednocześnie na posadzce zakrystii zauważyłeś szczelinę, z której owe jęki się dobywają. To drzwi do innego świata!''',
            '''Z drugiego świata dobywa się rozmowa. To sam wielki przedwieczny Cthulhu rozmawia z biskupem Dzięgą! Wszystko wskazuje na to, ze przekupił biskupa i ten zapewnił Wielkim Przedwiecznym wejście na Ziemię. Trzeba ratować świat! Wziąłeś luk i wskoczyłeś. Po chwili z mroków wyjrzała ohydna morda psa z mackami niczym od Cthulhu!''']
        self.level_lore_texts = [
            '''Ostatkiem sil pokonałeś potwornego psa. Resztki ohydnej głowy z mackami pozostały w poprzednim pomieszczeniu mrocznego lochu, w którym się znalazłeś. Zapomniałeś jednak o wrogu tak szybko, jak to możliwe. Zaczarował cię bowiem kompletnie ten cudowny śpiew, który dobywał się z głębin lochu. Czy to kolejna sztuczka podłego Cthulhu? Nie, to niemożliwe. Był zbyt piękny. Wielcy Przedwieczni nie umieją tworzyć piękna, tylko szaleństwo, zło i zniszczenie. Stwierdziłeś, ze musisz odnaleźć źródło tego śpiewu. Niestety, po chwili usłyszałeś potworny skrzek, a w kolejnym pomieszczeniu pojawiła się oślizgła, zielona kreatura...''',
            '''Glowa potwora spadla i poturlała się pod ceglaną ścianę. Kolejne zwycięstwo! Tymczasem przepiękny śpiew nadal dobiegał z głębin lochu. Czy to syreny, przed którymi trzeba ratować się, przywiązując niczym Odyseusz do masztu? Jedno jest pewne. Trzeba pokonać Wielkich Przedwiecznych. Jeśli tego nie zrobisz, opanują nie tylko Choszczno, ale cały świat... W Choszcznie są Rodzice, Przyjaciele - nie możesz do tego dopuścić!''',
            '''Z tym nie było już tak łatwo. Jesteś bardzo zmęczony walka. Marzysz chwilami o tym, by zasiąść w fotelu z dobrym RIS-em i pogadać z Jaremą i Esthelem o starych Polakach. Ale to nie Choszczno, nie Tychy, tu nie ma Jaremy i Esthela. Trzeba walczyć, i jedyne, co podtrzymuje cię na duchu, to dochodzący z oddali tęskny śpiew. ALE ZARAZ! Cóż to za postać w purpurze na tronie w kolejnym pomieszczeniu? Mimo złowieszczych, czerwonych oczu i wściekłego wyrazu twarzy rozpoznajesz samego Dzhiengę!''',
            '''Dzhienga padł martwy, a jego ciało rozsypało się na kawałki i uleciało w złowieszczym pisku w górę. Sam tez wspiąłeś się na wieżę, z której oglądasz teraz okolice. To miasto cyklopowe R'lyeh, potworne, niszczące samym swym widokiem. Piękny śpiew dobiega zza krat. Jednak nagle drogę zastępuje ci sam WIELKI CTHULHU! <<To teraz, marny człowiecze, zapłacisz mi za swoje grzechy!!!>> Melodia zmienia się...''']
        self.ending_text = '''Świat uratowany, wielki Cthulhu legł! Uwalniasz  porwana przez niego piękną kobietę. Śpiewała, przywołując swojego ratownika! To miłość od pierwszego wejrzenia.    - Jak masz na imię? - pytasz. - Mam na imię Agnieszka... - odpowiada brunetka. A dalsze wydarzenia ukryjmy przed ciekawskim okiem widzów...'''
        self.level_names = ['Straszliwe Szczekanie', 'Zielona Zjawa', 'Żółta Obrzydliwość', 'Opętany Dzhienga',
                            'Wielki Cthulhu']

    # Draw the background
    def draw_background(self, color):
        self.screen.fill(color)
        self.screen.blit(self.health_font.render(f"ENEMY HEALTH: {self.enemy.health}", True, (0, 0, 0)), (2, 2))

    # Draw text
    def draw_text(self, text: str, color: tuple, rect: tuple, font: pygame.font.Font, aa: bool = False, bkg=None):
        """
        Draws some text into an area of a surface. Automatically wraps words. Source: https://www.pygame.org/wiki/TextWrap
        :param text: text to be displayed
        :param color: colour tuple: (r, g, b)
        :param rect: rectangle tuple: (left, top, width, height)
        :param font: Pygame Font object
        :param aa: anti-alias: True or False
        :param bkg: background
        :return: None
        """
        # Define rectangle, top and line spacing
        rect = pygame.Rect(rect)
        y = rect.top
        line_spacing = 2
        # get the height of the font
        font_height = font.size("Tg")[1]
        # Do the loop of blitting text
        while text:
            i = 1
            # Determine if the row of text will be outside our area
            if y + font_height > rect.bottom:
                break
            # Determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
            # If we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1
            # Render the line suitable to the surface
            if bkg:
                text_label = font.render(text[:i], True, color, bkg)
                text_label.set_colorkey(bkg)
            else:
                text_label = font.render(text[:i], aa, color)
            # Blit the text
            self.screen.blit(text_label, (rect.left, y))
            # Move to the next line
            y += font_height + line_spacing
            # remove the text we just blitted
            text = text[i:]

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
            self.check_input()
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
                self.enemy.next_move = pygame.time.get_ticks() + self.enemy.level_move_delay_dict[self.enemy.level]
            # Draw enemy
            if self.enemy.alive:
                self.enemy.draw(self.screen)
            # ...or draw enemy explosion
            elif not self.enemy.alive and not self.enemy.explosion_coooldown_over:
                self.enemy.update_animation()
                self.enemy.draw(self.screen)
            # ...or go to the  next level
            elif not self.enemy.alive and self.enemy.explosion_coooldown_over and self.player.alive:
                self.player.kill()
                for arrow in self.arrow_group:
                    arrow.kill()
                self.new_level_starts = True
                if self.level < 4:
                    self.level += 1
                else:
                    pygame.time.wait(700)
                    self.ending()
                    self.credits()
                    self.post_credits()
            # Move player
            if pygame.time.get_ticks() >= self.player.next_move and self.player.alive:
                self.player.move()
                self.player.next_move = pygame.time.get_ticks() + 3
            # Check collision of player with the enemy
            self.check_collisions()
            # Check for game over
            if not self.player.alive and self.player.death_animation_over:
                self.game_over()
            # Update display
            pygame.display.update()

    # Event listener
    def check_input(self):
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
            self.enemy.hit_sound.play()
            self.enemy.frame_index = 0
            self.enemy.health -= 1
            if self.enemy.health == 0:
                self.enemy.die()

        # Collision of player and enemy
        if pygame.sprite.collide_rect(self.player, self.enemy) and self.player.alive and self.enemy.alive:
            self.player.alive = False
            self.player.death_sound.play()
            self.game_over_cooldown = pygame.time.get_ticks() + 4000

    def main_menu(self):
        # Set font for labels on the title screen
        title_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 50)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 30)
        main_image = pygame.image.load(os.path.join("assets", "title_picture.png"))
        main_image = pygame.transform.scale(main_image, (350, 230))
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        # Loop for the main menu
        main_menu_run = True
        while main_menu_run:
            # Put labels on the screen
            title_label = title_font.render("CZARNY ZAKRYSTIANIN", True, (255, 0, 0))
            instruction_label = pushbutton_font.render("STRZAŁKI - PORUSZANIE, Z - STRZAŁ", True, (255, 255, 255))
            space_label = pushbutton_font.render("SPACJA - START, ESC - WYJŚCIE Z GRY", True, (255, 255, 255))
            self.screen.blit(title_label, (self.settings.screen_width / 2 - title_label.get_width() / 2,
                                           self.settings.screen_height * 0.1))
            self.screen.blit(main_image, (self.settings.screen_width / 2 - main_image.get_width() / 2,
                                          self.settings.screen_height * 0.27))
            self.screen.blit(instruction_label, (self.settings.screen_width / 2 - instruction_label.get_width() / 2,
                                                 self.settings.screen_height * 0.78))
            self.screen.blit(space_label, (self.settings.screen_width / 2 - space_label.get_width() / 2,
                                           self.settings.screen_height * 0.85))

            # Update display
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    main_menu_run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                    # Play sound
                    self.game_beginning_sound.play()
                    # Display lore
                    self.main_lore()
                    pygame.mixer.music.stop()
                    main_menu_run = False

    def main_lore(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sound/main_lore.mp3")
        pygame.mixer.music.play(0)
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 23)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        for part in range(3):
            main_lore_run = True
            while main_lore_run:
                # Background fill
                self.screen.fill((0, 0, 0))
                image = pygame.image.load(f"assets/lore_{part}.jpg")
                image = pygame.transform.scale(image, (300, 280))
                self.screen.blit(image, (self.settings.screen_width / 2 - image.get_width() / 2,
                                         self.settings.screen_height * 0.1))
                self.draw_text(text=self.main_lore_texts[part],
                               color=(255, 255, 255),
                               rect=(90, 360, 720, 150),
                               font=text_font)
                pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
                self.screen.blit(pushbutton_label,
                                 (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                                  self.settings.screen_height * 0.9))
                pygame.time.wait(1000)
                pygame.display.update()
                # Listen for events. Start game if any key is pressed
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.settings.game_run = False
                        main_lore_run = False
                        pygame.quit()
                        break
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.main_menu()
                        else:
                            main_lore_run = False

    def level_cutscene(self, level):
        # Set font for labels on the title screen
        title_font = pygame.font.Font(os.path.join("assets", "Minecraft.ttf"), 30)
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 30)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        level_cutscene_run = True
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        while level_cutscene_run:
            # Background fill
            self.screen.fill((0, 0, 0))
            # Put labels on the screen
            title_label = title_font.render(f"LEVEL {level + 1}", True, (255, 0, 0))
            image = pygame.image.load(f"assets/lore_level_{level+1}.jpg")
            image = pygame.transform.scale(image, (300, 280))
            text = text_font.render(f"{self.level_names[level]}", True, (255, 255, 255))
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.blit(title_label,
                             (self.settings.screen_width / 2 - title_label.get_width() / 2,
                              self.settings.screen_height * 0.1))
            self.screen.blit(image, (self.settings.screen_width / 2 - image.get_width() / 2,
                                     self.settings.screen_height * 0.21))
            self.screen.blit(text, (self.settings.screen_width / 2 - text.get_width() / 2,
                                    self.settings.screen_height * 0.73))
            self.screen.blit(pushbutton_label,
                             (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                              self.settings.screen_height * 0.9))
            pygame.time.wait(1000)
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    level_cutscene_run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                        level_cutscene_run = False
                        pygame.mixer.music.stop()
                        self.level = 0
                        self.main_menu()
                    else:
                        level_cutscene_run = False
        pygame.mixer.music.load(f'assets/sound/music_lev_{level + 1}.mp3')
        pygame.mixer.music.play(0)

    def level_lore(self, level):
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        level_lore_run = True
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        while level_lore_run:
            # Background fill
            self.screen.fill((0, 0, 0))
            self.draw_text(text=self.level_lore_texts[level],
                           color=(255, 255, 255),
                           rect=(100, 100, 700, 700),
                           font=text_font)
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.blit(pushbutton_label,
                             (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                              self.settings.screen_height * 0.9))
            pygame.time.wait(1000)
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    level_lore_run = False
                    pygame.quit()
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                        level_lore_run = False
                        self.main_menu()
                    else:
                        level_lore_run = False

    def new_level_setting(self):
        pygame.mixer.music.stop()
        if self.level > 0:
            self.level_lore(self.level - 1)
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
            pygame.mixer.music.stop()
            self.main_menu()

    # Game ending
    def ending(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sound/ending.mp3")
        pygame.mixer.music.play(0)
        # Set font for labels on the ending screen
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 20)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        game_ending_run = True
        self.screen.fill((10, 20, 10))
        pygame.display.update()
        pygame.time.wait(700)
        while game_ending_run:
            # Background fill
            self.screen.fill((10, 20, 10))
            # Put labels on the screen
            image = pygame.image.load("assets/ending.jpg")
            image = pygame.transform.scale(image, (300, 280))
            self.screen.blit(image, (self.settings.screen_width / 2 - image.get_width() / 2,
                                     self.settings.screen_height * 0.1))
            self.draw_text(text=self.ending_text,
                           color=(255, 255, 255),
                           rect=(90, 360, 720, 150),
                           font=text_font)
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.blit(pushbutton_label,
                             (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                              self.settings.screen_height * 0.9))
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    game_ending_run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                        game_ending_run = False
                        pygame.quit()
                        break
                    else:
                        self.screen.fill((10, 20, 10))
                        pygame.display.update()
                        game_ending_run = False


    def credits(self):
        # Set font for labels on the title screen
        title_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 35)
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        credits_run = True
        self.screen.fill((10, 20, 10))
        pygame.display.update()
        pygame.time.wait(700)
        while credits_run:
            # Background fill
            title = title_font.render("WYGRAŁEŚ!", True, (255, 0, 0))
            credit_title = title_font.render("TWORCY GRY:", True, (0, 255, 0))
            jarema = text_font.render("Jarema Piekutowski", True, (255, 255, 255))
            esthel = text_font.render("Piotr Bednarz", True, (255, 255, 255))
            counselling = text_font.render("Doradztwo: Michał Kapuściński, Krzysztof Hubaczek", True, (255, 255, 255))
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.fill((10, 20, 10))
            self.screen.blit(title, (self.settings.screen_width / 2 - title.get_width() / 2,
                                     self.settings.screen_height * 0.1))
            self.screen.blit(credit_title, (self.settings.screen_width / 2 - credit_title.get_width() / 2,
                                            self.settings.screen_height * 0.2))
            self.screen.blit(jarema, (self.settings.screen_width / 2 - jarema.get_width() / 2,
                                      self.settings.screen_height * 0.3))
            self.screen.blit(esthel, (self.settings.screen_width / 2 - esthel.get_width() / 2,
                                      self.settings.screen_height * 0.4))
            self.screen.blit(counselling, (self.settings.screen_width / 2 - counselling.get_width() / 2,
                                           self.settings.screen_height * 0.5))
            self.screen.blit(pushbutton_label,
                             (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                              self.settings.screen_height * 0.9))
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    credits_run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                        level_lore_run = False
                        pygame.quit()
                        break
                    else:
                        self.screen.fill((10, 20, 10))
                        pygame.display.update()
                        credits_run = False

    def post_credits(self):
        # Set font for labels on the screen
        text_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        pushbutton_font = pygame.font.Font(os.path.join("assets", "LanaPixel.ttf"), 25)
        post_credits_run = True
        self.screen.fill((10, 20, 10))
        pygame.display.update()
        pygame.time.wait(700)
        while post_credits_run:
            # Background fill
            text = '''Wraz z piekna Agnieszka trafiliscie z powrotem do naszego swiata i zamierzaliscie zyc spokojnie. Jednak ktoregos dnia w podziemiach kosciola znowu odezwalo sie szuranie macek...'''
            pushbutton_label = pushbutton_font.render("PRESS ANY KEY", True, (255, 255, 255))
            self.screen.fill((10, 20, 10))
            self.draw_text(text=text,
                           color=(255, 255, 255),
                           rect=(90, 360, 720, 150),
                           font=text_font)
            self.screen.blit(pushbutton_label,
                             (self.settings.screen_width / 2 - pushbutton_label.get_width() / 2,
                              self.settings.screen_height * 0.9))
            pygame.display.update()
            # Listen for events. Start game if any key is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.game_run = False
                    post_credits_run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.game_run = False
                        level_lore_run = False
                        pygame.quit()
                        break
                    else:
                        self.screen.fill((10, 20, 10))
                        pygame.display.update()
                        post_credits_run = False
        pygame.mixer.music.stop()
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
        #  3 - moving left, 4 - moving right, 5 - dead,
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
        # I know it's stupid but I do it only for time purposes
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
        # Set shoot sound effect
        self.shoot_sound = pygame.mixer.Sound('assets/sound/arrow_shoot.wav')
        # Set death sound effect
        self.death_sound = pygame.mixer.Sound('assets/sound/game_die.mp3')
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
            # SHOULDN'T THE ARROW GROUP BE AN ATTRIBUTE OF THE PLAYER?
            arrow_group.add(arrow)
            self.shoot_sound.play()
            # Set shooting to False to prevent shooting more than one arrow
            self.shooting = False

    # Get shooding direction
    def get_shoot_direction(self):
        if self.action == 1:  # if self.moving_up and not self.moving_left and not self.moving_right:
            return 0
        elif self.action == 2:
            return 270
        elif self.action == 3:
            return 180
        elif self.action == 4:
            return 90
        elif self.action == 6:
            return 315
        elif self.action == 7:
            return 225
        elif self.action == 8:
            return 45
        elif self.action == 9:
            return 135
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


# ENEMY CLASS TODO: change difficulty
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
        self.level_scale_dict = {0: 6, 1: 6, 2: 5, 3: 7, 4: 9}
        self.scale = self.level_scale_dict[self.level]
        # Get settings
        self.settings = Settings()
        # Check if alive
        self.alive = True
        # Set move list
        self.move_list = ["up", "up_right", "right", "down_right", "down", "down_left", "left", "up_left"]
        # Set first movement
        self.movement = random.choice(self.move_list)
        # Set speed
        self.level_speed_dict = {0: 1, 1: 2, 2: 3, 3: 3, 4: 3}
        self.speed = self.level_speed_dict[self.level]
        # Set if hit
        self.hit = False
        # Set health based on a level/health dictionary
        self.level_health_dict = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}
        self.health = self.level_health_dict[self.level]
        # Set next move time based on level #TODO: MAKE IT HARDER
        self.level_move_delay_dict = {0: 3, 1: 8, 2: 10, 3: 8, 4: 6}
        self.next_move = pygame.time.get_ticks() + self.level_move_delay_dict[self.level]
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
        # Set hit sound
        self.hit_sound = pygame.mixer.Sound("assets/sound/cthulhu_hit.wav")
        # Set death sound
        self.death_sound = pygame.mixer.Sound("assets/sound/cthulhu_cry.wav")
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
        if self.frame_index >= len(self.animation_list[self.level]):
            if self.alive and self.hit:
                self.frame_index = 0
                self.hit = False
            if self.alive and not self.hit:
                if self.frame_index >= len(self.hit_animation_list[self.level]):
                    self.frame_index = 0
            if not self.alive:
                self.frame_index = len(self.dead_animation_list[self.level]) - 1
        # Update image depending on current action and frame index
        # Change self image
        if self.alive and not self.hit:
            self.image = self.animation_list[self.level][self.frame_index]
        elif self.alive and self.hit:
            self.image = self.hit_animation_list[self.level][self.frame_index]
        if not self.alive:
            self.image = self.dead_animation_list[self.level][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.animation_cooldown:
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

    # Set variables at the enemy's death
    def die(self):
        self.alive = False
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 200
        self.death_sound.play()

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
