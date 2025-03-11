import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c

# Initialise pygame
pg.init()

# Create clock
clock = pg.time.Clock()

# Create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

# Game variables
game_over = False
game_outcome = 0  # -1 is loss & 1 is win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

# Load images
# Map
map_image = pg.image.load('levels/level.png').convert_alpha()
# Turret spritesheets
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
# Individual turret image for mouse cursor
cursor_turret = pg.image.load('assets/cursor_turret.png').convert_alpha()
# Enemies
enemy_images = {
    "weak": pg.image.load('assets/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('assets/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('assets/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('assets/enemy_4.png').convert_alpha()
}
# Buttons
buy_turret_image = pg.image.load('assets/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/begin.png').convert_alpha()
restart_image = pg.image.load('assets/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/fast_forward.png').convert_alpha()
# GUI
heart_image = pg.image.load("assets/heart.png").convert_alpha()
coin_image = pg.image.load("assets/coin.png").convert_alpha()
logo_image = pg.image.load("assets/logo.png").convert_alpha()

# Load json data for level
with open('levels/level.tmj') as file:
    world_data = json.load(file)

# Load fonts for displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24, bold=True)
large_font = pg.font.SysFont("Consolas", 36)

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def display_data():
    # Draw panel
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
    # Display data
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
    screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    # Calculate the sequential number of the tile
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    # Check if that tile is grass
    if world.tile_map[mouse_tile_num] == 7:
        # Check that there isn't already a turret there
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        # If it is a free space then create turret
        if space_is_free == True:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, None)  
            turret_group.add(new_turret)
            # Deduct cost of turret
            world.money -= c.BUY_COST

def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret

def clear_selection():
    for turret in turret_group:
        turret.selected = False

# Create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

# Create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# Create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

# Game loop
run = True
while run:
    clock.tick(c.FPS)

    
    # UPDATING SECTION
    

    if game_over == False:
        # Check if player has lost
        if world.health <= 0:
            game_over = True
            game_outcome = -1  # Loss
        # Check if player has won
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  # Win

        # Update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        # Highlight selected turret
        if selected_turret:
            selected_turret.selected = True

    
    
    # DRAWING SECTION
    

    # Draw level
    world.draw(screen)

    # Draw groups
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()

    if game_over == False:
        # Check if the level has been started or not
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True
        else:
            # Fast forward option
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            # Spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        # Check if the wave is finished
        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        # Draw buttons
        # Button for placing turrets
        # For the "turret button" show cost of turret and draw the button
        draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
        if turret_button.draw(screen):
            placing_turrets = True
        # If placing turrets then show the cancel button as well
        if placing_turrets == True:
            # Show cursor turret
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= c.SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
                placing_turrets = False
        # If a turret is selected then show the upgrade button
        if selected_turret:
            # If a turret can be upgraded then show the upgrade button
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                # Show cost of upgrade and draw the button
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST
    else:
        pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        # Restart level
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            # Empty groups
            enemy_group.empty()
            turret_group.empty()

    # Event handler
    for event in pg.event.get():
        # Quit program
        if event.type == pg.QUIT:
            run = False
        # Mouse click
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            # Check if mouse is on the game area
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                # Clear selected turrets
                selected_turret = None
                clear_selection()
                if placing_turrets == True:
                    # Check if there is enough money for a turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

    # Update display
    pg.display.flip()

pg.quit()